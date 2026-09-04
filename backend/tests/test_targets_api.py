"""API tests for target registration, credentials, updating, soft deletion, and validation probes."""

import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import app.db.models as models
from app.domain.enums import CredentialKind, CredentialStatus, TargetMode, TargetStatus


def test_create_target_success_and_idempotency(client: TestClient, sample_tenant: models.Tenant):
    target_payload = {
        "name": f"Wealth Advisor Bot-{uuid.uuid4().hex[:6]}",
        "mode": "HOSTED",
        "endpoint_url": "https://api.acmefin.com/v1/chat",
        "authorization_confirmed": True,
        "request_profile": {"headers": {"Custom-Header": "AegisTest"}},
        "capabilities": {"sessions": True},
        "credential_payload": "sk-secret-token-987654321",
        "credential_kind": "API_KEY",
    }
    idem_key = str(uuid.uuid4())

    # First request
    response1 = client.post(
        "/api/v1/targets",
        json=target_payload,
        headers={"X-Tenant-ID": str(sample_tenant.id), "Idempotency-Key": idem_key},
    )
    assert response1.status_code == 201
    data1 = response1.json()["data"]
    assert data1["name"] == target_payload["name"]
    assert data1["mode"] == "HOSTED"
    assert data1["status"] == "PENDING_VALIDATION"
    assert data1["configuration_version"] == 1
    assert "credential_payload" not in data1  # Secrets never echoed

    target_id = data1["id"]

    # Replay request with same Idempotency-Key returns same resource
    response2 = client.post(
        "/api/v1/targets",
        json=target_payload,
        headers={"X-Tenant-ID": str(sample_tenant.id), "Idempotency-Key": idem_key},
    )
    assert response2.status_code == 201
    data2 = response2.json()["data"]
    assert data2["id"] == target_id


def test_create_target_rejects_missing_authorization(client: TestClient, sample_tenant: models.Tenant):
    target_payload = {
        "name": "Unauthorized Bot",
        "mode": "HOSTED",
        "endpoint_url": "https://api.acmefin.com/v1/chat",
        "authorization_confirmed": False,
    }
    response = client.post(
        "/api/v1/targets",
        json=target_payload,
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert response.status_code == 422


def test_target_crud_lifecycle(client: TestClient, sample_tenant: models.Tenant):
    # 1. Create
    target_payload = {
        "name": f"Retirement Bot-{uuid.uuid4().hex[:6]}",
        "mode": "HOSTED",
        "endpoint_url": "https://api.acmefin.com/v1/retirement",
        "authorization_confirmed": True,
    }
    create_res = client.post(
        "/api/v1/targets",
        json=target_payload,
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert create_res.status_code == 201
    target_id = create_res.json()["data"]["id"]

    # 2. Get by ID
    get_res = client.get(
        f"/api/v1/targets/{target_id}",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert get_res.status_code == 200
    assert get_res.json()["data"]["id"] == target_id

    # 3. Patch (updates config and bumps configuration_version)
    patch_res = client.patch(
        f"/api/v1/targets/{target_id}",
        json={"name": f"Retirement Bot Updated-{uuid.uuid4().hex[:4]}", "capabilities": {"streaming": True}},
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["data"]["configuration_version"] == 2

    # 4. List targets
    list_res = client.get(
        "/api/v1/targets",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert list_res.status_code == 200
    items = list_res.json()["data"]["items"]
    assert any(t["id"] == target_id for t in items)

    # 5. Delete (Soft delete)
    del_res = client.delete(
        f"/api/v1/targets/{target_id}",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert del_res.status_code == 204

    # 6. Verify cannot get soft-deleted target
    get_after_del = client.get(
        f"/api/v1/targets/{target_id}",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert get_after_del.status_code == 404


def test_target_credential_management_and_revocation(client: TestClient, sample_tenant: models.Tenant):
    # 1. Create target without credential
    target_payload = {
        "name": f"Payment Assistant-{uuid.uuid4().hex[:6]}",
        "mode": "HOSTED",
        "endpoint_url": "https://api.acmefin.com/v1/pay",
        "authorization_confirmed": True,
    }
    res = client.post(
        "/api/v1/targets",
        json=target_payload,
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    target_id = res.json()["data"]["id"]

    # 2. Add credential
    cred_res = client.post(
        f"/api/v1/targets/{target_id}/credentials",
        json={"kind": "API_KEY", "secret": "live_key_secret_12345678"},
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert cred_res.status_code == 201
    cred_data = cred_res.json()["data"]
    assert cred_data["secret_last4"] == "5678"
    assert cred_data["status"] == "ACTIVE"
    cred_id = cred_data["id"]

    # 3. Revoke credential
    revoke_res = client.post(
        f"/api/v1/targets/{target_id}/credentials/{cred_id}/revoke",
        headers={"X-Tenant-ID": str(sample_tenant.id)},
    )
    assert revoke_res.status_code == 200
    assert revoke_res.json()["data"]["status"] == "REVOKED"
    assert revoke_res.json()["data"]["revoked_at"] is not None
