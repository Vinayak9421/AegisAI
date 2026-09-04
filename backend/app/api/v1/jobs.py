"""Evaluation jobs management and execution API v1 router."""

from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Header, Path, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant_id, get_db, get_request_id
from app.api.v1.targets import get_or_create_default_principal
from app.domain.enums import JobState, SeverityLevel, Verdict
from app.schemas.common import ApiResponse, Page, ResponseMeta
from app.schemas.jobs import CreateJobRequest, JobResponse
from app.schemas.results import TestResultResponse
from app.services.job_service import JobService
from app.workers.runner import EvaluationRunner

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post(
    "",
    response_model=ApiResponse[JobResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create Evaluation Job",
)
def create_job(
    request: CreateJobRequest,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[JobResponse]:
    """
    Create a new evaluation job for an authorized target.
    Samples test cases according to mode ('QUICK' ~25 prompts, 'FULL' 150-200 prompts).
    Creates individual work items (job_items) in an atomic transaction.
    """
    resolved_tenant_id, resolved_user_id = get_or_create_default_principal(db, tenant_id)
    service = JobService(db)
    job_resp = service.create_job(
        tenant_id=resolved_tenant_id,
        user_id=resolved_user_id,
        request=request,
        idempotency_key=idempotency_key,
        request_id=request_id,
    )
    return ApiResponse(
        data=job_resp,
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "",
    response_model=ApiResponse[Page[JobResponse]],
    summary="List Evaluation Jobs",
)
def list_jobs(
    target_id: Optional[uuid.UUID] = Query(None),
    state: Optional[JobState] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[Page[JobResponse]]:
    """List evaluation jobs for the tenant with optional target and state filters."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = JobService(db)
    page = service.list_jobs(
        tenant_id=resolved_tenant_id,
        target_id=target_id,
        state=state,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(
        data=page,
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/{job_id}",
    response_model=ApiResponse[JobResponse],
    summary="Get Evaluation Job Progress",
)
def get_job(
    job_id: uuid.UUID = Path(..., description="Job UUID"),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[JobResponse]:
    """Retrieve detailed state, item counters, and progress percentage for an evaluation job."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = JobService(db)
    job_resp = service.get_job(tenant_id=resolved_tenant_id, job_id=job_id)
    return ApiResponse(
        data=job_resp,
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/{job_id}/cancel",
    response_model=ApiResponse[JobResponse],
    summary="Cancel Evaluation Job",
)
def cancel_job(
    job_id: uuid.UUID = Path(..., description="Job UUID"),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[JobResponse]:
    """Request cooperative cancellation of a running or queued evaluation job."""
    resolved_tenant_id, resolved_user_id = get_or_create_default_principal(db, tenant_id)
    service = JobService(db)
    job_resp = service.cancel_job(
        tenant_id=resolved_tenant_id, job_id=job_id, user_id=resolved_user_id
    )
    return ApiResponse(
        data=job_resp,
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/{job_id}/run",
    response_model=ApiResponse[JobResponse],
    summary="Execute Pending Job Items",
)
async def run_job_items(
    job_id: uuid.UUID = Path(..., description="Job UUID"),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[JobResponse]:
    """Execute queued evaluation work items for a job and return updated progress."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = JobService(db)
    # Verify ownership
    service.get_job(tenant_id=resolved_tenant_id, job_id=job_id)

    runner = EvaluationRunner(db)
    updated_job = await runner.run_all_pending_items_for_job(job_id)
    job_resp = service.get_job(tenant_id=resolved_tenant_id, job_id=job_id)

    return ApiResponse(
        data=job_resp,
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/{job_id}/results",
    response_model=ApiResponse[Page[TestResultResponse]],
    summary="Get Job Test Results & Verdicts",
)
def get_job_results(
    job_id: uuid.UUID = Path(..., description="Job UUID"),
    category: Optional[str] = Query(None),
    severity: Optional[SeverityLevel] = Query(None),
    verdict: Optional[Verdict] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[Page[TestResultResponse]]:
    """Retrieve paginated test results and judge verdicts for an evaluation job."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = JobService(db)
    page = service.get_job_results(
        tenant_id=resolved_tenant_id,
        job_id=job_id,
        category=category,
        severity=severity,
        verdict=verdict,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(
        data=page,
        meta=ResponseMeta(request_id=request_id),
    )
