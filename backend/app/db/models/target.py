"""Target and TargetCredential models."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.db.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import CredentialKind, CredentialStatus, TargetMode, TargetStatus


class Target(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Registered authorized evaluation application."""

    __tablename__ = "targets"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_targets_tenant_name"),
        Index("ix_targets_tenant_status", "tenant_id", "status"),
    )

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    mode: Mapped[TargetMode] = mapped_column(
        SQLEnum(TargetMode, name="target_mode_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    endpoint_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    request_profile: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    capabilities: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    status: Mapped[TargetStatus] = mapped_column(
        SQLEnum(TargetStatus, name="target_status_enum", create_type=False, native_enum=False),
        default=TargetStatus.PENDING_VALIDATION,
        nullable=False,
    )
    authorization_confirmed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_validated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    configuration_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="targets")
    creator: Mapped["User"] = relationship("User", back_populates="created_targets")
    credentials: Mapped[List["TargetCredential"]] = relationship(
        "TargetCredential", back_populates="target", cascade="all, delete-orphan"
    )
    provenance_records: Mapped[List["ProvenanceRecord"]] = relationship(
        "ProvenanceRecord", back_populates="target", cascade="all, delete-orphan"
    )
    jobs: Mapped[List["Job"]] = relationship("Job", back_populates="target")


class TargetCredential(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Encrypted credential envelope for authenticated target connections."""

    __tablename__ = "target_credentials"

    target_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[CredentialKind] = mapped_column(
        SQLEnum(CredentialKind, name="credential_kind_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    ciphertext: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    key_version: Mapped[str] = mapped_column(String(64), nullable=False)
    secret_last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    status: Mapped[CredentialStatus] = mapped_column(
        SQLEnum(CredentialStatus, name="credential_status_enum", create_type=False, native_enum=False),
        default=CredentialStatus.ACTIVE,
        nullable=False,
    )
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    revoked_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    target: Mapped["Target"] = relationship("Target", back_populates="credentials")
