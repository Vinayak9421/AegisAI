"""Benchmark catalog and test case sampling API v1 router."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant_id, get_db, get_request_id
from app.domain.enums import BenchmarkSourceStatus, BenchmarkSourceType, SeverityLevel, TestCaseMode
from app.schemas.benchmarks import (
    BatchIngestTestCasesRequest,
    BenchmarkSourceResponse,
    BenchmarkSourceSummaryResponse,
    CreateBenchmarkSourceRequest,
    IngestBatchResponse,
    SampledTestCasesResponse,
    SampleTestCasesRequest,
    TestCaseResponse,
)
from app.schemas.common import ApiResponse, Page, ResponseMeta
from app.services.benchmark_service import BenchmarkService

router = APIRouter(prefix="/benchmarks", tags=["Benchmarks"])


@router.get(
    "/sources",
    response_model=ApiResponse[List[BenchmarkSourceSummaryResponse]],
    summary="List Benchmark Sources",
)
def list_sources(
    source_type: Optional[BenchmarkSourceType] = Query(None),
    status_filter: Optional[BenchmarkSourceStatus] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[List[BenchmarkSourceSummaryResponse]]:
    """List all registered benchmark sources with aggregated test case counts and category breakdowns."""
    service = BenchmarkService(db)
    sources = service.list_sources(source_type=source_type, status=status_filter)
    return ApiResponse(
        data=sources,
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/sources/{source_id}",
    response_model=ApiResponse[BenchmarkSourceSummaryResponse],
    summary="Get Benchmark Source Summary",
)
def get_source_summary(
    source_id: uuid.UUID,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[BenchmarkSourceSummaryResponse]:
    """Retrieve detailed statistics, category breakdowns, and manifest hash for a benchmark source."""
    service = BenchmarkService(db)
    summary = service.get_source_summary(source_id)
    return ApiResponse(
        data=summary,
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/sources",
    response_model=ApiResponse[BenchmarkSourceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register Benchmark Source Manifest",
)
def create_source(
    request: CreateBenchmarkSourceRequest,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[BenchmarkSourceResponse]:
    """Register a new immutable benchmark source manifest."""
    service = BenchmarkService(db)
    source = service.create_source(tenant_id=tenant_id, request=request)
    return ApiResponse(
        data=BenchmarkSourceResponse.model_validate(source, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/test-cases",
    response_model=ApiResponse[Page[TestCaseResponse]],
    summary="Search Test Cases",
)
def list_test_cases(
    source_id: Optional[uuid.UUID] = Query(None),
    category: Optional[str] = Query(None),
    subcategory: Optional[str] = Query(None),
    severity: Optional[SeverityLevel] = Query(None),
    mode: Optional[TestCaseMode] = Query(None),
    search: Optional[str] = Query(None, description="Substring search within prompt templates"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[Page[TestCaseResponse]]:
    """Paginated search across curated attack test cases with category and text filters."""
    service = BenchmarkService(db)
    page = service.list_test_cases(
        source_id=source_id,
        category=category,
        subcategory=subcategory,
        severity=severity,
        mode=mode,
        search=search,
        limit=limit,
        offset=offset,
    )
    return ApiResponse(
        data=page,
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/test-cases",
    response_model=ApiResponse[IngestBatchResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Batch Ingest Test Cases",
)
def ingest_test_cases(
    request: BatchIngestTestCasesRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[IngestBatchResponse]:
    """
    Batch ingest test cases into a benchmark source.
    Automatically computes SHA-256 content hashes, skips existing duplicate prompts, and updates the manifest hash.
    """
    service = BenchmarkService(db)
    result = service.ingest_test_cases(source_id=request.source_id, cases=request.test_cases)
    return ApiResponse(
        data=result,
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/sample",
    response_model=ApiResponse[SampledTestCasesResponse],
    summary="Sample Test Cases for Evaluation Run",
)
def sample_test_cases(
    request: SampleTestCasesRequest,
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[SampledTestCasesResponse]:
    """
    Sample a balanced, deterministic set of test cases for an evaluation job.
    - Quick Mode defaults to 25 prompts balanced across categories.
    - Full Audit Mode is capped at 150-200 relevant prompts.
    - Uses seed for reproducible, scientific evaluation.
    """
    service = BenchmarkService(db)
    result = service.select_test_cases(
        mode=request.mode,
        categories=request.categories,
        seed=request.seed,
        sample_size=request.sample_size,
    )
    return ApiResponse(
        data=result,
        meta=ResponseMeta(request_id=request_id),
    )
