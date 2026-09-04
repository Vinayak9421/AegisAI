"""Tests for Provenance & Identity Scoring Engine, Service, and REST API Endpoints."""

import datetime
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import app.db.models as models
from app.core.errors import ValidationError
from app.provenance.scorer import ProvenanceScorer, validate_no_secrets


# -----------------------------------------------------------------------------
# Fixtures & Sample Metadata Payloads
# -----------------------------------------------------------------------------

@pytest.fixture
def complete_metadata() -> dict:
    """Complete, high-transparency metadata yielding ~100% Identity Score."""
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "model_metadata": {
            "model_name": "meta-llama/Llama-3.3-70B-Instruct",
            "model_revision": "b96238b7244eb6f39643d9b4b00ec151b752945d",
            "provider": "Meta",
            "deployment_mode": "hosted",
            "is_fine_tuned": True,
            "fine_tuning_details": {
                "method": "LoRA",
                "base_model": "Llama-3.3-70B",
                "target_modules": ["q_proj", "v_proj"],
            },
            "evidence_links": ["https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct"],
            "review_notes": "Internal Red-Team Audit completed 2026-08-15.",
        },
        "data_sources": {
            "sources": [
                {
                    "source_id": "fin_faqs_v2",
                    "name": "Fintech Customer FAQs",
                    "purpose": "General banking assistance and product guidance",
                    "license": "Proprietary-Internal",
                    "owner": "Acme Fintech Corp",
                    "version": "2.4.0",
                    "last_updated": "2026-08-01",
                },
                {
                    "source_id": "regulatory_guidance_2026",
                    "name": "Financial Conduct Authority Public Handbook",
                    "purpose": "Regulatory compliance grounding",
                    "license": "Open Government Licence v3.0",
                    "owner": "FCA UK",
                    "version": "2026-Q2",
                    "last_updated": "2026-06-30",
                },
            ],
            "rag_enabled": True,
            "grounding_policy": "Cosine similarity top-k=3, chunk_size=512, strict grounding threshold 0.82.",
        },
        "system_prompt_metadata": {
            "documented": True,
            "prompt_version": "v3.1.2",
            "prompt_owner": "sec-ops@acmefin.com",
            "safety_instructions": "Refuse illegal financial advice, require human approval for transfers over $1000, enforce KYC verification.",
            "tool_constraints": "Read-only access to account balance API; executing wire transfers is strictly prohibited.",
            "tools_enabled": True,
            "change_history": [
                {"version": "v3.1.2", "date": "2026-08-20", "note": "Strengthened anti-phishing guardrails"}
            ],
            "last_reviewed_at": "2026-08-20",
            "known_limitations": "Cannot process non-English financial terminology or tax advisory.",
            "human_escalation_path": "Route ambiguous queries or complaints to live customer support tier 2.",
        },
        "operational_metadata": {
            "application_version": "2.1.0",
            "contact_email": "ai-safety@acmefin.com",
            "evaluation_consent": True,
            "evidence_freshness_date": now_iso,
        },
        "evidence_refs": [
            {
                "title": "Model Card & Audit Report",
                "uri": "https://docs.acmefin.com/audit/2026-report.pdf",
                "evidence_type": "audit_report",
            }
        ],
    }


# -----------------------------------------------------------------------------
# Unit Tests: ProvenanceScorer Formula & Quality Flags
# -----------------------------------------------------------------------------

def test_scorer_complete_metadata_gives_100_percent(complete_metadata):
    scorer = ProvenanceScorer()
    result = scorer.calculate_identity_score(
        model_metadata=complete_metadata["model_metadata"],
        data_sources=complete_metadata["data_sources"],
        system_prompt_metadata=complete_metadata["system_prompt_metadata"],
        operational_metadata=complete_metadata["operational_metadata"],
    )
    assert result.identity_score == 100.0
    assert result.dimension_scores["model_identity"] == 100.0
    assert result.dimension_scores["data_provenance"] == 100.0
    assert result.dimension_scores["system_configuration"] == 100.0
    assert result.dimension_scores["operational_accountability"] == 100.0
    assert "POOR_TRANSPARENCY_SCORE" not in result.quality_flags
    assert "LOW_MODEL_TRANSPARENCY" not in result.quality_flags


def test_scorer_partial_metadata_deductions_and_flags():
    scorer = ProvenanceScorer()
    # Sparse metadata: only names, missing revisions, no data sources, no safety constraints
    result = scorer.calculate_identity_score(
        model_metadata={"model_name": "Llama-3"},
        data_sources={"sources": []},
        system_prompt_metadata={"documented": False},
        operational_metadata={"application_version": "1.0", "evaluation_consent": False},
    )
    # Score should be significantly lower than 50%
    assert result.identity_score < 40.0
    assert "POOR_TRANSPARENCY_SCORE" in result.quality_flags
    assert "NO_DECLARED_DATA_SOURCES" in result.quality_flags
    assert "MISSING_EVALUATION_CONSENT" in result.quality_flags
    assert "LOW_MODEL_TRANSPARENCY" in result.quality_flags
    assert "WEAK_SYSTEM_PROMPT_GOVERNANCE" in result.quality_flags


def test_scorer_dynamic_not_applicable_denominator(complete_metadata):
    scorer = ProvenanceScorer()
    # If RAG is explicitly not applicable and tools are disabled
    complete_metadata["data_sources"]["retrieval_not_applicable"] = True
    complete_metadata["system_prompt_metadata"]["tools_enabled"] = False

    result = scorer.calculate_identity_score(
        model_metadata=complete_metadata["model_metadata"],
        data_sources=complete_metadata["data_sources"],
        system_prompt_metadata=complete_metadata["system_prompt_metadata"],
        operational_metadata=complete_metadata["operational_metadata"],
    )
    # Since all applicable sub-criteria are satisfied, score remains 100%
    assert result.identity_score == 100.0
    assert result.dimension_scores["data_provenance"] == 100.0
    assert result.dimension_scores["system_configuration"] == 100.0


def test_scorer_secret_leak_prevention():
    # Attempting to embed an API key inside the system prompt metadata must be rejected
    with pytest.raises(ValidationError, match="Potential credential or secret detected"):
        validate_no_secrets(
            {"safety_instructions": "Connect using sk-ant-api03-secret1234567890abcdefghijklm to fetch balances."}
        )

    with pytest.raises(ValidationError, match="Potential credential or secret detected"):
        validate_no_secrets(
            {"evidence": ["Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.dummytoken1234567890abcdef"]}
        )


# -----------------------------------------------------------------------------
# Integration Tests: REST API Endpoints (/api/v1/targets/{id}/provenance)
# -----------------------------------------------------------------------------

def test_provenance_api_lifecycle(client: TestClient, sample_tenant: models.Tenant, complete_metadata):
    # 1. Register a target first
    target_resp = client.post(
        "/api/v1/targets",
        json={
            "name": f"Fintech Advisor Bot-{uuid.uuid4().hex[:6]}",
            "mode": "HOSTED",
            "endpoint_url": "https://api.acmefin.com/v1/chat",
            "authorization_confirmed": True,
        },
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert target_resp.status_code == 201
    target_id = target_resp.json()["data"]["id"]

    # 2. Ingest first provenance declaration (Version 1)
    prov_resp1 = client.post(
        f"/api/v1/targets/{target_id}/provenance",
        json=complete_metadata,
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert prov_resp1.status_code == 201
    data1 = prov_resp1.json()["data"]
    assert data1["target_id"] == target_id
    assert data1["version"] == 1
    assert data1["identity_score"] == 100.0
    assert data1["dimension_scores"]["model_identity"] == 100.0
    assert data1["score_version"] == "identity_v1.0"

    # 3. Ingest updated declaration with some missing fields (Version 2)
    updated_metadata = dict(complete_metadata)
    updated_metadata["model_metadata"] = {"model_name": "Llama-3.3-Custom"}  # Missing revision and fine-tuning
    prov_resp2 = client.post(
        f"/api/v1/targets/{target_id}/provenance",
        json=updated_metadata,
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert prov_resp2.status_code == 201
    data2 = prov_resp2.json()["data"]
    assert data2["target_id"] == target_id
    assert data2["version"] == 2
    assert data2["identity_score"] < 100.0

    # 4. Fetch latest version
    latest_resp = client.get(
        f"/api/v1/targets/{target_id}/provenance/latest",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert latest_resp.status_code == 200
    assert latest_resp.json()["data"]["version"] == 2

    # 5. Fetch specific historical version 1
    v1_resp = client.get(
        f"/api/v1/targets/{target_id}/provenance/1",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert v1_resp.status_code == 200
    assert v1_resp.json()["data"]["version"] == 1
    assert v1_resp.json()["data"]["identity_score"] == 100.0

    # 6. List all versions (should be 2 versions, ordered descending: [v2, v1])
    list_resp = client.get(
        f"/api/v1/targets/{target_id}/provenance",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert list_resp.status_code == 200
    history = list_resp.json()["data"]
    assert len(history) == 2
    assert history[0]["version"] == 2
    assert history[1]["version"] == 1


def test_provenance_idempotency_replay(client: TestClient, sample_tenant: models.Tenant, complete_metadata):
    # Register target
    target_resp = client.post(
        "/api/v1/targets",
        json={
            "name": f"Wealth Manager-{uuid.uuid4().hex[:6]}",
            "mode": "HOSTED",
            "endpoint_url": "https://api.acmefin.com/v1/chat",
            "authorization_confirmed": True,
        },
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    target_id = target_resp.json()["data"]["id"]
    idem_key = str(uuid.uuid4())

    # Submit with idempotency key
    resp1 = client.post(
        f"/api/v1/targets/{target_id}/provenance",
        json=complete_metadata,
        headers={"X-Tenant-ID": str(sample_tenant.id), "Idempotency-Key": idem_key},
    )
    assert resp1.status_code == 201
    record_id = resp1.json()["data"]["id"]
    assert resp1.json()["data"]["version"] == 1

    # Replay with same key returns the exact same record without incrementing version
    resp2 = client.post(
        f"/api/v1/targets/{target_id}/provenance",
        json=complete_metadata,
        headers={"X-Tenant-ID": str(sample_tenant.id), "Idempotency-Key": idem_key},
    )
    assert resp2.status_code == 201
    assert resp2.json()["data"]["id"] == record_id
    assert resp2.json()["data"]["version"] == 1


def test_provenance_tenant_isolation(client: TestClient, sample_tenant: models.Tenant, complete_metadata):
    # Create target in tenant 1
    target_resp = client.post(
        "/api/v1/targets",
        json={
            "name": f"Isolated Target-{uuid.uuid4().hex[:6]}",
            "mode": "HOSTED",
            "endpoint_url": "https://api.acmefin.com/v1/chat",
            "authorization_confirmed": True,
        },
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    target_id = target_resp.json()["data"]["id"]

    # Different tenant tries to add provenance -> 404
    other_tenant_id = uuid.uuid4()
    resp = client.post(
        f"/api/v1/targets/{target_id}/provenance",
        json=complete_metadata,
        headers={"X-Tenant-ID": str(other_tenant_id)},
    )
    assert resp.status_code == 404


def test_provenance_nonexistent_target(client: TestClient, sample_tenant: models.Tenant, complete_metadata):
    fake_target_id = uuid.uuid4()
    resp = client.post(
        f"/api/v1/targets/{fake_target_id}/provenance",
        json=complete_metadata,
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert resp.status_code == 404
