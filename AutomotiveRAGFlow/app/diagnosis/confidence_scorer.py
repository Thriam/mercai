class ConfidenceScorer:
    def score(self, retrieved_docs: list[dict], diagnosis_result: dict) -> float:
        if not retrieved_docs:
            return 0.0

        avg_similarity = sum(doc["score"] for doc in retrieved_docs) / len(retrieved_docs)
        causes_count = len(diagnosis_result.get("possible_causes", []))

        confidence = avg_similarity

        if causes_count > 0:
            confidence = min(1.0, confidence + 0.05)

        return round(confidence, 2)