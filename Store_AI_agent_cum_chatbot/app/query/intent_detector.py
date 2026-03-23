from typing import Optional
from app.config.logging_config import logger

class IntentDetector:
    """Detect user intent from queries."""

    INTENT_KEYWORDS = {
        'price_filter': ['under', 'over', 'above', 'below', 'less than', 'more than', 'price', 'cost', 'expensive', 'cheap'],
        'rating_filter': ['rating', 'rate', 'star', 'highly-rated', 'best', 'quality'],
        'stock_check': ['stock', 'inventory', 'available', 'in stock', 'quantity'],
        'search': ['find', 'show', 'list', 'product', 'items', 'give me'],
        'compare': ['compare', 'difference', 'vs', 'versus', 'better'],
        'recommendations': ['recommend', 'suggest', 'best', 'top'],
    }

    @staticmethod
    def detect(query: str) -> str:
        """
        Detect primary intent from query.

        Args:
            query: User query

        Returns:
            Intent type string
        """
        query_lower = query.lower()

        for intent, keywords in IntentDetector.INTENT_KEYWORDS.items():
            if any(kw in query_lower for kw in keywords):
                return intent

        return 'search'  # Default intent
