"""Target service implementing CRUD, validation probes, and lifecycle transitions."""

import datetime
import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from app.connectors.factory import ConnectorFactory
from app.core.errors import ConflictError, NotFoundError, PolicyBlockedError, ValidationError
from app.core.logging import logger
from app.core.ssrf import validate_target_url
from app.db.models.audit import AuditLog
from app.db.models.idempotency import IdempotencyKey
from app.db.models.job import Job
from app.modules.targets.models import Target, TargetCredential
from app.domain.enums import CredentialKind, JobState, TargetMode, TargetStatus
from app.modules.targets.schemas import CreateTargetRequest, PatchTargetRequest
from app.services.base import BaseService
from app.services.credential_service import CredentialService


class TargetService(BaseService):
    """Encapsulates business operations for targets, validation, and authorization consent."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.credential_service = CredentialService(db)

    def create_target(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        request: CreateTargetRequest,
        idempotency_key: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> Target:
        """Register a new evaluation target, store consent, and optionally encrypt initial credential."""
        if idempotency_key:
            req_hash = hashlib.sha256(request.model_dump_json().encode("utf-8")).hexdigest()
            stmt = select(IdempotencyKey).where(
                IdempotencyKey.tenant_id == tenant_id,
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.key == idempotency_key,
            )
            existing_key = self.db.scalars(stmt).first()
            if existing_key:
                if existing_key.request_hash != req_hash:
                    raise ConflictError("Idempotency key reused with different request payload")
                if existing_key.resource_id:
                    existing_target = self.get_target(tenant_id, existing_key.resource_id)
                    return existing_target

        stmt = select(Target).where(
            Target.tenant_id == tenant_id,
            Target.name == request.name,
            Target.deleted_at.is_(None),
        )
        if self.db.scalars(stmt).first():
            raise ConflictError(f"Target with name '{request.name}' already exists in this tenant")

        canonical_url = None
        if request.mode == TargetMode.HOSTED:
            if not request.endpoint_url:
                raise ValidationError("endpoint_url is required for HOSTED mode")
            canonical_url, _ = validate_target_url(request.endpoint_url)

        target_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)
        target = Target(
            id=target_id,
            tenant_id=tenant_id,
            name=request.name,
            mode=request.mode,
            endpoint_url=canonical_url,
            model_ref=request.model_ref,
            request_profile=request.request_profile,
            capabilities=request.capabilities,
            status=TargetStatus.PENDING_VALIDATION,
            authorization_confirmed_at=now,
            configuration_version=1,
            created_by=user_id,
        )
        self.db.add(target)
        self.db.flush()

        if request.credential_payload:
            kind = request.credential_kind or CredentialKind.API_KEY
            self.credential_service.add_target_credential(
                target_id=target_id,
                secret=request.credential_payload,
                kind=kind,
            )

        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="TARGET_CREATED",
            resource_type="TARGET",
            resource_id=target_id,
            request_id=request_id,
            metadata_payload={"target_name": target.name, "mode": target.mode.value},
        )
        self.db.add(audit)

        if idempotency_key:
            expires_at = now + datetime.timedelta(days=1)
            idem = IdempotencyKey(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                key=idempotency_key,
                request_hash=req_hash,
                resource_id=target_id,
                expires_at=expires_at,
            )
            self.db.add(idem)

        self.db.commit()
        self.db.refresh(target)
        return target

    def get_target(self, tenant_id: uuid.UUID, target_id: uuid.UUID) -> Target:
        """Retrieve target with tenant isolation check and soft-delete verification."""
        stmt = select(Target).where(
            Target.id == target_id,
            Target.tenant_id == tenant_id,
            Target.deleted_at.is_(None),
        )
        target = self.db.scalars(stmt).first()
        if not target:
            raise NotFoundError(f"Target '{target_id}' not found")
        return target

    def list_targets(
        self,
        tenant_id: uuid.UUID,
        mode: Optional[TargetMode] = None,
        status_filter: Optional[TargetStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Target], int]:
        """List active targets belonging to a tenant with pagination."""
        query = select(Target).where(
            Target.tenant_id == tenant_id,
            Target.deleted_at.is_(None),
        )
        if mode:
            query = query.where(Target.mode == mode)
        if status_filter:
            query = query.where(Target.status == status_filter)

        total_stmt = select(Target.id).where(
            Target.tenant_id == tenant_id,
            Target.deleted_at.is_(None),
        )
        total_estimate = len(list(self.db.scalars(total_stmt).all()))

        paginated_stmt = query.order_by(Target.created_at.desc()).limit(limit).offset(offset)
        items = list(self.db.scalars(paginated_stmt).all())
        return items, total_estimate

    def update_target(
        self,
        tenant_id: uuid.UUID,
        target_id: uuid.UUID,
        user_id: uuid.UUID,
        patch: PatchTargetRequest,
        request_id: Optional[str] = None,
    ) -> Target:
        """Update mutable target configuration and increment configuration_version."""
        target = self.get_target(tenant_id, target_id)

        if patch.name and patch.name != target.name:
            stmt = select(Target).where(
                Target.tenant_id == tenant_id,
                Target.name == patch.name,
                Target.id != target_id,
                Target.deleted_at.is_(None),
            )
            if self.db.scalars(stmt).first():
                raise ConflictError(f"Target with name '{patch.name}' already exists")
            target.name = patch.name

        if patch.endpoint_url is not None:
            canonical_url, _ = validate_target_url(patch.endpoint_url)
            target.endpoint_url = canonical_url

        if patch.model_ref is not None:
            target.model_ref = patch.model_ref

        if patch.request_profile is not None:
            target.request_profile = patch.request_profile

        if patch.capabilities is not None:
            target.capabilities = patch.capabilities

        target.configuration_version += 1
        target.status = TargetStatus.PENDING_VALIDATION

        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="TARGET_UPDATED",
            resource_type="TARGET",
            resource_id=target_id,
            request_id=request_id,
            metadata_payload={"new_version": target.configuration_version},
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(target)
        return target

    def delete_target(
        self,
        tenant_id: uuid.UUID,
        target_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: Optional[str] = None,
    ) -> None:
        """Soft-delete target if no running jobs exist."""
        target = self.get_target(tenant_id, target_id)

        active_states = [JobState.QUEUED, JobState.RUNNING, JobState.VALIDATING, JobState.AGGREGATING]
        stmt = select(Job).where(
            Job.target_id == target_id,
            Job.state.in_(active_states),
        )
        active_job = self.db.scalars(stmt).first()
        if active_job:
            raise ConflictError(f"Cannot delete target while job {active_job.id} is active (state: {active_job.state.value})")

        target.deleted_at = datetime.datetime.now(datetime.timezone.utc)

        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="TARGET_DELETED",
            resource_type="TARGET",
            resource_id=target_id,
            request_id=request_id,
            metadata_payload={"target_name": target.name},
        )
        self.db.add(audit)
        self.db.commit()

    async def validate_target(
        self,
        tenant_id: uuid.UUID,
        target_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Perform connectivity and SSRF safety verification for a target."""
        target = self.get_target(tenant_id, target_id)
        decrypted_cred = self.credential_service.get_active_credential_decrypted(target_id)

        connector = ConnectorFactory.get_connector(target, decrypted_credential=decrypted_cred)
        now = datetime.datetime.now(datetime.timezone.utc)

        report = await connector.validate({
            "endpoint_url": target.endpoint_url,
            "model_ref": target.model_ref,
        })

        target.last_validated_at = now
        if report.is_valid:
            target.status = TargetStatus.VERIFIED
            target.verified_at = now
            if report.capabilities:
                target.capabilities = {**target.capabilities, **report.capabilities}
        else:
            target.status = TargetStatus.VALIDATION_FAILED

        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="TARGET_VALIDATED",
            resource_type="TARGET",
            resource_id=target_id,
            request_id=request_id,
            metadata_payload={
                "is_valid": report.is_valid,
                "status": target.status.value,
                "host_hash": report.resolved_host_hash,
            },
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(target)

        return {
            "target_id": target.id,
            "status": target.status,
            "resolved_host_hash": report.resolved_host_hash,
            "capability_report": report.capabilities,
            "safe_error_class": report.safe_error_class,
            "checked_at": now,
        }
