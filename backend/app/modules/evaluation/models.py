"""Evaluation database models: Job, JobItem, TestResult, ResultAttempt, JudgeEvaluation, Session, SessionTurn, TraceResult, TraceStage."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.db.base_class import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import (
    AttemptPhase,
    AttemptStatus,
    JobItemState,
    JobMode,
    JobState,
    JudgeStatus,
    SessionState,
    SeverityLevel,
    TargetResponseStatus,
    TraceAvailability,
    TraceStageStatus,
    TraceStageType,
    TurnRole,
    TurnState,
    Verdict,
)


class Job(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable evaluation run request and lifecycle controller."""

    __tablename__ = "jobs"
    __table_args__ = (
        Index("ix_jobs_tenant_state", "tenant_id", "state"),
        CheckConstraint("total_items >= 0", name="ck_jobs_total_items_nonnegative"),
        CheckConstraint("completed_items >= 0", name="ck_jobs_completed_items_nonnegative"),
        CheckConstraint("failed_items >= 0", name="ck_jobs_failed_items_nonnegative"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    mode: Mapped[JobMode] = mapped_column(
        SQLEnum(JobMode, name="job_mode_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    state: Mapped[JobState] = mapped_column(
        SQLEnum(JobState, name="job_state_enum", create_type=False, native_enum=False),
        default=JobState.CREATED,
        nullable=False,
    )
    config_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    sampling_seed: Mapped[int] = mapped_column(BigInteger, nullable=False)
    dataset_manifest: Mapped[Dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    judge_config: Mapped[Dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    scoring_version: Mapped[str] = mapped_column(String(32), nullable=False)
    total_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed_items: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cancel_requested_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONBType, nullable=True)

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="jobs")
    target: Mapped["Target"] = relationship("Target", back_populates="jobs")
    creator: Mapped["User"] = relationship("User", back_populates="created_jobs")
    job_items: Mapped[List["JobItem"]] = relationship(
        "JobItem", back_populates="job", cascade="all, delete-orphan"
    )
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="job", cascade="all, delete-orphan"
    )
    results: Mapped[List["TestResult"]] = relationship(
        "TestResult", back_populates="job", cascade="all, delete-orphan"
    )
    certificates: Mapped[List["Certificate"]] = relationship(
        "Certificate", back_populates="job", cascade="all, delete-orphan"
    )


class JobItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Durable logical work checkpoint per job, test case, or session turn."""

    __tablename__ = "job_items"
    __table_args__ = (
        Index("ix_job_items_queue", "job_id", "state", "next_retry_at"),
        Index("ix_job_items_lease", "state", "lease_expires_at"),
        CheckConstraint("attempt_count >= 0", name="ck_job_items_attempt_count_nonnegative"),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    turn_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    state: Mapped[JobItemState] = mapped_column(
        SQLEnum(JobItemState, name="job_item_state_enum", create_type=False, native_enum=False),
        default=JobItemState.PENDING,
        nullable=False,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lease_owner: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    lease_expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    next_retry_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_error: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONBType, nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="job_items")
    test_case: Mapped["TestCase"] = relationship("TestCase", back_populates="job_items")
    session: Mapped[Optional["Session"]] = relationship("Session", back_populates="job_items")
    test_result: Mapped[Optional["TestResult"]] = relationship(
        "TestResult", back_populates="job_item", uselist=False
    )
    attempts: Mapped[List["ResultAttempt"]] = relationship(
        "ResultAttempt", back_populates="job_item", cascade="all, delete-orphan"
    )


class TestResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Deterministic logical evaluation result after connector execution and judging."""

    __tablename__ = "test_results"
    __table_args__ = (
        UniqueConstraint("logical_key", name="uq_test_results_logical_key"),
        Index("ix_test_results_job_lookup", "job_id", "category", "severity"),
        Index("ix_test_results_session", "session_id", "turn_number"),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_item_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("job_items.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    turn_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    target_status: Mapped[TargetResponseStatus] = mapped_column(
        SQLEnum(TargetResponseStatus, name="target_response_status_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    response_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    judge_status: Mapped[JudgeStatus] = mapped_column(
        SQLEnum(JudgeStatus, name="judge_status_enum", create_type=False, native_enum=False),
        default=JudgeStatus.PENDING,
        nullable=False,
        index=True,
    )
    verdict: Mapped[Optional[Verdict]] = mapped_column(
        SQLEnum(Verdict, name="verdict_enum", create_type=False, native_enum=False),
        nullable=True,
    )
    severity: Mapped[Optional[SeverityLevel]] = mapped_column(
        SQLEnum(SeverityLevel, name="severity_level_enum", create_type=False, native_enum=False),
        nullable=True,
    )
    category: Mapped[Optional[str]] = mapped_column(String(80), nullable=True, index=True)
    owasp_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    rubric_version: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    judge_model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    logical_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="results")
    job_item: Mapped["JobItem"] = relationship("JobItem", back_populates="test_result")
    test_case: Mapped["TestCase"] = relationship("TestCase")
    session: Mapped[Optional["Session"]] = relationship("Session", back_populates="results")
    judge_evaluations: Mapped[List["JudgeEvaluation"]] = relationship(
        "JudgeEvaluation", back_populates="test_result", cascade="all, delete-orphan"
    )
    trace_result: Mapped[Optional["TraceResult"]] = relationship(
        "TraceResult", back_populates="test_result", uselist=False, cascade="all, delete-orphan"
    )


class ResultAttempt(Base, UUIDPrimaryKeyMixin):
    """Execution attempt log for connector or judge calls."""

    __tablename__ = "result_attempts"
    __table_args__ = (
        UniqueConstraint("job_item_id", "attempt_no", "phase", name="uq_result_attempts_item_attempt_phase"),
    )

    job_item_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("job_items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    phase: Mapped[AttemptPhase] = mapped_column(
        SQLEnum(AttemptPhase, name="attempt_phase_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    status: Mapped[AttemptStatus] = mapped_column(
        SQLEnum(AttemptStatus, name="attempt_status_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    provider_request_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_class: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    error_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONBType, nullable=True)
    started_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    finished_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    job_item: Mapped["JobItem"] = relationship("JobItem", back_populates="attempts")


class JudgeEvaluation(Base, UUIDPrimaryKeyMixin):
    """Normalized output from an independent judge."""

    __tablename__ = "judge_evaluations"
    __table_args__ = (
        UniqueConstraint("test_result_id", "judge_model", "rubric_version", name="uq_judge_eval_result_model_rubric"),
    )

    test_result_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("test_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    judge_model: Mapped[str] = mapped_column(String(128), nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(64), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    verdict: Mapped[Verdict] = mapped_column(
        SQLEnum(Verdict, name="verdict_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    severity: Mapped[SeverityLevel] = mapped_column(
        SQLEnum(SeverityLevel, name="severity_level_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    category: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    owasp_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    raw_output_ref: Mapped[Optional[uuid.UUID]] = mapped_column(UUIDType, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    test_result: Mapped["TestResult"] = relationship("TestResult", back_populates="judge_evaluations")


class Session(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Multi-turn evaluation state container."""

    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_job_state", "job_id", "state"),
        CheckConstraint("current_turn >= 0", name="ck_sessions_current_turn_nonnegative"),
        CheckConstraint("max_turns >= 0", name="ck_sessions_max_turns_nonnegative"),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    test_case_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    state: Mapped[SessionState] = mapped_column(
        SQLEnum(SessionState, name="session_state_enum", create_type=False, native_enum=False),
        default=SessionState.PENDING,
        nullable=False,
    )
    script_version: Mapped[str] = mapped_column(String(64), nullable=False)
    current_turn: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_turns: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    history_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    termination_reason: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="sessions")
    target: Mapped["Target"] = relationship("Target")
    test_case: Mapped["TestCase"] = relationship("TestCase")
    job_items: Mapped[List["JobItem"]] = relationship("JobItem", back_populates="session")
    turns: Mapped[List["SessionTurn"]] = relationship(
        "SessionTurn", back_populates="session", cascade="all, delete-orphan"
    )
    results: Mapped[List["TestResult"]] = relationship("TestResult", back_populates="session")


class SessionTurn(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable per-turn evidence within a multi-turn evaluation session."""

    __tablename__ = "session_turns"
    __table_args__ = (
        UniqueConstraint("session_id", "turn_number", name="uq_session_turns_turn_number"),
        CheckConstraint("turn_number > 0", name="ck_session_turns_positive_turn"),
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[TurnRole] = mapped_column(
        SQLEnum(TurnRole, name="turn_role_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    history_before_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    history_after_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    response_ref: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        nullable=True,
    )
    state: Mapped[TurnState] = mapped_column(
        SQLEnum(TurnState, name="turn_state_enum", create_type=False, native_enum=False),
        default=TurnState.PENDING,
        nullable=False,
    )

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="turns")


class TraceResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Captured agent execution trace metadata and quality assessment."""

    __tablename__ = "trace_results"

    test_result_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("test_results.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    trace_id: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    availability: Mapped[TraceAvailability] = mapped_column(
        SQLEnum(TraceAvailability, name="trace_availability_enum", create_type=False, native_enum=False),
        default=TraceAvailability.AVAILABLE,
        nullable=False,
    )
    schema_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    raw_trace_ref: Mapped[Optional[uuid.UUID]] = mapped_column(UUIDType, nullable=True)
    quality_flags: Mapped[List[str]] = mapped_column(
        JSONBType,
        default=list,
        nullable=False,
    )

    # Relationships
    test_result: Mapped["TestResult"] = relationship("TestResult", back_populates="trace_result")
    stages: Mapped[List["TraceStage"]] = relationship(
        "TraceStage", back_populates="trace_result", cascade="all, delete-orphan"
    )


class TraceStage(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Granular intermediate reasoning, retrieval, or tool execution stage within a trace."""

    __tablename__ = "trace_stages"
    __table_args__ = (
        UniqueConstraint("trace_result_id", "stage_index", name="uq_trace_stages_index"),
        Index("ix_trace_stages_lookup", "trace_result_id", "stage_index"),
    )

    trace_result_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("trace_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    stage_index: Mapped[int] = mapped_column(Integer, nullable=False)
    stage_type: Mapped[TraceStageType] = mapped_column(
        SQLEnum(TraceStageType, name="trace_stage_type_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    stage_status: Mapped[TraceStageStatus] = mapped_column(
        SQLEnum(TraceStageStatus, name="trace_stage_status_enum", create_type=False, native_enum=False),
        default=TraceStageStatus.SUCCESS,
        nullable=False,
    )
    input_ref: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    output_ref: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tool_metadata: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    judge_status: Mapped[JudgeStatus] = mapped_column(
        SQLEnum(JudgeStatus, name="judge_status_enum", create_type=False, native_enum=False),
        default=JudgeStatus.PENDING,
        nullable=False,
    )
    verdict: Mapped[Optional[Verdict]] = mapped_column(
        SQLEnum(Verdict, name="verdict_enum", create_type=False, native_enum=False),
        nullable=True,
    )
    severity: Mapped[Optional[SeverityLevel]] = mapped_column(
        SQLEnum(SeverityLevel, name="severity_level_enum", create_type=False, native_enum=False),
        nullable=True,
    )
    owasp_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    trace_result: Mapped["TraceResult"] = relationship("TraceResult", back_populates="stages")
