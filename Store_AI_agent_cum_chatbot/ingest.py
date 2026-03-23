"""
Data ingestion script for Store AI Agent.

Loads product CSV and generates embeddings for vector store.
"""

import json
from pathlib import Path
from app.config.settings import settings
from app.config.logging_config import logger
from app.retrieval.csv_loader import CSVLoader
from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore

def ingest():
    """Load CSV and build vector store."""
    logger.info("Starting data ingestion...")

    # Load products from CSV
    products = CSVLoader.load(settings.CSV_FILE_PATH)

    if not products:
        logger.error("No products loaded from CSV")
        return

    # Initialize services
    embedding_service = EmbeddingService()
    vector_store = VectorStore()

    # Build product descriptions for embedding
    product_descriptions = []
    for p in products:
        description = f"Product {p['id']}: ${p['price']} "
        if 'name' in p:
            description += f"({p['name']}) "
        description += f"rating {p['rating']}/5, {p['quantity']} in stock"
        product_descriptions.append(description)

    logger.info(f"Generating embeddings for {len(products)} products...")

    # Generate embeddings
    embeddings = embedding_service.embed_texts(product_descriptions)

    # Add to vector store
    for product, embedding, description in zip(products, embeddings, product_descriptions):
        metadata = {
            'id': product['id'],
            'price': product['price'],
            'quantity': product['quantity'],
            'rating': product['rating'],
            'description': description,
            **{k: v for k, v in product.items() if k not in ['id', 'price', 'quantity', 'rating']}
        }
        vector_store.add(product['id'], embedding, metadata)

    # Save vector store
    vector_store.save()

    # Save processed chunks
    processed_data = {
        'products': products,
        'descriptions': product_descriptions,
        'count': len(products)
    }
    with open(settings.PRODUCTS_CHUNKS_PATH, 'w') as f:
        json.dump(processed_data, f, indent=2)

    logger.info(f"Ingestion complete. {len(products)} products processed.")

if __name__ == "__main__":
    ingest()
