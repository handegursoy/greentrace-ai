from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from qdrant_client import QdrantClient, models

from app.core.config import get_settings


class EmbeddingProvider(Protocol):
    model_name: str

    def get_vector_size(self, client: QdrantClient) -> int: ...

    def build_documents(self, texts: list[str]) -> list[models.Document]: ...

    def build_query(self, text: str) -> models.Document: ...


class QdrantFastEmbedProvider:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def get_vector_size(self, client: QdrantClient) -> int:
        return client.get_embedding_size(self.model_name)

    def build_documents(self, texts: list[str]) -> list[models.Document]:
        return [models.Document(text=text, model=self.model_name) for text in texts]

    def build_query(self, text: str) -> models.Document:
        return models.Document(text=text, model=self.model_name)


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()
    if settings.embedding_provider == "qdrant-fastembed":
        return QdrantFastEmbedProvider(model_name=settings.embedding_model_name)
    raise RuntimeError(f"Unsupported embedding provider: {settings.embedding_provider}")
