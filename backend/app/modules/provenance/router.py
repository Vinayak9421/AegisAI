"""Provenance metadata and Identity Score API router."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant_id, get_db, get_request_id
from app.modules.targets.router import get_or_create_default_principal
from app.schemas.common import ApiResponse, ResponseMeta
from app.modules.provenance.schemas import ProvenanceRequest, ProvenanceResponse
from app.modules.provenance.service import ProvenanceService

router = APIRouter(prefix="/targets/{target_id}/provenance", tags=["Provenance"])


@router.post(
    "",
    response_model=ApiResponse[ProvenanceResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Declare Target Provenance & Calculate Identity Score",
)
def create_provenance(
    target_id: uuid.UUID = Path(..., description="Target application UUID"),
    request: ProvenanceRequest = ...,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ProvenanceResponse]:
    """
    Ingest declared metadata for a registered target.
    Calculates the 4-dimension Identity Score (0-100) and produces immutable version.
    """
    resolved_tenant_id, resolved_user_id = get_or_create_default_principal(db, tenant_id)
    service = ProvenanceService(db)
    record = service.create_provenance_record(
        tenant_id=resolved_tenant_id,
        user_id=resolved_user_id,
        target_id=target_id,
        request=request,
        idempotency_key=idempotency_key,
        request_id=request_id,
    )
    return ApiResponse(
        data=ProvenanceResponse.model_validate(record, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "",
    response_model=ApiResponse[List[ProvenanceResponse]],
    summary="List Target Provenance Versions",
)
def list_provenance_versions(
    target_id: uuid.UUID = Path(..., description="Target application UUID"),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[List[ProvenanceResponse]]:
    """List all immutable provenance versions for a target application, newest to oldest."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = ProvenanceService(db)
    records = service.get_provenance_history(tenant_id=resolved_tenant_id, target_id=target_id)
    return ApiResponse(
        data=[ProvenanceResponse.model_validate(r, from_attributes=True) for r in records],
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/latest",
    response_model=ApiResponse[ProvenanceResponse],
    summary="Get Latest Target Provenance & Identity Score",
)
def get_latest_provenance(
    target_id: uuid.UUID = Path(..., description="Target application UUID"),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ProvenanceResponse]:
    """Retrieve the latest active provenance record and Identity Score for a target."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = ProvenanceService(db)
    record = service.get_latest_provenance(tenant_id=resolved_tenant_id, target_id=target_id)
    return ApiResponse(
        data=ProvenanceResponse.model_validate(record, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/{version}",
    response_model=ApiResponse[ProvenanceResponse],
    summary="Get Specific Provenance Version",
)
def get_provenance_by_version(
    target_id: uuid.UUID = Path(..., description="Target application UUID"),
    version: int = Path(..., ge=1, description="Sequential version number"),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[ProvenanceResponse]:
    """Retrieve a specific historical provenance version for a target application."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = ProvenanceService(db)
    record = service.get_provenance_by_version(
        tenant_id=resolved_tenant_id, target_id=target_id, version=version
    )
    return ApiResponse(
        data=ProvenanceResponse.model_validate(record, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )
