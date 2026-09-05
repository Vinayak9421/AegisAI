"""Base model mixins, UTC timestamps, and deterministic logical key generator."""

import datetime
import hashlib
import uuid
from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import UUIDType


class TimestampMixin:
    """Provides UTC created_at and updated_at timestamps."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """Provides UUID primary key generated application-side or via server default."""

    id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        primary_key=True,
        default=uuid.uuid4,
    )


def generate_logical_key(
    job_id: uuid.UUID,
    test_case_id: uuid.UUID,
    session_id: Optional[uuid.UUID] = None,
    turn_number: Optional[int] = None,
) -> str:
    """
    Computes deterministic SHA-256 logical identity for test results:
    sha256(job_id + ":" + test_case_id + ":" + normalized_session_id + ":" + normalized_turn_number)
    Guarantees AD-003 and Section B.2 deduplication requirement.
    """
    sess_str = str(session_id) if session_id else "NONE"
    turn_str = str(turn_number) if turn_number is not None else "0"
    raw_key = f"{job_id}:{test_case_id}:{sess_str}:{turn_str}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
