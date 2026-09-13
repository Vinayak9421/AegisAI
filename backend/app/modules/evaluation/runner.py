"""Evaluation worker runner executing target dispatch, independent judging, and checkpoint persistence."""

import asyncio
import datetime
import time
from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.connectors.factory import ConnectorFactory
from app.core.config import settings
from app.core.logging import logger
from app.db.base_class import generate_logical_key
from app.domain.contracts import ConnectorRequest, JudgeInput
from app.domain.enums import (
    AttemptPhase,
    AttemptStatus,
    JobItemState,
    JobState,
    JudgeStatus,
    SeverityLevel,
    TargetResponseStatus,
    Verdict,
)
from app.judging.router import judge_router
from app.modules.evaluation.models import Job, JobItem, JudgeEvaluation, ResultAttempt, TestResult
from app.modules.targets.models import Target
from app.services.credential_service import CredentialService


class EvaluationRunner:
    """Orchestrates execution of single-turn attack test cases and independent judging."""

    def __init__(self, db: Session):
        self.db = db
        self.credential_service = CredentialService(db)

    async def execute_item(self, item_id: uuid.UUID) -> Optional[TestResult]:
        """
        Execute a single JobItem work unit:
        1. Dispatches attack prompt to target application via connector.
        2. Routes response to independent LLM judge.
        3. Persists attempts, test result, and judge evaluation atomically.
        """
        item = self.db.get(JobItem, item_id)
        if not item or item.state == JobItemState.COMPLETE:
            return None

        job = item.job
        target = job.target
        test_case = item.test_case

        # 1. Check for cancellation request
        if job.cancel_requested_at:
            item.state = JobItemState.FAILED
            item.last_error = {"reason": "Job cancelled by user"}
            job.state = JobState.CANCELLED
            self.db.commit()
            return None

        # 2. Update item state to TARGET_RUNNING
        item.state = JobItemState.TARGET_RUNNING
        item.attempt_count += 1
        self.db.commit()

        now = datetime.datetime.now(datetime.timezone.utc)
        target_status = TargetResponseStatus.SUCCESS
        response_text = ""
        response_metadata = {}
        target_error = None

        # 3. Phase A: Invoke Target Connector
        start_time = time.perf_counter()
        attempt_1_id = uuid.uuid4()
        try:
            # Resolve target decrypted credentials in memory
            decrypted_cred = self.credential_service.get_active_credential_decrypted(target.id)
            connector = ConnectorFactory.get_connector(
                target=target,
                decrypted_credential=decrypted_cred,
            )

            req = ConnectorRequest(
                target_id=str(target.id),
                request_id=str(uuid.uuid4()),
                message=test_case.prompt_template,
                ordered_history=[],
                timeout_budget_ms=int(settings.TARGET_READ_TIMEOUT * 1000),
                response_size_budget_bytes=settings.TARGET_MAX_RESPONSE_BYTES,
            )
            connector_resp = await connector.invoke(req)
            response_text = connector_resp.text or ""
            response_metadata = connector_resp.usage_metadata or {}
            target_attempt_status = AttemptStatus.SUCCESS
        except Exception as e:
            logger.warning(f"Target execution failed for item {item.id}: {e}")
            target_status = TargetResponseStatus.ERROR
            target_error = str(e)
            response_text = f"ERROR: Target failed: {type(e).__name__} - {str(e)}"
            target_attempt_status = AttemptStatus.HARD_FAILURE

        duration_target_ms = int((time.perf_counter() - start_time) * 1000)

        # Record Phase A attempt
        attempt_target = ResultAttempt(
            id=attempt_1_id,
            job_item_id=item.id,
            attempt_no=item.attempt_count,
            phase=AttemptPhase.TARGET,
            status=target_attempt_status,
            error_class=type(target_error).__name__ if target_error else None,
            started_at=now,
            finished_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self.db.add(attempt_target)
        item.state = JobItemState.TARGET_COMPLETE
        self.db.commit()

        # 4. Phase B: Invoke Independent Judge
        item.state = JobItemState.JUDGING
        self.db.commit()

        judge_provider_name = job.judge_config.get("provider", settings.JUDGE_PROVIDER)
        judge = judge_router.get_judge(judge_provider_name)

        judge_in = JudgeInput(
            target_response=response_text,
            test_case_prompt=test_case.prompt_template,
            category=test_case.category,
            intent=test_case.subcategory,
            rubric_version="financial_safety_v1.0",
        )

        judge_start = time.perf_counter()
        attempt_2_id = uuid.uuid4()
        try:
            judge_out = await judge.evaluate(judge_in)
            judge_attempt_status = AttemptStatus.SUCCESS
            judge_status = JudgeStatus.JUDGED
        except Exception as e:
            logger.error(f"Judge execution failed for item {item.id}: {e}")
            judge_attempt_status = AttemptStatus.HARD_FAILURE
            judge_status = JudgeStatus.JUDGE_INVALID
            judge_out = None

        duration_judge_ms = int((time.perf_counter() - judge_start) * 1000)

        # Record Phase B attempt
        attempt_judge = ResultAttempt(
            id=attempt_2_id,
            job_item_id=item.id,
            attempt_no=item.attempt_count,
            phase=AttemptPhase.JUDGE,
            status=judge_attempt_status,
            started_at=datetime.datetime.now(datetime.timezone.utc),
            finished_at=datetime.datetime.now(datetime.timezone.utc),
        )
        self.db.add(attempt_judge)

        # 5. Phase C: Atomically commit Logical Result and Judge Evaluation
        logical_key = generate_logical_key(
            job_id=job.id,
            test_case_id=test_case.id,
            session_id=item.session_id,
            turn_number=item.turn_number,
        )

        # Check for existing result (deterministic idempotency AD-003)
        stmt_res = select(TestResult).where(TestResult.logical_key == logical_key)
        existing_res = self.db.scalars(stmt_res).first()

        verdict_val = None
        severity_val = None
        rationale_val = None
        confidence_val = None

        if judge_out:
            try:
                verdict_val = Verdict(judge_out.verdict)
            except Exception:
                verdict_val = Verdict.AMBIGUOUS
            try:
                severity_val = SeverityLevel(judge_out.severity)
            except Exception:
                severity_val = SeverityLevel.NONE
            rationale_val = judge_out.rationale
            confidence_val = judge_out.confidence

        if not existing_res:
            test_result = TestResult(
                id=uuid.uuid4(),
                job_id=job.id,
                job_item_id=item.id,
                test_case_id=test_case.id,
                session_id=item.session_id,
                turn_number=item.turn_number,
                target_status=target_status,
                response_text=response_text,
                response_metadata=response_metadata,
                judge_status=judge_status,
                verdict=verdict_val,
                severity=severity_val,
                category=test_case.category,
                owasp_id=test_case.owasp_ids[0] if test_case.owasp_ids else None,
                rationale=rationale_val,
                confidence=confidence_val,
                rubric_version=judge_out.rubric_version if judge_out else "1.0.0",
                judge_model=settings.JUDGE_MODEL,
                logical_key=logical_key,
            )
            self.db.add(test_result)
            self.db.flush()
        else:
            test_result = existing_res
            test_result.response_text = response_text
            test_result.verdict = verdict_val
            test_result.severity = severity_val
            test_result.rationale = rationale_val
            test_result.confidence = confidence_val
            self.db.flush()

        # Add JudgeEvaluation entity
        if judge_out:
            eval_entity = JudgeEvaluation(
                id=uuid.uuid4(),
                test_result_id=test_result.id,
                judge_model=settings.JUDGE_MODEL,
                rubric_version=judge_out.rubric_version,
                schema_version=judge_out.schema_version,
                verdict=verdict_val,
                severity=severity_val,
                category=test_case.category,
                owasp_id=test_result.owasp_id,
                rationale=rationale_val or "Evaluated",
                confidence=confidence_val,
            )
            self.db.add(eval_entity)

        # 6. Update JobItem and Job progress counters
        if target_status == TargetResponseStatus.SUCCESS:
            item.state = JobItemState.COMPLETE
            job.completed_items += 1
        else:
            item.state = JobItemState.FAILED
            item.last_error = {"error": target_error}
            job.failed_items += 1

        # Check if job is finished
        if (job.completed_items + job.failed_items) >= job.total_items:
            job.state = JobState.COMPLETED
            job.finished_at = datetime.datetime.now(datetime.timezone.utc)

        self.db.commit()
        return test_result

    async def run_all_pending_items_for_job(self, job_id: uuid.UUID) -> Job:
        """Execute all pending work items for a job sequentially to completion."""
        job = self.db.get(Job, job_id)
        if not job:
            return None

        # Transition to RUNNING
        if job.state in (JobState.CREATED, JobState.QUEUED):
            job.state = JobState.RUNNING
            self.db.commit()

        stmt = (
            select(JobItem.id)
            .where(
                JobItem.job_id == job_id,
                JobItem.state.in_([JobItemState.PENDING, JobItemState.LEASED]),
            )
            .order_by(JobItem.created_at.asc())
        )
        item_ids = list(self.db.scalars(stmt).all())

        target = job.target
        rpm = target.rate_limit_requests_per_minute if target and target.rate_limit_requests_per_minute else 12
        # Bound pacing delay to at least 2.5s to prevent burst exhaustion against Groq/judge rate limits
        pacing_delay = max(round(60.0 / max(rpm, 1), 1), 2.5)

        logger.info(
            f"Running evaluation execution loop for job {job_id} "
            f"({len(item_ids)} pending items, target RPM: {rpm}, pacing delay: {pacing_delay}s)"
        )
        for idx, i_id in enumerate(item_ids):
            # Check if cancellation requested
            self.db.refresh(job)
            if job.cancel_requested_at:
                job.state = JobState.CANCELLED
                job.finished_at = datetime.datetime.now(datetime.timezone.utc)
                self.db.commit()
                break

            # Sleep between requests to avoid exceeding target rate limits (e.g. Gemini 15 RPM)
            if idx > 0 and pacing_delay > 0:
                await asyncio.sleep(pacing_delay)

            await self.execute_item(i_id)

        self.db.refresh(job)
        return job
