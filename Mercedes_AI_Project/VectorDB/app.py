import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter


# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
CHROMA_DIR = BASE_DIR / "chroma_db"

LLM_MODEL = "mistral"
EMBED_MODEL = "nomic-embed-text"
COLLECTION_NAME = "vehicle_knowledge"

llm = Ollama(model=LLM_MODEL)
embedding_model = OllamaEmbeddings(model=EMBED_MODEL)

app = FastAPI(title="Vehicle RAG Assistant", version="1.0")


# =========================================================
# REQUEST / RESPONSE MODELS
# =========================================================

class DiagnoseRequest(BaseModel):
    user_input: str = Field(..., min_length=3)


class RefineRequest(BaseModel):
    original_input: str = Field(..., min_length=3)
    selected_path: str = Field(..., min_length=2)
    prior_extraction: Dict[str, Any]
    prior_diagnosis: Dict[str, Any]


# =========================================================
# HELPERS
# =========================================================

def safe_json_load(text: str) -> Dict[str, Any]:
    """
    Parse model output safely even if fenced in markdown.
    """
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError as ex:
        raise ValueError(f"Invalid JSON from model: {text}") from ex


def read_knowledge_documents() -> List[Dict[str, Any]]:
    documents: List[Dict[str, Any]] = []

    if not KNOWLEDGE_DIR.exists():
        raise FileNotFoundError(f"Knowledge directory not found: {KNOWLEDGE_DIR}")

    for path in KNOWLEDGE_DIR.glob("*.txt"):
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        category = path.stem.lower()
        documents.append({
            "source": path.name,
            "category": category,
            "content": content
        })

    if not documents:
        raise FileNotFoundError("No knowledge documents found in knowledge_base")

    return documents


def build_vector_store() -> Chroma:
    """
    Create or load Chroma DB from local text files.
    """
    docs = read_knowledge_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    texts: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for doc in docs:
        chunks = splitter.split_text(doc["content"])
        for idx, chunk in enumerate(chunks):
            texts.append(chunk)
            metadatas.append({
                "source": doc["source"],
                "category": doc["category"],
                "chunk_index": idx
            })

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=str(CHROMA_DIR)
    )

    # Rebuild collection cleanly each run for training/demo stability.
    try:
        existing = vector_store.get()
        existing_ids = existing.get("ids", [])
        if existing_ids:
            vector_store.delete(ids=existing_ids)
    except Exception:
        pass

    vector_store.add_texts(texts=texts, metadatas=metadatas)
    vector_store.persist()

    return vector_store


vector_db = build_vector_store()


# =========================================================
# STAGE 1 + STAGE 2 : EXTRACTION
# =========================================================

def extract_issue(user_input: str) -> Dict[str, Any]:
    prompt = f"""
You are a vehicle issue extractor.

Return ONLY valid JSON.

Schema:
{{
  "problemCategory": "engine | battery | fuel | electrical | cooling | transmission | brakes | unknown",
  "problemSubCategory": "string",
  "vehicleState": "running | not_starting | stalled | intermittent | unknown",
  "severity": "low | medium | high | critical",
  "signals": {{
    "powerLoss": boolean,
    "notStarting": boolean,
    "overheating": boolean,
    "warningLights": boolean,
    "strangeNoise": boolean,
    "weakCrank": boolean,
    "smoke": boolean
  }},
  "context": {{
    "eventType": "while_driving | ignition | parked | unknown",
    "pattern": "sudden | gradual | intermittent | unknown"
  }}
}}

Rules:
- Infer from user language if reasonably clear.
- If not mentioned, default booleans to false.
- Keep strings short.
- No explanation outside JSON.

User Input:
{user_input}
"""
    result = llm.invoke(prompt)
    return safe_json_load(result)


# =========================================================
# STAGE 3 : QUERY BUILDER
# =========================================================

def build_query(extracted: Dict[str, Any]) -> str:
    problem_category = extracted.get("problemCategory", "unknown")
    vehicle_state = extracted.get("vehicleState", "unknown")
    severity = extracted.get("severity", "unknown")
    signals = extracted.get("signals", {})
    active_signals = [key for key, value in signals.items() if value]

    query_parts = [problem_category, vehicle_state, severity] + active_signals
    return " ".join(part for part in query_parts if part and part != "unknown")


# =========================================================
# STAGE 3 : RETRIEVAL
# =========================================================

def retrieve_context(query: str, category: str, k: int = 3) -> List[Dict[str, Any]]:
    # broad semantic retrieval
    docs = vector_db.similarity_search(query, k=6)

    # category-aware prioritization
    ranked: List[Dict[str, Any]] = []
    for d in docs:
        meta = d.metadata or {}
        score_boost = 1 if meta.get("category") == category else 0
        ranked.append({
            "content": d.page_content,
            "source": meta.get("source", "unknown"),
            "category": meta.get("category", "unknown"),
            "score_boost": score_boost
        })

    ranked.sort(key=lambda x: x["score_boost"], reverse=True)
    return ranked[:k]


# =========================================================
# STAGE 3 : LLM DIAGNOSIS
# =========================================================

def generate_diagnosis(
    user_input: str,
    extracted: Dict[str, Any],
    retrieved_context: List[Dict[str, Any]]
) -> Dict[str, Any]:
    context_text = "\n\n".join(
        [f"[{item['category']} | {item['source']}] {item['content']}" for item in retrieved_context]
    )

    prompt = f"""
You are an automotive diagnosis assistant.

Use the retrieved context and structured extraction.
Return ONLY valid JSON in this schema:

{{
  "caseId": "string",
  "problem": "string",
  "severity": "low | medium | high | critical",
  "vehicleState": "running | not_starting | stalled | intermittent | unknown",
  "diagnosis": [
    {{
      "title": "string",
      "confidence": 0.0,
      "actions": ["string", "string", "string"]
    }}
  ],
  "advice": "string",
  "towRequired": true,
  "driveAllowed": false,
  "nextButtons": ["string", "string", "string"]
}}

Rules:
- max 3 diagnosis items
- max 3 actions per item
- confidence must be between 0 and 1
- ground your answer in the context
- no extra explanation outside JSON

User Input:
{user_input}

Extracted JSON:
{json.dumps(extracted, indent=2)}

Retrieved Context:
{context_text}
"""
    result = llm.invoke(prompt)
    diagnosis = safe_json_load(result)

    # sanitize nextButtons if model misses them
    if "nextButtons" not in diagnosis or not isinstance(diagnosis["nextButtons"], list):
        diagnosis["nextButtons"] = suggest_buttons(diagnosis)

    return diagnosis


def suggest_buttons(diagnosis: Dict[str, Any]) -> List[str]:
    buttons: List[str] = []

    for item in diagnosis.get("diagnosis", []):
        title = item.get("title", "").lower()

        if "battery" in title or "electrical" in title:
            buttons.append("Check Battery")
        if "fuel" in title:
            buttons.append("Check Fuel")
        if "engine" in title or "ignition" in title or "ecu" in title or "sensor" in title:
            buttons.append("Check Engine Electronics")
        if "cool" in title or "overheat" in title:
            buttons.append("Check Cooling")

    buttons.append("Safety Advice")

    unique: List[str] = []
    seen = set()
    for b in buttons:
        if b not in seen:
            seen.add(b)
            unique.append(b)

    return unique[:4]


# =========================================================
# STAGE 3 : REFINEMENT LOOP
# =========================================================

def build_refinement_questions(selected_path: str) -> List[str]:
    followup_map = {
        "Check Battery": [
            "Are headlights dim?",
            "Do you hear clicking when starting?",
            "Does the engine crank slowly?"
        ],
        "Check Fuel": [
            "Is there enough fuel in the tank?",
            "Did the engine sputter before stopping?",
            "Do you smell fuel?"
        ],
        "Check Engine Electronics": [
            "Is the check-engine light on?",
            "Did the issue happen suddenly?",
            "Any unusual dashboard warnings?"
        ],
        "Check Cooling": [
            "Did you see a temperature warning?",
            "Was there steam or coolant smell?",
            "Did overheating happen before shutdown?"
        ],
        "Safety Advice": [
            "Is the vehicle in a safe place?",
            "Are hazard lights on?",
            "Do you need towing guidance?"
        ]
    }

    return followup_map.get(selected_path, ["Please describe what you observe now."])


def refine_diagnosis(
    original_input: str,
    selected_path: str,
    prior_extraction: Dict[str, Any],
    prior_diagnosis: Dict[str, Any]
) -> Dict[str, Any]:
    refinement_prompt = f"""
You are refining an automotive diagnosis path.

Return ONLY valid JSON in this schema:

{{
  "selectedPath": "string",
  "followupQuestions": ["string", "string", "string"],
  "refinedAdvice": "string"
}}

Original Input:
{original_input}

Selected Path:
{selected_path}

Prior Extraction:
{json.dumps(prior_extraction, indent=2)}

Prior Diagnosis:
{json.dumps(prior_diagnosis, indent=2)}
"""
    try:
        result = llm.invoke(refinement_prompt)
        refined = safe_json_load(result)
        if "followupQuestions" not in refined:
            refined["followupQuestions"] = build_refinement_questions(selected_path)
        return refined
    except Exception:
        return {
            "selectedPath": selected_path,
            "followupQuestions": build_refinement_questions(selected_path),
            "refinedAdvice": f"Proceed with the {selected_path} path and collect more evidence."
        }


# =========================================================
# FULL PIPELINE
# =========================================================

def run_pipeline(user_input: str) -> Dict[str, Any]:
    extracted = extract_issue(user_input)
    query = build_query(extracted)
    retrieved = retrieve_context(
        query=query,
        category=extracted.get("problemCategory", "unknown"),
        k=3
    )
    diagnosis = generate_diagnosis(user_input, extracted, retrieved)

    return {
        "stage1_userInput": user_input,
        "stage2_extractionJson": extracted,
        "stage3_query": query,
        "stage3_retrievedContext": retrieved,
        "final_output": diagnosis
    }


# =========================================================
# API ENDPOINTS
# =========================================================

@app.get("/")
def home() -> Dict[str, str]:
    return {"message": "Vehicle RAG Assistant is running."}


@app.post("/diagnose")
def diagnose(request: DiagnoseRequest) -> Dict[str, Any]:
    try:
        return run_pipeline(request.user_input)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.post("/refine")
def refine(request: RefineRequest) -> Dict[str, Any]:
    try:
        return refine_diagnosis(
            original_input=request.original_input,
            selected_path=request.selected_path,
            prior_extraction=request.prior_extraction,
            prior_diagnosis=request.prior_diagnosis
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
