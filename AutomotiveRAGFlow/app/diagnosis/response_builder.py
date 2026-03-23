class ResponseBuilder:
    def build(
        self,
        diagnosis_result: dict,
        needs_clarification: bool = False,
        clarification_question: str = "",
    ) -> str:
        issue = diagnosis_result.get("issue", "unknown issue")
        causes = diagnosis_result.get("possible_causes", [])
        checks = diagnosis_result.get("recommended_checks", [])
        reasoning = diagnosis_result.get("reasoning_summary", "")
        confidence = diagnosis_result.get("confidence", 0.0)

        parts = [
            f"Issue: {issue}",
            f"Confidence: {confidence}",
        ]

        if causes:
            parts.append("Possible causes: " + "; ".join(causes))

        if checks:
            parts.append("Recommended checks: " + "; ".join(checks))

        if reasoning:
            parts.append("Reasoning: " + reasoning)

        if needs_clarification and clarification_question:
            parts.append("Clarification needed: " + clarification_question)

        return "\n\n".join(parts)