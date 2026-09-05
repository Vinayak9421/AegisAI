"""Provenance service implementing metadata ingestion, versioning, scoring, and audit logging."""

import datetime
import hashlib
import uuid
from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError
from app.core.logging import logger
from app.db.models.audit import AuditLog
from app.db.models.idempotency import IdempotencyKey
from app.modules.provenance.models import ProvenanceRecord
from app.modules.targets.models import Target
from app.provenance.scorer import ProvenanceScorer
from app.modules.provenance.schemas import DimensionScores, ProvenanceRequest
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
            DimensionScores(
                model_identity=score_result.dimension_scores["model_identity"],
                data_provenance=score_result.dimension_scores["data_provenance"],
                system_configuration=score_result.dimension_scores["system_configuration"],
                operational_accountability=score_result.dimension_scores["operational_accountability"],
            ),
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
        """Ingest declared metadata, calculate Identity Score, and produce immutable version."""
        self._verify_target(tenant_id, target_id)

        req_hash = hashlib.sha256(request.model_dump_json().encode("utf-8")).hexdigest()
        now = datetime.datetime.now(datetime.timezone.utc)

        if idempotency_key:
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
                    record = self.db.get(ProvenanceRecord, existing_key.resource_id)
                    if record:
                        return self._attach_dimension_scores(record)

        version_stmt = select(func.max(ProvenanceRecord.version)).where(
            ProvenanceRecord.target_id == target_id
        )
        current_max = self.db.scalars(version_stmt).first() or 0
        new_version = current_max + 1

        score_result = self.scorer.calculate_identity_score(
            model_metadata=request.model_metadata,
            data_sources=request.data_sources,
            system_prompt_metadata=request.system_prompt_metadata,
            operational_metadata=request.operational_metadata,
        )

        record_id = uuid.uuid4()
        record = ProvenanceRecord(
            id=record_id,
            target_id=target_id,
            version=new_version,
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

        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="PROVENANCE_DECLARED",
            resource_type="TARGET",
            resource_id=target_id,
            request_id=request_id,
            metadata_payload={
                "provenance_id": str(record_id),
                "version": new_version,
                "identity_score": score_result.identity_score,
                "flags": score_result.quality_flags,
            },
        )
        self.db.add(audit)

        if idempotency_key:
            idem = IdempotencyKey(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                key=idempotency_key,
                request_hash=req_hash,
                resource_id=record_id,
                expires_at=now + datetime.timedelta(days=1),
            )
            self.db.add(idem)

        self.db.commit()
        self.db.refresh(record)

        setattr(
            record,
            "dimension_scores",
            DimensionScores(
                model_identity=score_result.dimension_scores["model_identity"],
                data_provenance=score_result.dimension_scores["data_provenance"],
                system_configuration=score_result.dimension_scores["system_configuration"],
                operational_accountability=score_result.dimension_scores["operational_accountability"],
            ),
        )
        logger.info(
            f"Created provenance v{new_version} for target {target_id}: "
            f"score={score_result.identity_score}/100, flags={len(score_result.quality_flags)}"
        )
        return record

    def get_latest_provenance(self, tenant_id: uuid.UUID, target_id: uuid.UUID) -> ProvenanceRecord:
        """Retrieve the latest immutable provenance record for a target."""
        self._verify_target(tenant_id, target_id)
        stmt = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.target_id == target_id)
            .order_by(ProvenanceRecord.version.desc())
        )
        record = self.db.scalars(stmt).first()
        if not record:
            raise NotFoundError(f"No provenance records found for target '{target_id}'")
        return self._attach_dimension_scores(record)

    def get_provenance_version(
        self, tenant_id: uuid.UUID, target_id: uuid.UUID, version: int
    ) -> ProvenanceRecord:
        """Retrieve a specific historical provenance version for a target."""
        self._verify_target(tenant_id, target_id)
        stmt = select(ProvenanceRecord).where(
            ProvenanceRecord.target_id == target_id,
            ProvenanceRecord.version == version,
        )
        record = self.db.scalars(stmt).first()
        if not record:
            raise NotFoundError(
                f"Provenance record v{version} not found for target '{target_id}'"
            )
        return self._attach_dimension_scores(record)

    def list_provenance_versions(
        self, tenant_id: uuid.UUID, target_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> Tuple[List[ProvenanceRecord], int]:
        """List all historical provenance versions for a target, ordered by version descending."""
        self._verify_target(tenant_id, target_id)
        total_stmt = select(ProvenanceRecord.id).where(ProvenanceRecord.target_id == target_id)
        total_estimate = len(list(self.db.scalars(total_stmt).all()))

        query = (
            select(ProvenanceRecord)
            .where(ProvenanceRecord.target_id == target_id)
            .order_by(ProvenanceRecord.version.desc())
            .limit(limit)
            .offset(offset)
        )
        records = list(self.db.scalars(query).all())
        return [self._attach_dimension_scores(r) for r in records], total_estimate

    get_provenance_by_version = get_provenance_version

    def get_provenance_history(self, tenant_id: uuid.UUID, target_id: uuid.UUID) -> List[ProvenanceRecord]:
        records, _ = self.list_provenance_versions(tenant_id, target_id)
        return records
