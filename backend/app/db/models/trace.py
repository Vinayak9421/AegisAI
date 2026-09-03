"""TraceResult and TraceStage models for agentic intermediate reasoning and tool invocation evaluation."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.db.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import (
    JudgeStatus,
    SeverityLevel,
    TraceAvailability,
    TraceStageStatus,
    TraceStageType,
    Verdict,
)


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
