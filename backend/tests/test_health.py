"""Health check endpoints and correlation ID middleware tests."""

import uuid
from fastapi.testclient import TestClient


def test_health_live_endpoint(client: TestClient):
    response = client.get("/health/live")
    assert response.status_code == 200
    json_data = response.json()
    assert "data" in json_data
    assert "meta" in json_data
    assert json_data["data"]["status"] == "alive"
    assert "request_id" in json_data["meta"]
    assert "X-Request-ID" in response.headers


def test_health_db_endpoint(client: TestClient):
    response = client.get("/health/db")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["data"]["status"] == "ready"
    assert json_data["data"]["database"] == "connected"


def test_correlation_id_propagated_when_provided(client: TestClient):
    custom_request_id = str(uuid.uuid4())
    response = client.get(
        "/health/live",
        headers={"X-Request-ID": custom_request_id},
    )
    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == custom_request_id
    json_data = response.json()
    assert json_data["meta"]["request_id"] == custom_request_id


def test_error_envelope_format_on_not_found(client: TestClient):
    response = client.get("/api/v1/non_existent_resource")
    assert response.status_code == 404
    json_data = response.json()
    assert "error" in json_data
    assert json_data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in json_data["error"]
