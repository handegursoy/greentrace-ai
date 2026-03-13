from pydantic import BaseModel, Field


class RetrievalRequest(BaseModel):
    company: str = Field(min_length=1, max_length=200)
    question: str = Field(min_length=3, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)
    sources: list[str] | None = None


class EvidenceHit(BaseModel):
    point_id: str
    article_id: str
    score: float
    text: str
    title: str | None = None
    url: str
    domain: str
    source: str
    matched_keywords: list[str] = Field(default_factory=list)
    keyword_relevance: float | None = None


class RetrievalResponse(BaseModel):
    company: str
    question: str
    collection_name: str
    total_hits: int
    evidence: list[EvidenceHit]


class MockAnswerResponse(BaseModel):
    company: str
    question: str
    answer_status: str
    answer: str
    retrieval: RetrievalResponse
    orchestration: dict[str, str]
