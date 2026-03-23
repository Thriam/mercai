import numpy as np
from typing import List, Dict, Any
from app.config.logging_config import logger

class ConfidenceScorer:
    """Score confidence in query results."""

    @staticmethod
    def score(retrieved_products: List[Dict[str, Any]], query_result: Dict[str, Any]) -> float:
        """
        Calculate confidence score for results.

        Args:
            retrieved_products: Retrieved product list
            query_result: LLM query result

        Returns:
            Confidence score (0-1)
        """
        if not retrieved_products:
            return 0.0

        # Average relevance of retrieved products
        avg_relevance = np.mean([p.get('relevance_score', 0) for p in retrieved_products])

        # Number of filtered products
        filtered_count = len(query_result.get('filtered_products', []))
        product_count_score = min(1.0, filtered_count / len(retrieved_products)) if retrieved_products else 0.0

        # LLM confidence
        llm_confidence = query_result.get('confidence', 0.5)

        # Weighted average
        confidence = 0.4 * avg_relevance + 0.3 * product_count_score + 0.3 * llm_confidence

        return max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
