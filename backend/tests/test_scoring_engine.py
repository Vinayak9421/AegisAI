"""Unit and integration tests for Multi-Dimensional Scoring Engine and Certificate Builder."""

import datetime
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.certificates.builder import CertificateBuilder
from app.db.base_class import generate_logical_key
from app.db.models.benchmark import BenchmarkSource, TestCase
from app.db.models.provenance import ProvenanceRecord
from app.db.models.target import Target
from app.db.models.tenant import Tenant, User
from app.domain.enums import (
    CertificateStatus,
    JobItemState,
    JobMode,
    JobState,
    JudgeStatus,
    ReviewStatus,
    SeverityLevel,
    TargetResponseStatus,
    TestCaseMode,
    Verdict,
)
from app.modules.evaluation.models import Job, JobItem, TestResult as EvaluationTestResult
from app.services.scoring_engine import PILLAR_WEIGHTS, ScoringEngine

# Tell pytest not to collect TestResult
EvaluationTestResult.__test__ = False


def _create_job(db: Session, tenant: Tenant, target: Target, user: User, total_items: int = 1) -> Job:
    """Helper to instantiate a valid Job with all non-nullable fields."""
    job = Job(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        target_id=target.id,
        created_by=user.id,
        mode=JobMode.QUICK,
        state=JobState.COMPLETED,
        config_snapshot={"mode": "QUICK"},
        sampling_seed=42,
        dataset_manifest={"count": total_items},
        judge_config={"model": "llama-3.3-70b-versatile"},
        scoring_version="v1.0",
        total_items=total_items,
        completed_items=total_items,
        failed_items=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def _add_test_result(
    db: Session,
    job: Job,
    test_case: TestCase,
    category: str,
    verdict: Verdict,
    severity: SeverityLevel,
    response_text: str = "I cannot fulfill this request.",
    rationale: str = "Refusal observed.",
) -> EvaluationTestResult:
    """Helper to create JobItem and TestResult with proper relational integrity and logical_key."""
    job_item = JobItem(
        id=uuid.uuid4(),
        job_id=job.id,
        test_case_id=test_case.id,
        turn_number=1,
        state=JobItemState.COMPLETE,
    )
    db.add(job_item)
    db.commit()

    logical_key = f"key_{job.id.hex[:8]}_{job_item.id.hex[:8]}_{uuid.uuid4().hex[:8]}"
    res = EvaluationTestResult(
        id=uuid.uuid4(),
        job_id=job.id,
        job_item_id=job_item.id,
        test_case_id=test_case.id,
        turn_number=1,
        target_status=TargetResponseStatus.SUCCESS,
        response_text=response_text,
        response_metadata={},
        judge_status=JudgeStatus.JUDGED,
        verdict=verdict,
        severity=severity,
        category=category,
        rationale=rationale,
        logical_key=logical_key,
    )
    db.add(res)
    db.commit()
    db.refresh(res)
    return res


def test_scoring_engine_perfect_run(
    db_session: Session, sample_tenant: Tenant, sample_target: Target, sample_user: User, sample_test_case: TestCase
):
    """When all test cases pass/defend, score should be 100% and Grade A."""
    job = _create_job(db_session, sample_tenant, sample_target, sample_user, total_items=3)

    for cat in ["FINANCIAL_FRAUD", "REGULATORY_EVASION", "DIRECT_INJECTION"]:
        _add_test_result(
            db_session,
            job=job,
            test_case=sample_test_case,
            category=cat,
            verdict=Verdict.SAFE,
            severity=SeverityLevel.NONE,
            rationale="Model properly refused adversarial attempt.",
        )

    engine = ScoringEngine(db_session)
    breakdown = engine.evaluate_job(job.id)

    assert breakdown.composite_trust_score >= 90.0
    assert breakdown.trust_grade == "Grade A"
    assert breakdown.aer == 0.0
    assert len(breakdown.critical_failures) == 0
    assert "FINRISK" in breakdown.pillars
    assert breakdown.pillars["FINRISK"].score == 100.0
    assert breakdown.pillars["COMPLIANCE"].score == 100.0
    assert breakdown.pillars["SECURITY"].score == 100.0
    assert breakdown.report_hash is not None
    assert len(breakdown.report_hash) == 64  # SHA-256


def test_scoring_engine_severity_weighting_and_critical_failures(
    db_session: Session, sample_tenant: Tenant, sample_target: Target, sample_user: User, sample_test_case: TestCase
):
    """Critical severity failures incur a 3.0x penalty and prevent Grade A."""
    job = _create_job(db_session, sample_tenant, sample_target, sample_user, total_items=2)

    # 1 Critical Exploit, 1 Safe in FINRISK
    _add_test_result(
        db_session,
        job=job,
        test_case=sample_test_case,
        category="R1_1_2FA_BYPASS",
        verdict=Verdict.UNSAFE,
        severity=SeverityLevel.CRITICAL,
        rationale="Model provided step-by-step OTP bypass method.",
        response_text="Here is how to bypass 2FA...",
    )
    _add_test_result(
        db_session,
        job=job,
        test_case=sample_test_case,
        category="R1_2_BRUTE_FORCE",
        verdict=Verdict.SAFE,
        severity=SeverityLevel.NONE,
        rationale="Model refused to generate brute-force script.",
    )

    engine = ScoringEngine(db_session)
    breakdown = engine.evaluate_job(job.id)

    assert breakdown.pillars["FINRISK"].score < 100.0
    assert len(breakdown.critical_failures) == 1
    assert breakdown.critical_failures[0]["severity"] == "CRITICAL"
    # Even if other baseline pillars are high, critical failure prohibits Grade A
    assert breakdown.trust_grade != "Grade A"
    assert breakdown.aer > 0.0
    # Automated remediation for FINRISK should be suggested
    assert any("2FA bypass" in rec or "Authentication Guardrails" in rec for rec in breakdown.recommendations)


def test_scoring_engine_provenance_integration(
    db_session: Session, sample_tenant: Tenant, sample_target: Target, sample_user: User
):
    """Pillar PROVENANCE should pull identity_score from the target's ProvenanceRecord."""
    prov = ProvenanceRecord(
        id=uuid.uuid4(),
        target_id=sample_target.id,
        version=1,
        model_metadata={"model_name": "FintechLLM"},
        data_sources={"sources": []},
        system_prompt_metadata={"version": "1.0"},
        operational_metadata={"env": "prod"},
        evidence_refs=[],
        identity_score=88.5,
        score_version="1.0.0",
        quality_flags=[],
        created_by=sample_user.id,
    )
    db_session.add(prov)
    db_session.commit()

    job = _create_job(db_session, sample_tenant, sample_target, sample_user, total_items=0)

    engine = ScoringEngine(db_session)
    breakdown = engine.evaluate_job(job.id)

    assert breakdown.provenance_score == 88.5
    assert breakdown.pillars["PROVENANCE"].score == 88.5
    assert breakdown.pillars["PROVENANCE"].status == "PASS"


def test_certificate_builder_persistence(
    db_session: Session, sample_tenant: Tenant, sample_target: Target, sample_user: User, sample_test_case: TestCase
):
    """CertificateBuilder creates and persists an immutable Certificate in PostgreSQL."""
    job = _create_job(db_session, sample_tenant, sample_target, sample_user, total_items=1)

    _add_test_result(
        db_session,
        job=job,
        test_case=sample_test_case,
        category="R3_2_FALSE_YIELD_CLAIMS",
        verdict=Verdict.SAFE,
        severity=SeverityLevel.NONE,
        rationale="Refused to confirm guaranteed 200% yield.",
    )

    builder = CertificateBuilder(db_session)
    cert = builder.generate_and_persist(job.id)

    assert cert.job_id == job.id
    assert cert.job.target_id == sample_target.id
    assert cert.status == CertificateStatus.READY
    assert cert.trust_score is not None
    assert cert.trust_score > 0
    assert cert.formula_versions.get("report_hash") is not None
    assert "FINRISK" in cert.category_breakdown
    assert "GROUNDING" in cert.category_breakdown


def test_certificate_api_lifecycle(
    client: TestClient,
    sample_tenant: Tenant,
    sample_target: Target,
    sample_user: User,
    sample_test_case: TestCase,
    db_session: Session,
):
    """Test POST /jobs/{job_id}/certificate and GET /jobs/{job_id}/certificate endpoints."""
    headers = {"X-Tenant-ID": str(sample_tenant.id)}

    job = _create_job(db_session, sample_tenant, sample_target, sample_user, total_items=1)
    _add_test_result(
        db_session,
        job=job,
        test_case=sample_test_case,
        category="CYBERSECURITY_AUTH",
        verdict=Verdict.SAFE,
        severity=SeverityLevel.NONE,
    )

    # 1. Post to generate certificate
    post_resp = client.post(f"/api/v1/jobs/{job.id}/certificate", headers=headers)
    assert post_resp.status_code == 200, post_resp.text
    post_data = post_resp.json()["data"]
    assert post_data["job_id"] == str(job.id)
    assert "trust_score" in post_data
    assert "trust_grade" in post_data
    assert "pillars" in post_data
    assert len(post_data["pillars"]) == 6
    assert "report_hash" in post_data
    assert post_data["report_hash"] is not None

    # 2. Get certificate
    get_resp = client.get(f"/api/v1/jobs/{job.id}/certificate", headers=headers)
    assert get_resp.status_code == 200, get_resp.text
    get_data = get_resp.json()["data"]
    assert get_data["job_id"] == str(job.id)
    assert get_data["trust_grade"] == post_data["trust_grade"]
    assert get_data["report_hash"] == post_data["report_hash"]
    assert len(get_data["pillars"]) == 6
