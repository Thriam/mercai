from app.query.query_rewriter import QueryRewriter
from app.query.intent_detector import IntentDetector


class QueryHandler:
    def __init__(self):
        self.rewriter = QueryRewriter()
        self.intent_detector = IntentDetector()

    def process(self, user_query: str) -> dict:
        normalized_query = self.rewriter.rewrite(user_query)
        intent_data = self.intent_detector.detect(normalized_query)

        return {
            "original_query": user_query,
            "normalized_query": normalized_query,
            "intent": intent_data["intent"],
            "entities": intent_data["entities"],
        }