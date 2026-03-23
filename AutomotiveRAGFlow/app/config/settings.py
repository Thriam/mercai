import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass
class AppSettings:
    app_name: str = os.getenv("APP_NAME", "AutomotiveRAGFlow")
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "mistral:latest")
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL",
        "sentence-transformers/all-MiniLM-L6-v2",
    )

    raw_data_dir: str = os.getenv("RAW_DATA_DIR", str(BASE_DIR / "app" / "data" / "raw"))
    processed_data_dir: str = os.getenv(
        "PROCESSED_DATA_DIR",
        str(BASE_DIR / "app" / "data" / "processed"),
    )
    vector_db_dir: str = os.getenv(
        "VECTOR_DB_DIR",
        str(BASE_DIR / "app" / "data" / "vector_db"),
    )
    vector_store_file: str = os.getenv("VECTOR_STORE_FILE", "vectors.json")

    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    top_k: int = int(os.getenv("TOP_K", "5"))

    @property
    def vector_store_path(self) -> str:
        return str(Path(self.vector_db_dir) / self.vector_store_file)