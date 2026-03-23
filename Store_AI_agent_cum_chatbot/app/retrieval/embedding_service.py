from sentence_transformers import SentenceTransformer
from app.config.settings import settings
from app.config.logging_config import logger

class EmbeddingService:
    """Service for generating text embeddings."""

    def __init__(self):
        """Initialize embedding model."""
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)

    def embed_text(self, text: str):
        """
        Generate embedding for text.

        Args:
            text: Text to embed

        Returns:
            Numpy array of embeddings
        """
        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts: list):
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            Numpy array of embeddings
        """
        return self.model.encode(texts, convert_to_numpy=True)
