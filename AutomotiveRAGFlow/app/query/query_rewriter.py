class QueryRewriter:
    def rewrite(self, user_query: str) -> str:
        return user_query.lower().strip()