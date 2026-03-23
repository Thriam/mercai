from app.core.state import PipelineState
from app.retrieval.vector_store import VectorStore
from app.retrieval.embedding_service import EmbeddingService
from app.config.settings import settings
from app.config.logging_config import logger

class Retriever:
    """Retrieve products based on query similarity."""

    def __init__(self):
        """Initialize retriever with vector store and embeddings."""
        self.vector_store = VectorStore()
        self.embedding_service = EmbeddingService()

    def retrieve(self, state: PipelineState) -> PipelineState:
        """
        Retrieve relevant products for the query.

        Args:
            state: Pipeline state with normalized_query set

        Returns:
            Updated state with retrieved_products
        """
        query = state.normalized_query or state.user_query

        # Embed the query
        query_embedding = self.embedding_service.embed_text(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, top_k=settings.TOP_K)

        # Format results
        state.retrieved_products = [
            {
                'product_id': r['product_id'],
                'metadata': r['metadata'],
                'relevance_score': r['score']
            }
            for r in results
        ]

        logger.info(f"Retrieved {len(state.retrieved_products)} products")
        return state
