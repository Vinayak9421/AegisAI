"""Job and JobItem models."""

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
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.db.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import JobItemState, JobMode, JobState


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
