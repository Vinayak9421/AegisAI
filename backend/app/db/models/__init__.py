"""Consolidated ORM models export for application code and Alembic migrations."""

from app.db.base import Base
from app.db.models.base import TimestampMixin, UUIDPrimaryKeyMixin, generate_logical_key
from app.db.models.tenant import Tenant, User, AuthSession
from app.db.models.target import Target, TargetCredential
from app.db.models.provenance import ProvenanceRecord
from app.db.models.benchmark import BenchmarkSource, TestCase
from app.db.models.job import Job, JobItem
from app.db.models.session import Session, SessionTurn
from app.db.models.result import TestResult, ResultAttempt, JudgeEvaluation
from app.db.models.trace import TraceResult, TraceStage
from app.db.models.certificate import Certificate
from app.db.models.audit import AuditLog
from app.db.models.idempotency import IdempotencyKey

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "generate_logical_key",
    "Tenant",
    "User",
    "AuthSession",
    "Target",
    "TargetCredential",
    "ProvenanceRecord",
    "BenchmarkSource",
    "TestCase",
    "Job",
    "JobItem",
    "Session",
    "SessionTurn",
    "TestResult",
    "ResultAttempt",
    "JudgeEvaluation",
    "TraceResult",
    "TraceStage",
    "Certificate",
    "AuditLog",
    "IdempotencyKey",
]
