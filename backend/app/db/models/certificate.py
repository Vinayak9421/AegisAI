"""Certificate model representing immutable trust and safety evaluation reports."""

import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.db.base_class import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import CertificateStatus


class Certificate(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable Trust & Safety Certificate report projection."""

    __tablename__ = "certificates"
    __table_args__ = (
        UniqueConstraint("job_id", "version", name="uq_certificates_job_version"),
        Index("ix_certificates_job_version", "job_id", "version"),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    certificate_number: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    status: Mapped[CertificateStatus] = mapped_column(
        SQLEnum(CertificateStatus, name="certificate_status_enum", create_type=False, native_enum=False),
        default=CertificateStatus.GENERATING,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    identity_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    trust_score: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    aer: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    shr: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    cmr: Mapped[Optional[float]] = mapped_column(Numeric(6, 2), nullable=True)
    coverage_summary: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    category_breakdown: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    failures: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSONBType,
        default=list,
        nullable=False,
    )
    recommendations: Mapped[List[str]] = mapped_column(
        JSONBType,
        default=list,
        nullable=False,
    )
    limitations: Mapped[List[str]] = mapped_column(
        JSONBType,
        default=list,
        nullable=False,
    )
    formula_versions: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    export_ref: Mapped[Optional[uuid.UUID]] = mapped_column(UUIDType, nullable=True)

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="certificates")
