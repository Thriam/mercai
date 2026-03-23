class ClarificationEngine:
    def evaluate(self, diagnosis_result: dict) -> dict:
        confidence = diagnosis_result.get("confidence", 0.0)

        if confidence < 0.60:
            return {
                "needs_clarification": True,
                "clarification_question": (
                    "Does the problem happen while idling, in traffic, or only while driving? "
                    "Also, do you see warning lights, leaks, smoke, or unusual fan behavior?"
                ),
            }

        return {
            "needs_clarification": False,
            "clarification_question": "",
        }