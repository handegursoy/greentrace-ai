from fastapi import APIRouter, HTTPException

from app.schemas.retrieval import MockAnswerResponse, RetrievalRequest, RetrievalResponse
from app.services.mock_answer_service import get_mock_answer_service
from app.services.retrieval_service import get_retrieval_service


router = APIRouter(tags=["evidence-qa"])


@router.post("/evidence/retrieve", response_model=RetrievalResponse)
def retrieve_evidence(request: RetrievalRequest) -> RetrievalResponse:
    try:
        return get_retrieval_service().retrieve(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/evidence/answer/mock", response_model=MockAnswerResponse)
def answer_with_mock_llm(request: RetrievalRequest) -> MockAnswerResponse:
    try:
        return get_mock_answer_service().answer(request)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
