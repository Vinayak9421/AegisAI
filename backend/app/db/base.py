"""SQLAlchemy DeclarativeBase, naming conventions, and cross-dialect types."""

from sqlalchemy import JSON, MetaData, Uuid
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase

# Standard constraint naming conventions for clean Alembic migrations
POSTGRES_NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Cross-dialect JSONB type: compiles to native JSONB in PostgreSQL, standard JSON in SQLite
JSONBType = JSON().with_variant(JSONB, "postgresql")

# Cross-dialect UUID type: compiles to native UUID in PostgreSQL, CHAR(32) in SQLite
UUIDType = Uuid(as_uuid=True).with_variant(PG_UUID(as_uuid=True), "postgresql")


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    metadata = MetaData(naming_convention=POSTGRES_NAMING_CONVENTION)
