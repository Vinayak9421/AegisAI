"""ProvenanceRecord database model."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.db.models.base import UUIDPrimaryKeyMixin


class ProvenanceRecord(Base, UUIDPrimaryKeyMixin):
    """Immutable versioned declared provenance and calculated Identity Score."""

    __tablename__ = "provenance_records"
    __table_args__ = (
        UniqueConstraint("target_id", "version", name="uq_provenance_target_version"),
    )

    target_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    model_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    data_sources: Mapped[Dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    system_prompt_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    operational_metadata: Mapped[Dict[str, Any]] = mapped_column(JSONBType, nullable=False)
    evidence_refs: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONBType,
        default=list,
        nullable=False,
    )
    identity_score: Mapped[Optional[float]] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )
    score_version: Mapped[str] = mapped_column(String(32), nullable=False)
    quality_flags: Mapped[List[str]] = mapped_column(
        JSONBType,
        default=list,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id"),
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    # Relationships
    target: Mapped["Target"] = relationship("Target", back_populates="provenance_records")
    creator: Mapped["User"] = relationship("User")
