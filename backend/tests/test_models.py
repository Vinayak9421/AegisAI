"""Database models, relationships, and integrity tests."""

import datetime
import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import CredentialEncryptionService
import app.db.models as models
from app.domain.enums import (
    AttemptPhase,
    AttemptStatus,
    CertificateStatus,
    CredentialKind,
    CredentialStatus,
    JobItemState,
    JobMode,
    JobState,
    JudgeStatus,
    SeverityLevel,
    TargetMode,
    TargetResponseStatus,
    TargetStatus,
    TenantStatus,
    UserRole,
    UserStatus,
    Verdict,
)


def test_tenant_and_user_creation(db_session: Session, sample_tenant: models.Tenant, sample_user: models.User):
    assert sample_tenant.id is not None
    assert sample_user.tenant_id == sample_tenant.id
    assert len(sample_tenant.users) == 1
    assert sample_tenant.users[0].email == sample_user.email


def test_target_credential_encryption(db_session: Session, sample_target: models.Target):
    raw_api_key = "sk-live-supersecrettoken123456789"
    ciphertext, key_version, last4 = CredentialEncryptionService.encrypt_secret(raw_api_key)
    
    assert last4 == "6789"
    assert ciphertext != raw_api_key.encode()

    cred = models.TargetCredential(
        id=uuid.uuid4(),
        target_id=sample_target.id,
        kind=CredentialKind.API_KEY,
        ciphertext=ciphertext,
        key_version=key_version,
        secret_last4=last4,
        status=CredentialStatus.ACTIVE,
    )
    db_session.add(cred)
    db_session.commit()
    db_session.refresh(cred)

    assert cred.id is not None
    assert cred.secret_last4 == "6789"
    
    decrypted = CredentialEncryptionService.decrypt_secret(cred.ciphertext, cred.key_version)
    assert decrypted == raw_api_key


def test_provenance_record_versioning(
    db_session: Session,
    sample_target: models.Target,
    sample_user: models.User,
):
    prov = models.ProvenanceRecord(
        id=uuid.uuid4(),
        target_id=sample_target.id,
        version=1,
        model_metadata={"base_model": "llama-3-8b-instruct", "provider": "Groq"},
        data_sources={"internal_kb": "v2026.1"},
        system_prompt_metadata={"safety_version": "v1.2", "bounded": True},
        operational_metadata={"owner": "compliance-team@acme.com"},
        identity_score=85.50,
        score_version="1.0.0",
        created_by=sample_user.id,
    )
    db_session.add(prov)
    db_session.commit()

    # Verify uniqueness of (target_id, version)
    duplicate_prov = models.ProvenanceRecord(
        id=uuid.uuid4(),
        target_id=sample_target.id,
        version=1,
        model_metadata={},
        data_sources={},
        system_prompt_metadata={},
        operational_metadata={},
        score_version="1.0.0",
        created_by=sample_user.id,
    )
    db_session.add(duplicate_prov)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_audit_log_creation(
    db_session: Session,
    sample_tenant: models.Tenant,
    sample_user: models.User,
):
    audit = models.AuditLog(
        id=uuid.uuid4(),
        tenant_id=sample_tenant.id,
        actor_user_id=sample_user.id,
        action="TARGET_REGISTERED",
        resource_type="TARGET",
        resource_id=uuid.uuid4(),
        request_id="req-12345",
        metadata_payload={"target_name": "Loan Bot"},
    )
    db_session.add(audit)
    db_session.commit()
    db_session.refresh(audit)

    assert audit.id is not None
    assert audit.action == "TARGET_REGISTERED"
