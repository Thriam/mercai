import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application configuration from environment variables."""

    # OpenRouter API
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "gpt-4o")

    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

    # Data Directories
    BASE_DIR = Path(__file__).parent.parent.parent
    DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "app" / "data")))
    PROCESSED_DIR = Path(os.getenv("PROCESSED_DIR", str(DATA_DIR / "processed")))
    VECTOR_DB_DIR = Path(os.getenv("VECTOR_DB_DIR", str(DATA_DIR / "vector_db")))

    # CSV Configuration
    CSV_FILE_PATH = Path(os.getenv("CSV_FILE_PATH", str(DATA_DIR / "raw" / "products.csv")))

    # Retrieval Configuration
    TOP_K = int(os.getenv("TOP_K", "5"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))

    # Vector Store Path
    VECTOR_STORE_PATH = VECTOR_DB_DIR / "vectors.json"
    PRODUCTS_CHUNKS_PATH = PROCESSED_DIR / "products_chunks.json"

    def __init__(self):
        """Validate and create necessary directories."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        self.VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

        if not self.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set in .env")

# Singleton instance
settings = Settings()
