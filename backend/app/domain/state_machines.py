"""State machine transition definitions and validation helpers for Aegis AI."""

from typing import Dict, Set
from app.domain.enums import JobState, JobItemState, SessionState, CertificateStatus
from app.core.errors import ConflictError


JOB_TRANSITIONS: Dict[JobState, Set[JobState]] = {
    JobState.CREATED: {JobState.VALIDATING, JobState.CANCELLED, JobState.FAILED},
    JobState.VALIDATING: {JobState.QUEUED, JobState.CANCELLED, JobState.FAILED},
    JobState.QUEUED: {JobState.RUNNING, JobState.CANCELLED, JobState.FAILED},
    JobState.RUNNING: {
        JobState.PAUSING,
        JobState.AGGREGATING,
        JobState.CANCELLED,
        JobState.FAILED,
    },
    JobState.PAUSING: {JobState.PAUSED, JobState.CANCELLED, JobState.FAILED},
    JobState.PAUSED: {JobState.QUEUED, JobState.CANCELLED, JobState.FAILED},
    JobState.RECOVERING: {JobState.RUNNING, JobState.CANCELLED, JobState.FAILED},
    JobState.AGGREGATING: {JobState.CERTIFYING, JobState.CANCELLED, JobState.FAILED},
    JobState.CERTIFYING: {
        JobState.COMPLETED,
        JobState.COMPLETED_WITH_LIMITATIONS,
        JobState.FAILED,
    },
    JobState.COMPLETED: set(),
    JobState.COMPLETED_WITH_LIMITATIONS: set(),
    JobState.CANCELLED: set(),
    JobState.FAILED: {JobState.RECOVERING},  # only recoverable failed jobs can transition
}


JOB_ITEM_TRANSITIONS: Dict[JobItemState, Set[JobItemState]] = {
    JobItemState.PENDING: {JobItemState.LEASED, JobItemState.BLOCKED, JobItemState.FAILED},
    JobItemState.LEASED: {
        JobItemState.TARGET_RUNNING,
        JobItemState.RETRY_WAIT,
        JobItemState.BLOCKED,
        JobItemState.FAILED,
        JobItemState.PENDING,  # released on worker crash
    },
    JobItemState.TARGET_RUNNING: {
        JobItemState.TARGET_COMPLETE,
        JobItemState.RETRY_WAIT,
        JobItemState.BLOCKED,
        JobItemState.FAILED,
    },
    JobItemState.TARGET_COMPLETE: {
        JobItemState.JUDGING,
        JobItemState.COMPLETE,
        JobItemState.JUDGE_INVALID,
        JobItemState.FAILED,
    },
    JobItemState.JUDGING: {
        JobItemState.COMPLETE,
        JobItemState.JUDGE_INVALID,
        JobItemState.RETRY_WAIT,
        JobItemState.FAILED,
    },
    JobItemState.RETRY_WAIT: {JobItemState.PENDING, JobItemState.FAILED},
    JobItemState.COMPLETE: set(),
    JobItemState.BLOCKED: set(),
    JobItemState.FAILED: set(),
    JobItemState.JUDGE_INVALID: set(),
}


SESSION_TRANSITIONS: Dict[SessionState, Set[SessionState]] = {
    SessionState.PENDING: {SessionState.RUNNING, SessionState.BLOCKED, SessionState.FAILED},
    SessionState.RUNNING: {
        SessionState.PAUSED,
        SessionState.COMPLETED,
        SessionState.SAFE_TERMINATED,
        SessionState.HARM_DETECTED,
        SessionState.BLOCKED,
        SessionState.FAILED,
        SessionState.PARTIAL,
    },
    SessionState.PAUSED: {SessionState.RUNNING, SessionState.FAILED},
    SessionState.PARTIAL: {SessionState.RUNNING, SessionState.FAILED},
    SessionState.COMPLETED: set(),
    SessionState.SAFE_TERMINATED: set(),
    SessionState.HARM_DETECTED: set(),
    SessionState.BLOCKED: set(),
    SessionState.FAILED: set(),
}


CERTIFICATE_TRANSITIONS: Dict[CertificateStatus, Set[CertificateStatus]] = {
    CertificateStatus.GENERATING: {
        CertificateStatus.READY,
        CertificateStatus.FAILED,
    },
    CertificateStatus.READY: {
        CertificateStatus.SUPERSEDED,
    },
    CertificateStatus.FAILED: set(),
    CertificateStatus.SUPERSEDED: set(),
}


def validate_job_transition(current: JobState, target: JobState) -> None:
    allowed = JOB_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ConflictError(
            f"Invalid Job state transition from {current.value} to {target.value}"
        )


def validate_job_item_transition(current: JobItemState, target: JobItemState) -> None:
    allowed = JOB_ITEM_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ConflictError(
            f"Invalid JobItem state transition from {current.value} to {target.value}"
        )


def validate_session_transition(current: SessionState, target: SessionState) -> None:
    allowed = SESSION_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ConflictError(
            f"Invalid Session state transition from {current.value} to {target.value}"
        )
