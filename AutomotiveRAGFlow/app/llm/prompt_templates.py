import json


def build_diagnosis_prompt(query_payload: dict, retrieved_docs: list[dict]) -> str:
    context_lines = []

    for idx, doc in enumerate(retrieved_docs, start=1):
        context_lines.append(
            f"[{idx}] Source={doc['source']} | Page={doc['page']} | Score={round(doc['score'], 4)}\n{doc['text']}"
        )

    context_block = "\n\n".join(context_lines)

    instruction = {
        "task": "Automotive diagnosis from retrieved evidence only",
        "rules": [
            "Use only the retrieved evidence.",
            "Do not invent unsupported facts.",
            "Be concise and practical.",
            "Return valid JSON only.",
        ],
        "required_output_schema": {
            "issue": "string",
            "possible_causes": ["string"],
            "recommended_checks": ["string"],
            "confidence": "float between 0 and 1",
            "reasoning_summary": "string",
        },
    }

    return f"""
SYSTEM INSTRUCTION:
{json.dumps(instruction, indent=2)}

USER QUERY:
{json.dumps(query_payload, indent=2)}

RETRIEVED CONTEXT:
{context_block}

Return only JSON.
""".strip()