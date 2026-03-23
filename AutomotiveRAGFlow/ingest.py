import json
import logging
from pathlib import Path

from app.config.logging_config import setup_logging
from app.config.settings import AppSettings
from app.extraction.pdf_extractor import PDFExtractor
from app.extraction.text_cleaner import TextCleaner
from app.extraction.chunker import TextChunker
from app.retrieval.embedding_service import EmbeddingService
from app.retrieval.vector_store import VectorStore

logger = logging.getLogger(__name__)


def main() -> None:
    setup_logging()
    settings = AppSettings()

    raw_dir = Path(settings.raw_data_dir)
    pdf_files = list(raw_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {raw_dir}")
        return

    extractor = PDFExtractor()
    cleaner = TextCleaner()
    chunker = TextChunker(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    embedder = EmbeddingService(settings.embedding_model)
    vector_store = VectorStore(settings.vector_store_path)

    all_documents = []

    for pdf_path in pdf_files:
        logger.info("Processing PDF: %s", pdf_path.name)

        extracted = extractor.extract(str(pdf_path))
        cleaned = cleaner.clean_document(extracted)
        chunks = chunker.chunk_document(cleaned)

        for chunk in chunks:
            embedding = embedder.embed_text(chunk["text"])
            all_documents.append(
                {
                    "doc_id": chunk["chunk_id"],
                    "embedding": embedding,
                    "metadata": {
                        "source": chunk["source"],
                        "page": chunk["page"],
                        "text": chunk["text"],
                        "document_type": chunk["metadata"].get("document_type", "manual"),
                    },
                }
            )

        processed_output = Path(settings.processed_data_dir) / f"{pdf_path.stem}_chunks.json"
        processed_output.parent.mkdir(parents=True, exist_ok=True)
        with processed_output.open("w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

    vector_store.add_documents(all_documents)
    print(f"Ingestion complete. Stored {len(all_documents)} vectors.")


if __name__ == "__main__":
    main()