"""Provenance service implementing metadata ingestion, versioning, scoring, and audit logging."""

import datetime
import hashlib
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.core.logging import logger
from app.db.models.audit import AuditLog
from app.db.models.idempotency import IdempotencyKey
from app.db.models.provenance import ProvenanceRecord
from app.db.models.target import Target
from app.provenance.scorer import ProvenanceScorer
from app.schemas.provenance import DimensionScores, ProvenanceRequest
from app.services.base import BaseService


class ProvenanceService(BaseService):
    """Encapsulates business operations for declared provenance metadata and Identity Scores."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.scorer = ProvenanceScorer()

    def _verify_target(self, tenant_id: uuid.UUID, target_id: uuid.UUID) -> Target:
        """Verify that target exists, belongs to tenant, and is not soft-deleted."""
        stmt = select(Target).where(
            Target.id == target_id,
            Target.tenant_id == tenant_id,
            Target.deleted_at.is_(None),
        )
        target = self.db.scalars(stmt).first()
        if not target:
            raise NotFoundError(f"Target '{target_id}' not found or does not belong to this tenant")
        return target

    def _attach_dimension_scores(self, record: ProvenanceRecord) -> ProvenanceRecord:
        """Recompute dimension scores for serialization (without modifying DB record)."""
        score_result = self.scorer.calculate_identity_score(
            model_metadata=record.model_metadata,
            data_sources=record.data_sources,
            system_prompt_metadata=record.system_prompt_metadata,
            operational_metadata=record.operational_metadata,
        )
        setattr(
            record,
            "dimension_scores",
            DimensionScores(**score_result.dimension_scores),
        )
        return record

    def create_provenance_record(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        target_id: uuid.UUID,
        request: ProvenanceRequest,
        idempotency_key: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> ProvenanceRecord:
        """
        Ingest declared metadata, compute versioned Identity Score, and persist immutable version.
        Supports idempotency deduplication and generates an audit log entry.
        """
        # 1. Target existence and tenant isolation
        self._verify_target(tenant_id, target_id)

        # 2. Idempotency Check
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
                    existing_record = self.get_provenance_by_id(tenant_id, target_id, existing_key.resource_id)
                    return existing_record

        # 3. Calculate next sequential version number
        stmt_v = select(func.coalesce(func.max(ProvenanceRecord.version), 0)).where(
            ProvenanceRecord.target_id == target_id
        )
        current_version = self.db.scalar(stmt_v) or 0
        next_version = current_version + 1

        # 4. Calculate Identity Score & Quality Flags via ProvenanceScorer
        score_result = self.scorer.calculate_identity_score(
            model_metadata=request.model_metadata,
            data_sources=request.data_sources,
            system_prompt_metadata=request.system_prompt_metadata,
            operational_metadata=request.operational_metadata,
        )

        # 5. Persist ProvenanceRecord
        record_id = uuid.uuid4()
        record = ProvenanceRecord(
            id=record_id,
            target_id=target_id,
            version=next_version,
            model_metadata=request.model_metadata,
            data_sources=request.data_sources,
            system_prompt_metadata=request.system_prompt_metadata,
            operational_metadata=request.operational_metadata,
            evidence_refs=request.evidence_refs,
            identity_score=score_result.identity_score,
            score_version=score_result.score_version,
            quality_flags=score_result.quality_flags,
            created_by=user_id,
        )
        self.db.add(record)
        self.db.flush()

        now = datetime.datetime.now(datetime.timezone.utc)

        # 6. Record idempotency token if supplied
        if idempotency_key:
            expires_at = now + datetime.timedelta(days=1)
            idemp = IdempotencyKey(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                key=idempotency_key,
                request_hash=req_hash,
                resource_id=record_id,
                expires_at=expires_at,
            )
            self.db.add(idemp)

        # 7. Append audit log
        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="PROVENANCE_RECORD_CREATED",
            resource_type="provenance_record",
            resource_id=record_id,
            request_id=request_id,
            metadata_payload={
                "target_id": str(target_id),
                "version": next_version,
                "identity_score": score_result.identity_score,
                "score_version": score_result.score_version,
                "quality_flags": score_result.quality_flags,
                "dimension_scores": score_result.dimension_scores,
            },
        )
        self.db.add(audit)


        self.db.commit()
        self.db.refresh(record)

        # Attach dimension scores for response serialization
        setattr(
            record,
            "dimension_scores",
            DimensionScores(**score_result.dimension_scores),
        )

        logger.info(
            f"Created provenance record v{next_version} for target {target_id} with Identity Score {score_result.identity_score}",
            extra={"target_id": str(target_id), "identity_score": score_result.identity_score},
        )
        return record

    def get_provenance_by_id(
        self, tenant_id: uuid.UUID, target_id: uuid.UUID, record_id: uuid.UUID
    ) -> ProvenanceRecord:
        """Fetch a specific provenance record by its primary key UUID."""
        self._verify_target(tenant_id, target_id)
        stmt = select(ProvenanceRecord).where(
            ProvenanceRecord.id == record_id,
            ProvenanceRecord.target_id == target_id,
        )
        record = self.db.scalars(stmt).first()
        if not record:
            raise NotFoundError(f"Provenance record '{record_id}' not found for target '{target_id}'")
        return self._attach_dimension_scores(record)

    def get_provenance_by_version(
        self, tenant_id: uuid.UUID, target_id: uuid.UUID, version: int
    ) -> ProvenanceRecord:
        """Fetch a specific historical provenance version for a target."""
        self._verify_target(tenant_id, target_id)
        stmt = select(ProvenanceRecord).where(
            ProvenanceRecord.target_id == target_id,
            ProvenanceRecord.version == version,
        )
        record = self.db.scalars(stmt).first()
        if not record:
            raise NotFoundError(f"Provenance version {version} not found for target '{target_id}'")
        return self._attach_dimension_scores(record)

    def get_latest_provenance(
        self, tenant_id: uuid.UUID, target_id: uuid.UUID
    ) -> ProvenanceRecord:
        """Fetch the latest active provenance record for a target."""
        self._verify_target(tenant_id, target_id)
        stmt = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.target_id == target_id)
            .order_by(ProvenanceRecord.version.desc())
        )
        record = self.db.scalars(stmt).first()
        if not record:
            raise NotFoundError(f"No provenance records declared for target '{target_id}'")
        return self._attach_dimension_scores(record)

    def get_provenance_history(
        self, tenant_id: uuid.UUID, target_id: uuid.UUID
    ) -> List[ProvenanceRecord]:
        """Fetch all historical provenance versions for a target, ordered newest to oldest."""
        self._verify_target(tenant_id, target_id)
        stmt = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.target_id == target_id)
            .order_by(ProvenanceRecord.version.desc())
        )
        records = list(self.db.scalars(stmt).all())
        for r in records:
            self._attach_dimension_scores(r)
        return records
