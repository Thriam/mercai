class TextChunker:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _split_text(self, text: str) -> list[str]:
        if not text:
            return []

        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end >= text_length:
                break

            start = end - self.chunk_overlap

        return chunks

    def chunk_document(self, cleaned_doc: dict) -> list[dict]:
        output_chunks = []
        source_name = cleaned_doc["source"].replace(".pdf", "")

        for page in cleaned_doc.get("pages", []):
            page_number = page["page_number"]
            clean_text = page.get("clean_text", "")

            page_chunks = self._split_text(clean_text)

            for idx, chunk_text in enumerate(page_chunks, start=1):
                output_chunks.append(
                    {
                        "chunk_id": f"{source_name}_p{page_number}_c{idx}",
                        "source": cleaned_doc["source"],
                        "page": page_number,
                        "text": chunk_text,
                        "metadata": {
                            "document_type": "manual",
                        },
                    }
                )

        return output_chunks