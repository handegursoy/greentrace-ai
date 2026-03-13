from __future__ import annotations

from app.schemas.retrieval import MockAnswerResponse, RetrievalRequest
from app.services.llm_answer_service import get_llm_answer_service
from app.services.pydanticai_orchestrator import get_pydanticai_orchestrator
from app.services.retrieval_service import get_retrieval_service


class MockAnswerService:
    def __init__(self) -> None:
        self.retrieval = get_retrieval_service()
        self.orchestrator = get_pydanticai_orchestrator()
        self.answerer = get_llm_answer_service()

    def answer(self, request: RetrievalRequest) -> MockAnswerResponse:
        retrieval = self.retrieval.retrieve(request)
        orchestration = self.orchestrator.orchestrate(request, retrieval)
        answer = self.answerer.generate(request, retrieval)
        return MockAnswerResponse(
            company=request.company,
            question=request.question,
            answer_status="mocked",
            answer=answer,
            retrieval=retrieval,
            orchestration=orchestration,
        )


def get_mock_answer_service() -> MockAnswerService:
    return MockAnswerService()
