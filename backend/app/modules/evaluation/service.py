"""Job service implementing evaluation run creation, state transitions, and results retrieval."""

import datetime
import hashlib
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.logging import logger
from app.db.models.audit import AuditLog
from app.db.models.certificate import Certificate
from app.db.models.idempotency import IdempotencyKey
from app.domain.enums import JobItemState, JobMode, JobState, SeverityLevel, TargetStatus, Verdict
from app.modules.benchmarks.service import BenchmarkService
from app.modules.evaluation.models import Job, JobItem, TestResult
from app.modules.evaluation.schemas import CreateJobRequest, JobResponse, TestResultResponse
from app.modules.targets.models import Target
from app.schemas.common import Page
from app.services.base import BaseService


class JobService(BaseService):
    """Encapsulates operations for evaluation job lifecycle, progress tracking, and results."""

    def __init__(self, db: Session):
        super().__init__(db)
        self.benchmark_service = BenchmarkService(db)

    def _verify_job_in_tenant(self, tenant_id: uuid.UUID, job_id: uuid.UUID) -> Job:
        """Verify job exists and belongs to the specified tenant."""
        stmt = select(Job).where(Job.id == job_id, Job.tenant_id == tenant_id)
        job = self.db.scalars(stmt).first()
        if not job:
            raise NotFoundError(f"Job '{job_id}' not found in this tenant")
        return job

    def _format_job_response(self, job: Job) -> JobResponse:
        """Helper to attach dynamic progress_percentage and real trust score to JobResponse."""
        progress = (job.completed_items / job.total_items * 100.0) if job.total_items > 0 else 0.0

        trust_score = None
        trust_grade = None
        stmt_cert = (
            select(Certificate)
            .where(Certificate.job_id == job.id)
            .order_by(Certificate.version.desc())
        )
        cert = self.db.scalars(stmt_cert).first()
        if cert and cert.trust_score is not None:
            trust_score = float(cert.trust_score)
            trust_grade = (
                "Grade A" if trust_score >= 90.0 else (
                    "Grade B" if trust_score >= 75.0 else (
                        "Grade C" if trust_score >= 60.0 else "Grade F"
                    )
                )
            )

        return JobResponse(
            id=job.id,
            tenant_id=job.tenant_id,
            target_id=job.target_id,
            created_by=job.created_by,
            mode=job.mode,
            state=job.state,
            total_items=job.total_items,
            completed_items=job.completed_items,
            failed_items=job.failed_items,
            progress_percentage=round(progress, 1),
            scoring_version=job.scoring_version,
            sampling_seed=job.sampling_seed,
            started_at=job.started_at,
            finished_at=job.finished_at,
            error_summary=job.error_summary,
            trust_score=trust_score,
            trust_grade=trust_grade,
            created_at=job.created_at,
        )

    def create_job(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        request: CreateJobRequest,
        idempotency_key: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> JobResponse:
        """
        Create an evaluation job, snapshot target configuration, sample test cases,
        and generate individual work items (job_items) in a single transaction.
        """
        # 1. Target verification
        stmt = select(Target).where(
            Target.id == request.target_id,
            Target.tenant_id == tenant_id,
            Target.deleted_at.is_(None),
        )
        target = self.db.scalars(stmt).first()
        if not target:
            raise NotFoundError(f"Target '{request.target_id}' not found or belongs to another tenant")

        if target.status != TargetStatus.VERIFIED:
            raise ValidationError(
                f"Target '{request.target_id}' is in status '{target.status.value}'. Target must be VERIFIED prior to scheduling an evaluation run."
            )

        # 2. Explicit authorization check
        if not request.authorization_confirmed:
            raise ValidationError("Evaluation job creation requires explicit authorization confirmation.")

        # 3. Idempotency check
        if idempotency_key:
            req_hash = hashlib.sha256(request.model_dump_json().encode("utf-8")).hexdigest()
            stmt_idemp = select(IdempotencyKey).where(
                IdempotencyKey.tenant_id == tenant_id,
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.key == idempotency_key,
            )
            existing_key = self.db.scalars(stmt_idemp).first()
            if existing_key:
                if existing_key.request_hash != req_hash:
                    raise ConflictError("Idempotency key reused with different request payload")
                if existing_key.resource_id:
                    existing_job = self._verify_job_in_tenant(tenant_id, existing_key.resource_id)
                    return self._format_job_response(existing_job)

        # 4. Sample test cases from catalog via BenchmarkService
        seed = request.sampling_seed if request.sampling_seed is not None else 42
        sampled = self.benchmark_service.select_test_cases(
            mode=request.mode,
            categories=request.category_filters if request.category_filters else None,
            seed=seed,
        )

        if sampled.total_sampled == 0:
            raise ValidationError(
                "No approved test cases found in catalog matching the requested evaluation criteria. "
                "Ensure benchmarks have been ingested."
            )

        job_id = uuid.uuid4()
        now = datetime.datetime.now(datetime.timezone.utc)

        # 5. Build immutable Job entity
        job = Job(
            id=job_id,
            tenant_id=tenant_id,
            target_id=request.target_id,
            created_by=user_id,
            mode=request.mode,
            state=JobState.QUEUED,
            config_snapshot={
                "target_name": target.name,
                "target_mode": target.mode.value,
                "target_version": target.configuration_version,
                "endpoint_url": target.endpoint_url,
            },
            sampling_seed=seed,
            dataset_manifest={
                "total_sampled": sampled.total_sampled,
                "category_distribution": sampled.category_distribution,
            },
            judge_config={
                "provider": settings.JUDGE_PROVIDER,
                "model": settings.JUDGE_MODEL,
                **request.judge_profile,
            },
            scoring_version="aegis_v1.0",
            total_items=sampled.total_sampled,
            completed_items=0,
            failed_items=0,
            started_at=now,
        )
        self.db.add(job)
        self.db.flush()

        # 6. Create JobItem work checkpoints for each sampled test case
        for tc in sampled.test_cases:
            item = JobItem(
                id=uuid.uuid4(),
                job_id=job_id,
                test_case_id=tc.id,
                state=JobItemState.PENDING,
                attempt_count=0,
            )
            self.db.add(item)

        # 7. Record Idempotency Key
        if idempotency_key:
            expires_at = now + datetime.timedelta(days=1)
            idemp = IdempotencyKey(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                user_id=user_id,
                key=idempotency_key,
                request_hash=req_hash,
                resource_id=job_id,
                expires_at=expires_at,
            )
            self.db.add(idemp)

        # 8. Append AuditLog
        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="JOB_CREATED",
            resource_type="job",
            resource_id=job_id,
            request_id=request_id,
            metadata_payload={
                "target_id": str(request.target_id),
                "mode": request.mode.value,
                "total_items": sampled.total_sampled,
                "sampling_seed": seed,
            },
        )
        self.db.add(audit)

        self.db.commit()
        self.db.refresh(job)

        logger.info(
            f"Created evaluation job {job_id} for target {request.target_id} with {sampled.total_sampled} items in {request.mode.value} mode"
        )
        return self._format_job_response(job)

    def get_job(self, tenant_id: uuid.UUID, job_id: uuid.UUID) -> JobResponse:
        """Retrieve job progress and details with tenant verification."""
        job = self._verify_job_in_tenant(tenant_id, job_id)
        return self._format_job_response(job)

    def list_jobs(
        self,
        tenant_id: uuid.UUID,
        target_id: Optional[uuid.UUID] = None,
        state: Optional[JobState] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[JobResponse]:
        """List evaluation jobs for a tenant with optional target and state filters."""
        stmt = select(Job).where(Job.tenant_id == tenant_id)
        count_stmt = select(func.count(Job.id)).where(Job.tenant_id == tenant_id)

        if target_id:
            stmt = stmt.where(Job.target_id == target_id)
            count_stmt = count_stmt.where(Job.target_id == target_id)
        if state:
            stmt = stmt.where(Job.state == state)
            count_stmt = count_stmt.where(Job.state == state)

        total_estimate = self.db.scalar(count_stmt) or 0
        stmt = stmt.order_by(Job.created_at.desc()).offset(offset).limit(limit)
        jobs = list(self.db.scalars(stmt).all())

        return Page(
            items=[self._format_job_response(j) for j in jobs],
            total_estimate=total_estimate,
        )

    def cancel_job(
        self,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
        user_id: uuid.UUID,
        request_id: Optional[str] = None,
    ) -> JobResponse:
        """Cooperatively request job cancellation."""
        job = self._verify_job_in_tenant(tenant_id, job_id)

        if job.state in (JobState.COMPLETED, JobState.FAILED, JobState.CANCELLED):
            raise ValidationError(f"Cannot cancel job '{job_id}' in terminal state '{job.state.value}'.")

        now = datetime.datetime.now(datetime.timezone.utc)
        job.cancel_requested_at = now
        job.state = JobState.CANCELLED
        job.finished_at = now

        audit = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            actor_user_id=user_id,
            action="JOB_CANCELLED",
            resource_type="job",
            resource_id=job_id,
            request_id=request_id,
            metadata_payload={"cancelled_at": now.isoformat()},
        )
        self.db.add(audit)
        self.db.commit()
        self.db.refresh(job)

        logger.info(f"Cancelled evaluation job {job_id}")
        return self._format_job_response(job)

    def pause_job(
        self,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> JobResponse:
        """Set job state to PAUSED."""
        job = self._verify_job_in_tenant(tenant_id, job_id)
        if job.state != JobState.RUNNING:
            raise ValidationError(f"Can only pause running jobs. Current state: '{job.state.value}'")
        job.state = JobState.PAUSED
        self.db.commit()
        self.db.refresh(job)
        return self._format_job_response(job)

    def resume_job(
        self,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> JobResponse:
        """Resume a PAUSED evaluation job."""
        job = self._verify_job_in_tenant(tenant_id, job_id)
        if job.state != JobState.PAUSED:
            raise ValidationError(f"Can only resume paused jobs. Current state: '{job.state.value}'")
        job.state = JobState.RUNNING
        self.db.commit()
        self.db.refresh(job)
        return self._format_job_response(job)

    def get_job_results(
        self,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
        category: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        verdict: Optional[Verdict] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[TestResultResponse]:
        """Retrieve paginated test results and judge verdicts for an evaluation job."""
        self._verify_job_in_tenant(tenant_id, job_id)

        stmt = (
            select(TestResult)
            .options(joinedload(TestResult.test_case))
            .where(TestResult.job_id == job_id)
        )
        count_stmt = select(func.count(TestResult.id)).where(TestResult.job_id == job_id)

        if category:
            stmt = stmt.where(TestResult.category == category.upper())
            count_stmt = count_stmt.where(TestResult.category == category.upper())
        if severity:
            stmt = stmt.where(TestResult.severity == severity)
            count_stmt = count_stmt.where(TestResult.severity == severity)
        if verdict:
            stmt = stmt.where(TestResult.verdict == verdict)
            count_stmt = count_stmt.where(TestResult.verdict == verdict)

        total_estimate = self.db.scalar(count_stmt) or 0
        stmt = stmt.order_by(TestResult.created_at.asc()).offset(offset).limit(limit)
        results = list(self.db.scalars(stmt).unique().all())

        items = []
        for r in results:
            item = TestResultResponse.model_validate(r, from_attributes=True)
            if r.test_case:
                item.attack_prompt = r.test_case.prompt_template
            item.target_response = r.response_text
            item.response_text = r.response_text
            items.append(item)

        return Page(
            items=items,
            total_estimate=total_estimate,
        )

    list_job_results = get_job_results
