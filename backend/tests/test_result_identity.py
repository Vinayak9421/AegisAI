"""Deterministic result identity and uniqueness tests.

Validates AD-003 and Section B.2:
A unique logical key (job_id, test_case_id, session_id, turn_number)
prevents duplicate logical results while allowing multiple result_attempts.
"""

import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import app.db.models as models
from app.db.models.base import generate_logical_key
from app.domain.enums import (
    AttemptPhase,
    AttemptStatus,
    JobItemState,
    JudgeStatus,
    SeverityLevel,
    TargetResponseStatus,
    Verdict,
)


def test_deterministic_result_identity_prevents_duplicate_test_results(
    db_session: Session,
    sample_job: models.Job,
    sample_test_case: models.TestCase,
):
    # Create work item
    job_item = models.JobItem(
        id=uuid.uuid4(),
        job_id=sample_job.id,
        test_case_id=sample_test_case.id,
        turn_number=1,
        state=JobItemState.COMPLETE,
    )
    db_session.add(job_item)
    db_session.commit()

    # Generate deterministic logical key
    logical_key = generate_logical_key(
        job_id=sample_job.id,
        test_case_id=sample_test_case.id,
        session_id=None,
        turn_number=1,
    )

    # Insert first result
    result1 = models.TestResult(
        id=uuid.uuid4(),
        job_id=sample_job.id,
        job_item_id=job_item.id,
        test_case_id=sample_test_case.id,
        turn_number=1,
        target_status=TargetResponseStatus.SUCCESS,
        response_text="I cannot provide direct stock picks as I am an AI assistant.",
        judge_status=JudgeStatus.JUDGED,
        verdict=Verdict.SAFE,
        severity=SeverityLevel.NONE,
        logical_key=logical_key,
    )
    db_session.add(result1)
    db_session.commit()

    # Attempt to insert second logical result with identical (job_id, test_case_id, session_id, turn_number)
    duplicate_item = models.JobItem(
        id=uuid.uuid4(),
        job_id=sample_job.id,
        test_case_id=sample_test_case.id,
        turn_number=1,
        state=JobItemState.COMPLETE,
    )
    db_session.add(duplicate_item)
    db_session.commit()

    result2 = models.TestResult(
        id=uuid.uuid4(),
        job_id=sample_job.id,
        job_item_id=duplicate_item.id,
        test_case_id=sample_test_case.id,
        turn_number=1,
        target_status=TargetResponseStatus.SUCCESS,
        response_text="A retry outcome",
        judge_status=JudgeStatus.JUDGED,
        verdict=Verdict.SAFE,
        severity=SeverityLevel.NONE,
        logical_key=logical_key,  # Duplicate logical key
    )
    db_session.add(result2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_multiple_attempts_allowed_for_single_job_item(
    db_session: Session,
    sample_job: models.Job,
    sample_test_case: models.TestCase,
):
    job_item = models.JobItem(
        id=uuid.uuid4(),
        job_id=sample_job.id,
        test_case_id=sample_test_case.id,
        state=JobItemState.RETRY_WAIT,
    )
    db_session.add(job_item)
    db_session.commit()

    # Attempt 1: Failed with timeout
    attempt1 = models.ResultAttempt(
        id=uuid.uuid4(),
        job_item_id=job_item.id,
        attempt_no=1,
        phase=AttemptPhase.TARGET,
        status=AttemptStatus.TIMEOUT,
        error_class="timeout",
    )
    db_session.add(attempt1)

    # Attempt 2: Succeeded
    attempt2 = models.ResultAttempt(
        id=uuid.uuid4(),
        job_item_id=job_item.id,
        attempt_no=2,
        phase=AttemptPhase.TARGET,
        status=AttemptStatus.SUCCESS,
    )
    db_session.add(attempt2)
    db_session.commit()

    db_session.refresh(job_item)
    assert len(job_item.attempts) == 2
    assert {a.attempt_no for a in job_item.attempts} == {1, 2}
