from fastapi import APIRouter

from app.api.routes.company_esg import router as company_esg_router
from app.api.routes.evidence_ingestion import router as evidence_ingestion_router
from app.api.routes.evidence_qa import router as evidence_qa_router


api_router = APIRouter()
api_router.include_router(company_esg_router)
api_router.include_router(evidence_ingestion_router)
api_router.include_router(evidence_qa_router)