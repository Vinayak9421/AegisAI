"""Target and credential management API v1 router."""

import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_tenant_id, get_db, get_request_id
from app.core.errors import ValidationError
from app.db.models.tenant import User, Tenant
from app.domain.enums import TargetMode, TargetStatus
from app.schemas.common import ApiResponse, Page, ResponseMeta
from app.schemas.targets import (
    AddCredentialRequest,
    CreateTargetRequest,
    CredentialMetadataResponse,
    PatchTargetRequest,
    TargetResponse,
    TargetValidationResponse,
)
from app.services.credential_service import CredentialService
from app.services.target_service import TargetService

router = APIRouter(prefix="/targets", tags=["Targets"])


def get_or_create_default_principal(db: Session, tenant_id: Optional[uuid.UUID] = None) -> tuple[uuid.UUID, uuid.UUID]:
    """Helper to ensure a valid tenant_id and user_id exist for requests in development/evaluation."""
    if tenant_id:
        tenant = db.get(Tenant, tenant_id)
        if tenant:
            user = tenant.users[0] if tenant.users else None
            if not user:
                user = User(id=uuid.uuid4(), tenant_id=tenant.id, email=f"admin-{tenant.id.hex[:6]}@aegis.local")
                db.add(user)
                db.commit()
                db.refresh(user)
            return tenant.id, user.id
        else:
            # Explicit tenant_id was provided: create that tenant and principal to ensure true tenant isolation
            tenant = Tenant(id=tenant_id, name=f"Isolated Tenant-{tenant_id.hex[:6]}")
            db.add(tenant)
            db.flush()
            user = User(id=uuid.uuid4(), tenant_id=tenant.id, email=f"admin-{tenant.id.hex[:6]}@aegis.local")
            db.add(user)
            db.commit()
            db.refresh(user)
            return tenant.id, user.id
    
    # Default fallback for testing / local execution without explicit X-Tenant-ID header
    first_tenant = db.query(Tenant).first()
    if not first_tenant:
        first_tenant = Tenant(id=uuid.uuid4(), name="Default Fintech Tenant")
        db.add(first_tenant)
        db.flush()

    first_user = db.query(User).filter(User.tenant_id == first_tenant.id).first()
    if not first_user:
        first_user = User(
            id=uuid.uuid4(),
            tenant_id=first_tenant.id,
            email="admin@aegis.local",
        )
        db.add(first_user)
        db.commit()
        db.refresh(first_user)

    return first_tenant.id, first_user.id



@router.post(
    "",
    response_model=ApiResponse[TargetResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register Target Application",
)
def create_target(
    request: CreateTargetRequest,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[TargetResponse]:
    """
    Register a target for trust/safety evaluation.
    Requires explicit authorization confirmation.
    Accepts optional initial credential to encrypt at rest.
    """
    resolved_tenant_id, resolved_user_id = get_or_create_default_principal(db, tenant_id)
    service = TargetService(db)
    target = service.create_target(
        tenant_id=resolved_tenant_id,
        user_id=resolved_user_id,
        request=request,
        idempotency_key=idempotency_key,
        request_id=request_id,
    )
    return ApiResponse(
        data=TargetResponse.model_validate(target, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "",
    response_model=ApiResponse[Page[TargetResponse]],
    summary="List Targets",
)
def list_targets(
    mode: Optional[TargetMode] = Query(None),
    status_filter: Optional[TargetStatus] = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[Page[TargetResponse]]:
    """List registered targets belonging to the authenticated tenant."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = TargetService(db)
    items, total_est = service.list_targets(
        tenant_id=resolved_tenant_id,
        mode=mode,
        status_filter=status_filter,
        limit=limit,
        offset=offset,
    )
    pydantic_items = [TargetResponse.model_validate(t, from_attributes=True) for t in items]
    return ApiResponse(
        data=Page(items=pydantic_items, total_estimate=total_est),
        meta=ResponseMeta(request_id=request_id),
    )


@router.get(
    "/{id}",
    response_model=ApiResponse[TargetResponse],
    summary="Get Target by ID",
)
def get_target(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[TargetResponse]:
    """Retrieve sanitized target details (never returning credentials)."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    service = TargetService(db)
    target = service.get_target(resolved_tenant_id, id)
    return ApiResponse(
        data=TargetResponse.model_validate(target, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )


@router.patch(
    "/{id}",
    response_model=ApiResponse[TargetResponse],
    summary="Update Target Configuration",
)
def update_target(
    id: uuid.UUID,
    patch: PatchTargetRequest,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[TargetResponse]:
    """Update target configuration, bumping configuration_version and setting status to PENDING_VALIDATION."""
    resolved_tenant_id, resolved_user_id = get_or_create_default_principal(db, tenant_id)
    service = TargetService(db)
    target = service.update_target(
        tenant_id=resolved_tenant_id,
        target_id=id,
        user_id=resolved_user_id,
        patch=patch,
        request_id=request_id,
    )
    return ApiResponse(
        data=TargetResponse.model_validate(target, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft Delete Target",
)
def delete_target(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
):
    """Soft delete target if no running jobs exist."""
    resolved_tenant_id, resolved_user_id = get_or_create_default_principal(db, tenant_id)
    service = TargetService(db)
    service.delete_target(
        tenant_id=resolved_tenant_id,
        target_id=id,
        user_id=resolved_user_id,
        request_id=request_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{id}/validate",
    response_model=ApiResponse[TargetValidationResponse],
    summary="Validate Target Connectivity & SSRF Safety",
)
async def validate_target(
    id: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[TargetValidationResponse]:
    """Execute SSRF safety checks and connectivity probe against the target application."""
    resolved_tenant_id, resolved_user_id = get_or_create_default_principal(db, tenant_id)
    service = TargetService(db)
    report = await service.validate_target(
        tenant_id=resolved_tenant_id,
        target_id=id,
        user_id=resolved_user_id,
        request_id=request_id,
    )
    return ApiResponse(
        data=TargetValidationResponse(**report),
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/{id}/credentials",
    response_model=ApiResponse[CredentialMetadataResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add Target Credential",
)
def add_credential(
    id: uuid.UUID,
    request: AddCredentialRequest,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[CredentialMetadataResponse]:
    """Encrypt and attach credential to target. Secret plaintext is never echoed."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    target_service = TargetService(db)
    target_service.get_target(resolved_tenant_id, id)  # check target exists

    cred_service = CredentialService(db)
    cred = cred_service.add_target_credential(
        target_id=id,
        secret=request.secret,
        kind=request.kind,
    )
    return ApiResponse(
        data=CredentialMetadataResponse.model_validate(cred, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )


@router.post(
    "/{id}/credentials/{cid}/revoke",
    response_model=ApiResponse[CredentialMetadataResponse],
    summary="Revoke Target Credential",
)
def revoke_credential(
    id: uuid.UUID,
    cid: uuid.UUID,
    db: Session = Depends(get_db),
    tenant_id: Optional[uuid.UUID] = Depends(get_current_tenant_id),
    request_id: str = Depends(get_request_id),
) -> ApiResponse[CredentialMetadataResponse]:
    """Revoke a target credential so active and future jobs cannot use it."""
    resolved_tenant_id, _ = get_or_create_default_principal(db, tenant_id)
    target_service = TargetService(db)
    target_service.get_target(resolved_tenant_id, id)  # check target exists

    cred_service = CredentialService(db)
    cred = cred_service.revoke_credential(target_id=id, credential_id=cid)
    return ApiResponse(
        data=CredentialMetadataResponse.model_validate(cred, from_attributes=True),
        meta=ResponseMeta(request_id=request_id),
    )
