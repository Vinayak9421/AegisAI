"""Health check endpoints for container orchestrators, load balancers, and monitoring."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_request_id
from app.core.config import settings
from app.db.session import check_db_connection
from app.schemas.common import ApiResponse, ResponseMeta
from app.schemas.health import HealthLiveResponse, HealthReadyResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health/live",
    response_model=ApiResponse[HealthLiveResponse],
    summary="Public Liveness Endpoint",
)
def health_live(request_id: str = Depends(get_request_id)) -> ApiResponse[HealthLiveResponse]:
    """Process liveness probe; returns 200 without exposing secrets."""
    return ApiResponse(
        data=HealthLiveResponse(
            status="alive",
            environment=settings.APP_ENV,
            version="0.1.0",
        ),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/health/ready",
    response_model=ApiResponse[HealthReadyResponse],
    summary="Readiness Endpoint",
)
def health_ready(
    request_id: str = Depends(get_request_id),
) -> ApiResponse[HealthReadyResponse]:
    """Readiness probe; validates core database connectivity."""
    db_ok = check_db_connection()
    if not db_ok:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is unavailable",
        )
    return ApiResponse(
        data=HealthReadyResponse(
            status="ready",
            database="connected",
            environment=settings.APP_ENV,
        ),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/health/db",
    response_model=ApiResponse[HealthReadyResponse],
    summary="Database Connectivity Check",
)
def health_db(
    db: Session = Depends(get_db),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[HealthReadyResponse]:
    """Explicit database connection probe through dependency injection."""
    return ApiResponse(
        data=HealthReadyResponse(
            status="ready",
            database="connected",
            environment=settings.APP_ENV,
        ),
        meta=ResponseMeta(request_id=request_id),
    )
