import os
from functools import lru_cache
from pathlib import Path


def load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#") or "=" not in entry:
            continue
        key, value = entry.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()


class Settings:
    def __init__(self) -> None:
        self.apify_token = os.getenv("APIFY_TOKEN", "")
        self.apify_actor_id = os.getenv("APIFY_ACTOR_ID", "sama4/greentrace-scrapper")
        self.apify_timeout_secs = int(os.getenv("APIFY_TIMEOUT_SECS", "300"))
        self.qdrant_url = os.getenv("QDRANT_URL", "")
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY", "")
        self.qdrant_collection_name = os.getenv("QDRANT_COLLECTION_NAME", "company_evidence")
        self.embedding_provider = os.getenv("EMBEDDING_PROVIDER", "qdrant-fastembed")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-small-en")
        self.chunk_size_words = int(os.getenv("CHUNK_SIZE_WORDS", "180"))
        self.chunk_overlap_words = int(os.getenv("CHUNK_OVERLAP_WORDS", "40"))


@lru_cache
def get_settings() -> Settings:
    return Settings()