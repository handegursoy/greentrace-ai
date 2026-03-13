from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.routes.company_esg import build_options
from app.schemas.company_esg import CompanyEsgOptions
from app.schemas.evidence import IngestionResult
from app.services.greentrace_actor import ActorServiceError
from app.services.ingestion_service import get_ingestion_service


router = APIRouter(tags=["evidence-ingestion"])


@router.post("/evidence/companies/{company}/ingest", response_model=IngestionResult)
def ingest_company_evidence(
    company: Annotated[str, Path(min_length=1, max_length=200)],
    options: Annotated[CompanyEsgOptions, Depends(build_options)],
) -> IngestionResult:
    try:
        return get_ingestion_service().ingest_company(company=company, options=options)
    except ActorServiceError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
