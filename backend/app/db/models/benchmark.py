"""BenchmarkSource and TestCase models."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, JSONBType, UUIDType
from app.db.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from app.domain.enums import (
    BenchmarkSourceStatus,
    BenchmarkSourceType,
    ReviewStatus,
    SeverityLevel,
    TestCaseMode,
)


class BenchmarkSource(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Immutable dataset or domain benchmark manifest."""

    __tablename__ = "benchmark_sources"
    __table_args__ = (
        UniqueConstraint("source_type", "revision", name="uq_benchmark_source_revision"),
    )

    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUIDType,
        ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[BenchmarkSourceType] = mapped_column(
        SQLEnum(BenchmarkSourceType, name="benchmark_source_type_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    external_ref: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    revision: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    license_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manifest_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    status: Mapped[BenchmarkSourceStatus] = mapped_column(
        SQLEnum(BenchmarkSourceStatus, name="benchmark_source_status_enum", create_type=False, native_enum=False),
        default=BenchmarkSourceStatus.APPROVED,
        nullable=False,
    )

    # Relationships
    test_cases: Mapped[List["TestCase"]] = relationship(
        "TestCase", back_populates="source", cascade="all, delete-orphan"
    )


class TestCase(Base, UUIDPrimaryKeyMixin):
    """Immutable curated/reviewed test prompt or scripted session root."""

    __tablename__ = "test_cases"
    __table_args__ = (
        UniqueConstraint("source_id", "content_hash", name="uq_test_cases_source_content_hash"),
        UniqueConstraint("source_id", "external_case_ref", name="uq_test_cases_source_external_ref"),
        Index("ix_test_cases_category", "category"),
    )

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUIDType,
        ForeignKey("benchmark_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    external_case_ref: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    subcategory: Mapped[str] = mapped_column(String(80), nullable=False)
    mode: Mapped[TestCaseMode] = mapped_column(
        SQLEnum(TestCaseMode, name="test_case_mode_enum", create_type=False, native_enum=False),
        default=TestCaseMode.SINGLE,
        nullable=False,
    )
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    variables_schema: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType,
        default=dict,
        nullable=False,
    )
    session_script: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONBType, nullable=True)
    owasp_ids: Mapped[List[str]] = mapped_column(
        JSONBType,
        default=list,
        nullable=False,
    )
    severity_ceiling: Mapped[SeverityLevel] = mapped_column(
        SQLEnum(SeverityLevel, name="severity_level_enum", create_type=False, native_enum=False),
        nullable=False,
    )
    review_status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus, name="review_status_enum", create_type=False, native_enum=False),
        default=ReviewStatus.APPROVED,
        nullable=False,
        index=True,
    )
    language: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    metadata_payload: Mapped[Dict[str, Any]] = mapped_column(
        "metadata",
        JSONBType,
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    source: Mapped["BenchmarkSource"] = relationship("BenchmarkSource", back_populates="test_cases")
    job_items: Mapped[List["JobItem"]] = relationship("JobItem", back_populates="test_case")
