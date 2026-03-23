from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore


class Retriever:
    def __init__(self, settings):
        self.embedder = EmbeddingService(settings.embedding_model)
        self.vector_store = VectorStore(settings.vector_store_path)
        self.top_k = settings.top_k

    def retrieve(self, query_payload: dict) -> list[dict]:
        query_text = query_payload["normalized_query"]
        query_embedding = self.embedder.embed_text(query_text)
        return self.vector_store.search(query_embedding, top_k=self.top_k)