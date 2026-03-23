import json
import math
from pathlib import Path

from app.utils.exceptions import VectorStoreEmptyError


class VectorStore:
    def __init__(self, store_path: str):
        self.store_path = Path(store_path)
        self.store_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.store_path.exists():
            self._save([])

    def _load(self) -> list[dict]:
        with self.store_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save(self, data: list[dict]) -> None:
        with self.store_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def add_documents(self, documents: list[dict]) -> None:
        existing_docs = self._load()

        existing_ids = {doc["doc_id"] for doc in existing_docs}
        new_docs = [doc for doc in documents if doc["doc_id"] not in existing_ids]

        if new_docs:
            existing_docs.extend(new_docs)
            self._save(existing_docs)

    def clear(self) -> None:
        self._save([])

    def count(self) -> int:
        return len(self._load())

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        docs = self._load()

        if not docs:
            raise VectorStoreEmptyError("Vector store is empty. Run ingest.py first.")

        scored_results = []
        for doc in docs:
            score = self._cosine_similarity(query_embedding, doc["embedding"])

            scored_results.append(
                {
                    "doc_id": doc["doc_id"],
                    "source": doc["metadata"]["source"],
                    "page": doc["metadata"]["page"],
                    "text": doc["metadata"]["text"],
                    "score": score,
                }
            )

        scored_results.sort(key=lambda item: item["score"], reverse=True)
        return scored_results[:top_k]

    @staticmethod
    def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot_product / (norm_a * norm_b)