from pydantic import BaseModel, Field


class EvidenceArticle(BaseModel):
    article_id: str
    company: str
    query: str | None = None
    title: str | None = None
    url: str
    domain: str
    content: str
    source: str
    matched_keywords: list[str] = Field(default_factory=list)
    keyword_relevance: float | None = None


class EvidenceChunk(BaseModel):
    point_id: str
    article_id: str
    company: str
    chunk_index: int
    text: str
    title: str | None = None
    url: str
    domain: str
    source: str
    query: str | None = None
    matched_keywords: list[str] = Field(default_factory=list)
    keyword_relevance: float | None = None


class IngestionResult(BaseModel):
    company: str
    overall_status: str
    collection_name: str
    article_count: int
    chunk_count: int
    source_breakdown: dict[str, int]
