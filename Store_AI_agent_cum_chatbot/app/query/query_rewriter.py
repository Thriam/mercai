from app.config.logging_config import logger

class QueryRewriter:
    """Rewrite and normalize queries."""

    @staticmethod
    def rewrite(query: str) -> str:
        """
        Rewrite query for better retrieval.

        Args:
            query: Original query

        Returns:
            Rewritten query
        """
        # Simple rewriting rules
        rewritten = query.strip()

        # Expand common abbreviations
        replacements = {
            'w/': 'with',
            'w/o': 'without',
            '$': 'dollars',
        }

        for old, new in replacements.items():
            rewritten = rewritten.replace(old, new)

        logger.info(f"Rewrote query: '{query}' -> '{rewritten}'")
        return rewritten
