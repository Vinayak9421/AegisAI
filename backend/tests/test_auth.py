"""Unit and integration tests for authentication, user registration, and RBAC."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.tenant import Tenant, User
from app.domain.enums import TenantStatus, UserRole, UserStatus
from app.services.auth_service import AuthService


def test_auth_registration(client: TestClient, db_session: Session):
    """Test user registration assigns MEMBER role and returns JWT."""
    payload = {
        "email": "newuser@fintechcorp.com",
        "password": "securepassword123",
        "organization_name": "Fintech Corp",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@fintechcorp.com"
    assert data["user"]["role"] == "MEMBER"
    assert data["user"]["tenant_name"] == "Fintech Corp"

    # Duplicate registration fails with 409
    dup_resp = client.post("/api/v1/auth/register", json=payload)
    assert dup_resp.status_code == 409


def test_auth_login_success_and_failure(client: TestClient, db_session: Session):
    """Test login succeeds for valid credentials and rejects invalid password."""
    auth_svc = AuthService(db_session)
    auth_svc.seed_default_users()

    # 1. Admin login with password '123456'
    admin_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegis.ai", "password": "123456"},
    )
    assert admin_resp.status_code == 200
    admin_data = admin_resp.json()["data"]
    assert admin_data["user"]["role"] == "ADMIN"
    assert admin_data["user"]["email"] == "admin@aegis.ai"

    # 2. User login with password 'user123'
    user_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "user@aegis.ai", "password": "user123"},
    )
    assert user_resp.status_code == 200
    user_data = user_resp.json()["data"]
    assert user_data["user"]["role"] == "MEMBER"

    # 3. Invalid password fails with 401
    fail_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegis.ai", "password": "wrong_password"},
    )
    assert fail_resp.status_code == 401


def test_auth_me_endpoint(client: TestClient, db_session: Session):
    """Test /api/v1/auth/me returns identity when authenticated with Bearer token."""
    auth_svc = AuthService(db_session)
    auth_svc.seed_default_users()

    # Login to get token
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@aegis.ai", "password": "123456"},
    )
    token = login_resp.json()["data"]["access_token"]

    # Call /me with valid token
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    profile = me_resp.json()["data"]
    assert profile["email"] == "admin@aegis.ai"
    assert profile["role"] == "ADMIN"

    # Call /me without token fails with 401
    unauth_resp = client.get("/api/v1/auth/me")
    assert unauth_resp.status_code == 401
