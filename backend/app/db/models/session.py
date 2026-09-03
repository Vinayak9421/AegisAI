"""Session and SessionTurn models for multi-turn evaluations."""

import uuid
from typing import List, Optional
from sqlalchemy import (
    CheckConstraint,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, UUIDType
from app.db.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import SessionState, TurnRole, TurnState


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
    termination_reason: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

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
