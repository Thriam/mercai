import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any
from app.config.settings import settings
from app.config.logging_config import logger

class VectorStore:
    """Manages vector embeddings and similarity search."""

    def __init__(self):
        """Initialize vector store."""
        self.vectors = {}
        self.metadata = {}
        self.embeddings = {}
        self.load()

    def load(self):
        """Load vectors from disk if they exist."""
        if settings.VECTOR_STORE_PATH.exists():
            try:
                with open(settings.VECTOR_STORE_PATH, 'r') as f:
                    data = json.load(f)
                    self.vectors = {k: np.array(v) for k, v in data.get('vectors', {}).items()}
                    self.metadata = data.get('metadata', {})
                logger.info(f"Loaded {len(self.vectors)} vectors from store")
            except Exception as e:
                logger.warning(f"Could not load vector store: {e}")

    def save(self):
        """Save vectors to disk."""
        data = {
            'vectors': {k: v.tolist() for k, v in self.vectors.items()},
            'metadata': self.metadata
        }
        with open(settings.VECTOR_STORE_PATH, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved {len(self.vectors)} vectors to store")

    def add(self, product_id: str, embedding: np.ndarray, metadata: Dict[str, Any]):
        """Add a product vector with metadata."""
        self.vectors[product_id] = embedding
        self.metadata[product_id] = metadata

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for top-k products by embedding similarity.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of (product_id, metadata, score) tuples
        """
        if not self.vectors:
            return []

        results = []
        for product_id, embedding in self.vectors.items():
            # Cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding) + 1e-8
            )
            results.append({
                'product_id': product_id,
                'metadata': self.metadata.get(product_id, {}),
                'score': float(similarity)
            })

        # Sort by score and return top-k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
