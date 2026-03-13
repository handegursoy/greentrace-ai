from __future__ import annotations

from app.schemas.retrieval import RetrievalRequest, RetrievalResponse


class MockLlmAnswerService:
    def generate(self, request: RetrievalRequest, retrieval: RetrievalResponse) -> str:
        return (
            "Mock answer only. Future grounded synthesis will compare company claims against "
            f"{retrieval.total_hits} retrieved evidence chunk(s) for {request.company}."
        )


def get_llm_answer_service() -> MockLlmAnswerService:
    return MockLlmAnswerService()
