from __future__ import annotations

from app.schemas.retrieval import RetrievalRequest, RetrievalResponse


class MockPydanticAIOrchestrator:
    def orchestrate(self, request: RetrievalRequest, retrieval: RetrievalResponse) -> dict[str, str]:
        return {
            "agent": "pydanticai-mock",
            "company": request.company,
            "question": request.question,
            "evidence_count": str(retrieval.total_hits),
            "next_step": "Pass retrieved evidence to the future answer model.",
        }


def get_pydanticai_orchestrator() -> MockPydanticAIOrchestrator:
    return MockPydanticAIOrchestrator()
