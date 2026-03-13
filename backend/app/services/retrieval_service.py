from __future__ import annotations

from app.schemas.retrieval import EvidenceHit, RetrievalRequest, RetrievalResponse
from app.services.qdrant_store import get_qdrant_store


class RetrievalService:
    def __init__(self) -> None:
        self.store = get_qdrant_store()

    def retrieve(self, request: RetrievalRequest) -> RetrievalResponse:
        points = self.store.search(
            company=request.company,
            question=request.question,
            limit=request.top_k,
            sources=request.sources,
        )
        evidence = [
            EvidenceHit(
                point_id=str(point.id),
                article_id=str(point.payload.get("article_id") or ""),
                score=float(point.score or 0.0),
                text=str(point.payload.get("text") or ""),
                title=point.payload.get("title"),
                url=str(point.payload.get("url") or ""),
                domain=str(point.payload.get("domain") or ""),
                source=str(point.payload.get("source") or "unknown"),
                matched_keywords=[str(value) for value in point.payload.get("matched_keywords") or []],
                keyword_relevance=_as_float(point.payload.get("keyword_relevance")),
            )
            for point in points
        ]
        return RetrievalResponse(
            company=request.company,
            question=request.question,
            collection_name=self.store.collection_name,
            total_hits=len(evidence),
            evidence=evidence,
        )


def _as_float(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def get_retrieval_service() -> RetrievalService:
    return RetrievalService()
