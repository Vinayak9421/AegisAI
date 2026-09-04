"""Alembic migrations integrity and revision chain tests."""

import os
from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic import command
import pytest

from app.db.base import Base


def test_alembic_migration_revision_chain():
    """Verify that Alembic migrations form a continuous, valid chain."""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    alembic_cfg = Config(os.path.join(backend_dir, "alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))

    script = ScriptDirectory.from_config(alembic_cfg)
    heads = script.get_heads()
    
    assert len(heads) == 1
    assert heads[0] == "0001_initial_phase1"


def test_all_models_registered_in_metadata():
    """Verify that all Phase 1 domain tables are present in SQLAlchemy metadata."""
    expected_tables = {
        "tenants",
        "users",
        "auth_sessions",
        "targets",
        "target_credentials",
        "provenance_records",
        "benchmark_sources",
        "test_cases",
        "jobs",
        "sessions",
        "job_items",
        "session_turns",
        "test_results",
        "result_attempts",
        "judge_evaluations",
        "trace_results",
        "trace_stages",
        "certificates",
        "audit_logs",
        "idempotency_keys",
    }
    registered_tables = set(Base.metadata.tables.keys())
    missing = expected_tables - registered_tables
    assert not missing, f"Missing tables in Base.metadata: {missing}"
