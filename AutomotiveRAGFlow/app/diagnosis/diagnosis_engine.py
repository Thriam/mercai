from app.llm.llm_client import LLMClient
from app.llm.prompt_templates import build_diagnosis_prompt
from app.diagnosis.confidence_scorer import ConfidenceScorer


class DiagnosisEngine:
    def __init__(self, settings):
        # Original Ollama:
        # self.llm_client = LLMClient(
        #     base_url=settings.ollama_url,
        #     model_name=settings.ollama_model,
        # )
        self.llm_client = LLMClient(
            base_url=settings.openrouter_base_url,
            model_name=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
        )
        self.confidence_scorer = ConfidenceScorer()

    def diagnose(self, query_payload: dict, retrieved_docs: list[dict]) -> dict:
        if not retrieved_docs:
            return {
                "issue": "insufficient_context",
                "possible_causes": [],
                "recommended_checks": [
                    "No relevant knowledge found. Verify ingestion and vector store data."
                ],
                "confidence": 0.0,
                "reasoning_summary": "Retriever returned no evidence.",
            }

        prompt = build_diagnosis_prompt(query_payload, retrieved_docs)
        raw_output = self.llm_client.generate(prompt)

        try:
            diagnosis = self.llm_client.parse_json_response(raw_output)
        except Exception:
            diagnosis = {
                "issue": "llm_parse_fallback",
                "possible_causes": ["Unable to parse model output cleanly"],
                "recommended_checks": ["Inspect raw LLM output and prompt formatting"],
                "confidence": 0.2,
                "reasoning_summary": raw_output[:500],
            }

        diagnosis["confidence"] = self.confidence_scorer.score(retrieved_docs, diagnosis)
        return diagnosis