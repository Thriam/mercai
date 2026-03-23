# AutomotiveRAGFlow AI Agent Knowledge Base

## Overview
It processes user-described vehicle issues (e.g., \"brakes making noise\") by retrieving relevant chunks from technical manuals (PDFs on brakes, cooling, starting systems), feeding them to an LLM for diagnosis, scoring confidence, checking for clarification needs, and generating actionable responses with possible causes and checks.

- **Core Paradigm**: Evidence-grounded diagnosis to avoid hallucinations.
- **LLM Backend**: OpenRouter GPT-4o (migrated from local Ollama Mistral).
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 for local retrieval.
- **Vector Store**: Simple JSON file (`vectors.json`) with embeddings, metadata (source/page/text/score).
- **Status**: Pending user .env setup for OpenRouter API key and ingestion run (`python ingest.py && python main.py`).

## Architecture & Pipeline Flow
The AI agent is orchestrated via `AutomotiveRAGOrchestrator` which delegates to `AutomotiveRAGPipeline`. Execution tracked in `PipelineState` dataclass.

```
User Query (main.py interactive loop)
    ↓
1. QueryHandler.process() → normalized_query payload (intent detection/rewriting)
    ↓
2. Retriever.retrieve() → top-K docs via embedding similarity
    - EmbeddingService.embed_text(query)
    - VectorStore.search(embedding, top_k=5)
    ↓
3. DiagnosisEngine.diagnose()
    - build_diagnosis_prompt(payload, docs) → structured JSON prompt
    - LLMClient.generate(prompt) → raw text → parse_json_response()
    - ConfidenceScorer.score(docs, diagnosis) → 0-1 float (avg sim, doc count, etc.)
    ↓ Diagnosis JSON: {issue, possible_causes[], recommended_checks[], confidence, reasoning_summary}
    ↓
4. ClarificationEngine.evaluate() → needs_clarification?, clarification_question
    ↓
5. ResponseBuilder.build() → formatted final response
    ↓ Output: response, needs_clarification, diagnosis_result, retrieved_docs
```

## Key Components

### 1. Orchestrator & Pipeline
- **`app/core/orchestrator.py`**: Thin wrapper: `pipeline.run(user_query)`.
- **`app/core/pipeline.py`**: Coordinates all steps, initializes handlers/engines.

### 2. Retrieval
- **`app/retrieval/retriever.py`**: Embeds query, searches vector store.
- Supports `ingest.py` for building the store from PDFs.

### 3. LLM Integration
- **`app/llm/llm_client.py`**: OpenRouter `/chat/completions` compatible (with custom headers for blackbox.ai referer).
  - `generate(prompt)`: Returns LLM content.
  - `parse_json_response(raw)`: Strips markdown, JSON.loads.
- **`app/llm/prompt_templates.py`**: `build_diagnosis_prompt()` enforces JSON schema with rules (evidence-only, concise).

### 4. Diagnosis & Scoring
- **`app/diagnosis/diagnosis_engine.py`**: LLM call + parsing + confidence.
- **`app/diagnosis/confidence_scorer.py`**: Heuristic score based on retrieval quality, output structure.
- **`app/diagnosis/response_builder.py`**: Formats diagnosis into user-friendly text.

### 5. Loop & Polish
- **`app/loop/clarification_engine.py`**: Evaluates if more info needed (low confidence → ask question).
- **`app/query/query_handler.py`**, **`app/query/query_rewriter.py`**, **`app/query/intent_detector.py`**: Query preprocessing.

### 6. Data Pipeline
- **Extraction**: `app/extraction/pdf_extractor.py`, `text_cleaner.py`, `chunker.py` (size=500, overlap=50).
- **Storage**: `app/data/processed/*.json` (chunks), `app/data/vector_db/vectors.json`.
- **Raw Data**: PDFs in `app/data/raw/` (brake_system_noise.pdf, cooling_system_manual.pdf, starting_system_manual.pdf).

## Configuration (app/config/settings.py)
- Loaded from `.env`.
- Key vars: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL=https://openrouter.ai/api/v1`, `OPENROUTER_MODEL=gpt-4o`, `EMBEDDING_MODEL`, dirs for data/chunks/vectors, `TOP_K=5`, `CHUNK_SIZE=500`.

## Dependencies (requirements.txt)
```
python-dotenv
pypdf
sentence-transformers
numpy
requests
```

## Running the Agent
1. Set `.env` per TODO.md:
   ```
   OPENROUTER_API_KEY=your_key
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_MODEL=gpt-4o
   ```
2. `python ingest.py` (build vectors from PDFs).
3. `python main.py` → Interactive: Enter issue → Get diagnosis/confidence/response.

## Migration Notes (from TODO.md)
- Switched LLM from Ollama local to OpenRouter cloud.
- Code updated in settings.py, llm_client.py, diagnosis_engine.py.
- Pending: User .env + test.

## Strengths & Behaviors
- **Grounded**: Strictly uses retrieved evidence.
- **Confidence-Aware**: Scores outputs, triggers clarification loop.
- **JSON-Structured**: Reliable parsing.
- **Extensible**: Modular pipeline for adding query rewrite, feedback handling.

## Sample Output Structure
```
--- FINAL RESPONSE ---
Issue: Brake pad wear
Possible Causes: ['Worn brake pads', 'Glazed rotors']
Recommended Checks: ['Inspect pad thickness (>3mm)', 'Measure rotor thickness']
Confidence: 0.85

--- RAW JSON ---
{
  \"issue\": \"brake pad wear\",
  \"possible_causes\": [\"Worn brake pads\"],
  ...
}
```

This encapsulates **all gathered knowledge** from project files, search results, and structure. The AI agent excels in evidence-based automotive troubleshooting.
