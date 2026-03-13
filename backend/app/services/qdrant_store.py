from __future__ import annotations

from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    HnswConfigDiff,
    MatchAny,
    MatchValue,
    PayloadSchemaType,
    VectorParams,
)

from app.core.config import get_settings
from app.schemas.evidence import EvidenceChunk
from app.services.embedding_provider import get_embedding_provider


class QdrantEvidenceStore:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.qdrant_url:
            raise RuntimeError("QDRANT_URL is not configured")
        self.collection_name = settings.qdrant_collection_name
        self.client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
        self.embedder = get_embedding_provider()
        self.vector_size = self.embedder.get_vector_size(self.client)

    def ensure_collection(self) -> str:
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=self.vector_size, distance=Distance.COSINE),
                hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
                on_disk_payload=True,
            )
        for field in ("company", "source", "domain", "article_id"):
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
                wait=True,
            )
        return self.collection_name

    def upsert_chunks(self, chunks: list[EvidenceChunk]) -> int:
        self.ensure_collection()
        payload = [
            {
                "company": chunk.company,
                "article_id": chunk.article_id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "title": chunk.title,
                "url": chunk.url,
                "domain": chunk.domain,
                "source": chunk.source,
                "query": chunk.query,
                "matched_keywords": chunk.matched_keywords,
                "keyword_relevance": chunk.keyword_relevance,
            }
            for chunk in chunks
        ]
        ids = [chunk.point_id for chunk in chunks]
        documents = self.embedder.build_documents([chunk.text for chunk in chunks])
        for index in range(0, len(chunks), 64):
            self.client.upload_collection(
                collection_name=self.collection_name,
                vectors=documents[index : index + 64],
                payload=payload[index : index + 64],
                ids=ids[index : index + 64],
            )
        return len(chunks)

    def search(self, company: str, question: str, limit: int, sources: list[str] | None = None):
        must = [FieldCondition(key="company", match=MatchValue(value=company))]
        if sources:
            must.append(FieldCondition(key="source", match=MatchAny(any=sources)))
        return self.client.query_points(
            collection_name=self.collection_name,
            query=self.embedder.build_query(question),
            query_filter=Filter(must=must),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        ).points


@lru_cache
def get_qdrant_store() -> QdrantEvidenceStore:
    return QdrantEvidenceStore()
