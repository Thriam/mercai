class FeedbackHandler:
    def merge_feedback(self, original_query: str, follow_up_answer: str) -> str:
        return f"{original_query}. Additional info: {follow_up_answer}"