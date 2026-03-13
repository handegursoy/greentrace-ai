from __future__ import annotations

from app.core.config import get_settings
from app.schemas.company_esg import CompanyEsgOptions
from app.schemas.evidence import IngestionResult
from app.services.article_chunker import ArticleChunker
from app.services.classifier import get_classifier
from app.services.evidence_normalizer import extract_evidence_articles
from app.services.greentrace_actor import run_greentrace_actor
from app.services.qdrant_store import get_qdrant_store


class EvidenceIngestionService:
    def __init__(self) -> None:
        settings = get_settings()
        self.chunker = ArticleChunker(
            chunk_size_words=settings.chunk_size_words,
            chunk_overlap_words=settings.chunk_overlap_words,
        )
        self.classifier = get_classifier()
        self.store = get_qdrant_store()

    def ingest_company(self, company: str, options: CompanyEsgOptions) -> IngestionResult:
        payload = run_greentrace_actor(company=company, options=options)
        return self.ingest_payload(company=company, payload=payload)

    def ingest_payload(self, company: str, payload: dict) -> IngestionResult:
        articles = extract_evidence_articles(company=company, payload=payload)
        chunks = self.classifier.enrich(self.chunker.chunk_articles(articles))
        stored_count = self.store.upsert_chunks(chunks) if chunks else 0
        source_breakdown: dict[str, int] = {}
        for article in articles:
            source_breakdown[article.source] = source_breakdown.get(article.source, 0) + 1
        return IngestionResult(
            company=company,
            overall_status=str(payload.get("overall_status") or "unknown"),
            collection_name=self.store.collection_name,
            article_count=len(articles),
            chunk_count=stored_count,
            source_breakdown=source_breakdown,
        )


def get_ingestion_service() -> EvidenceIngestionService:
    return EvidenceIngestionService()
