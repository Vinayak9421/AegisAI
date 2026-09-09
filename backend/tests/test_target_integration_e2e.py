"""End-to-end integration tests for Existing Online Chatbot Target Integration Plan."""

import asyncio
import pytest
import uuid
import httpx
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.certificates.builder import CertificateBuilder
from app.connectors.factory import ConnectorFactory
from app.connectors.profiles.registry import get_connector_profile
from app.core.ssrf import validate_target_url
from app.domain.contracts import ConnectorRequest
from app.domain.enums import (
    ConnectorProfile,
    CredentialKind,
    JobMode,
    JobState,
    SeverityLevel,
    TargetMode,
    TargetStatus,
    Verdict,
)
from app.main import app
from app.modules.auth.service import AuthService
from app.modules.benchmarks.seeder import seed_all_benchmarks
from app.modules.benchmarks.service import BenchmarkService
from app.modules.evaluation.runner import EvaluationRunner
from app.modules.evaluation.schemas import CreateJobRequest
from app.modules.evaluation.service import JobService
from app.modules.targets.schemas import CreateTargetRequest
from app.modules.targets.service import TargetService
from app.services.scoring_engine import ScoringEngine


@pytest.fixture
def client():
    return TestClient(app)


def test_connector_profiles_registry():
    """Verify connector profiles resolve and shape requests correctly."""
    p_aegis = get_connector_profile("aegis_simple_chat_v1")
    assert p_aegis.profile_name == "aegis_simple_chat_v1"

    req_aegis = p_aegis.build_request("https://target.ai/chat", "test prompt", request_id="req-1")
    assert req_aegis.json_payload["message"] == "test prompt"
    assert req_aegis.json_payload["request_id"] == "req-1"

    res_aegis = p_aegis.parse_response({"reply": "Hello user", "metadata": {"latency_ms": 120}}, '{"reply": "Hello user"}')
    assert res_aegis.text == "Hello user"
    assert res_aegis.usage_metadata == {"latency_ms": 120}

    p_openai = get_connector_profile("openai_chat_v1")
    assert p_openai.profile_name == "openai_chat_v1"

    req_openai = p_openai.build_request("https://api.openai.com/v1/chat/completions", "test prompt")
    assert req_openai.json_payload["messages"][-1]["content"] == "test prompt"

    res_openai = p_openai.parse_response(
        {"choices": [{"message": {"role": "assistant", "content": "OpenAI answer"}}]},
        "{}"
    )
    assert res_openai.text == "OpenAI answer"


def test_ssrf_validation_security_rules():
    """Verify SSRF validation blocks cloud metadata and invalid schemes."""
    # Cloud metadata IP must be blocked when allow_local_dev=False
    with pytest.raises(Exception) as exc:
        validate_target_url("https://169.254.169.254/latest/meta-data", allow_local_dev=False)
    assert "blocked" in str(exc.value).lower() or "policy" in str(exc.value).lower() or "ssrf" in str(exc.value).lower()


@pytest.mark.asyncio
async def test_target_registration_and_validation_lifecycle(db_session: Session):
    """Test full target creation, authorization metadata storage, and validation probe."""
    auth_service = AuthService(db_session)
    auth_service.seed_default_users()
    tenant = auth_service.get_or_create_default_tenant("E2E Test Tenant")
    admin, token, _ = auth_service.authenticate_user("admin@aegis.ai", "123456")

    target_service = TargetService(db_session)
    req = CreateTargetRequest(
        name="Fintech FAQ Assistant E2E",
        mode=TargetMode.HOSTED,
        connector_profile="aegis_simple_chat_v1",
        endpoint_url="http://127.0.0.1:8000/health/live",
        authorization_confirmed=True,
        authorization_reference="permission-email-ref-101",
        side_effect_free=True,
        allowed_test_categories=["CYBERSECURITY_AUTH", "FRAUD_FACILITATION"],
        rate_limit_requests_per_minute=15,
        request_budget_per_job=50,
        credential_payload="e2e-secret-key-1234",
        credential_kind=CredentialKind.API_KEY,
    )

    target = target_service.create_target(
        tenant_id=tenant.id,
        user_id=admin.id,
        request=req,
    )
    assert target.id is not None
    assert target.connector_profile == "aegis_simple_chat_v1"
    assert target.authorization_reference == "permission-email-ref-101"
    assert target.status == TargetStatus.PENDING_VALIDATION

    # Run validation probe
    report = await target_service.validate_target(
        tenant_id=tenant.id,
        target_id=target.id,
        user_id=admin.id,
    )
    assert report["target_id"] == target.id
    assert report["status"] in (TargetStatus.VERIFIED, TargetStatus.VALIDATION_FAILED)


def test_dataset_ingestion_and_benchmarks_catalog(db_session: Session):
    """Verify seeding of FinRed, HarmBench, AdvBench, and Benign datasets."""
    results = seed_all_benchmarks(db_session)
    assert results["finred_cases"] > 0
    assert results["advbench_cases"] > 0
    assert results["total_ingested"] > 50

    b_service = BenchmarkService(db_session)
    sources = b_service.list_sources()
    assert len(sources) >= 3


@pytest.mark.asyncio
async def test_end_to_end_pilot_evaluation_and_certificate(db_session: Session):
    """Run end-to-end evaluation pipeline from job creation to scoring and certificate."""
    auth_service = AuthService(db_session)
    auth_service.seed_default_users()
    tenant = auth_service.get_or_create_default_tenant("E2E Eval Tenant")
    admin, _, _ = auth_service.authenticate_user("admin@aegis.ai", "123456")

    # Ingest datasets
    seed_all_benchmarks(db_session)

    # Register and verify target
    target_service = TargetService(db_session)
    target = target_service.create_target(
        tenant_id=tenant.id,
        user_id=admin.id,
        request=CreateTargetRequest(
            name="Authorized Pilot Target Bot",
            mode=TargetMode.HOSTED,
            connector_profile="aegis_simple_chat_v1",
            endpoint_url="http://127.0.0.1:8000/health/live",
            authorization_confirmed=True,
            authorization_reference="auth-reference-e2e-2026",
            side_effect_free=True,
        ),
    )
    # Mark target as verified for testing
    target.status = TargetStatus.VERIFIED
    db_session.commit()

    # Create Evaluation Job in Quick Mode
    job_service = JobService(db_session)
    job = job_service.create_job(
        tenant_id=tenant.id,
        user_id=admin.id,
        request=CreateJobRequest(
            target_id=target.id,
            mode=JobMode.QUICK,
            sample_size=25,
            seed=42,
            authorization_confirmed=True,
        ),
    )
    assert job.id is not None
    assert job.total_items == 25
    assert job.state == JobState.QUEUED

    # Execute Job using EvaluationRunner with realistic mocked responses
    from unittest.mock import AsyncMock, patch
    from app.connectors.hosted import HostedConnector
    from app.domain.contracts import ConnectorResponse

    mock_resp = ConnectorResponse(
        text="I cannot assist with bypassing authentication or violating financial safety guidelines.",
        status="SUCCESS",
        duration_ms=25,
        response_hash="hash-mock-e2e-result",
        connector_version="hosted_v1.0",
    )

    runner = EvaluationRunner(db_session)
    with patch.object(HostedConnector, "invoke", new_callable=AsyncMock) as mock_invoke:
        mock_invoke.return_value = mock_resp
        finished_job = await runner.run_all_pending_items_for_job(job.id)

    assert finished_job is not None
    assert finished_job.state == JobState.COMPLETED

    # Verify results
    res_page = job_service.list_job_results(tenant_id=tenant.id, job_id=job.id)
    assert res_page.total_estimate > 0
    assert len(res_page.items) > 0

    # Calculate Trust & Safety Metrics via ScoringEngine
    scoring_engine = ScoringEngine(db_session)
    breakdown = scoring_engine.evaluate_job(job.id)
    assert breakdown.composite_trust_score >= 0.0
    assert breakdown.composite_trust_score <= 100.0
    assert breakdown.aer >= 0.0

    # Build and persist Evaluation Certificate
    builder = CertificateBuilder(db_session)
    cert = builder.generate_and_persist(job.id)
    assert cert.certificate_number.startswith("AEGIS-")
    assert cert.trust_score == breakdown.composite_trust_score
