import re


class TextCleaner:
    def clean_text(self, text: str) -> str:
        if not text:
            return ""

        text = text.replace("\u00a0", " ")
        text = text.replace("\n", " ")
        text = text.replace("\t", " ")

        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"\s+([,.;:!?])", r"\1", text)

        return text.strip()

    def clean_document(self, extracted_doc: dict) -> dict:
        cleaned_pages = []

        for page in extracted_doc.get("pages", []):
            cleaned_pages.append(
                {
                    "page_number": page["page_number"],
                    "clean_text": self.clean_text(page.get("text", "")),
                }
            )

        return {
            "source": extracted_doc["source"],
            "pages": cleaned_pages,
        }