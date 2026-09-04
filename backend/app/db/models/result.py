"""TestResult, ResultAttempt, and JudgeEvaluation models."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
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
from app.db.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import (
    AttemptPhase,
    AttemptStatus,
    JudgeStatus,
    SeverityLevel,
    TargetResponseStatus,
    Verdict,
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
    """Execution attempt log for connector or judge calls (separate from logical results)."""

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
