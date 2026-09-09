"""Hosted HTTP connector execution and error normalization tests."""

import pytest
import httpx
from app.connectors.hosted import HostedConnector
from app.core.errors import AuthenticationError, QuotaExhaustedError, TargetUnavailableError, ValidationError
from app.domain.contracts import ConnectorRequest


@pytest.mark.asyncio
async def test_hosted_connector_capabilities_and_description():
    connector = HostedConnector(
        endpoint_url="https://api.acmefin.com/v1/chat",
        decrypted_credential="test_secret_key",
    )
    caps = await connector.capabilities()
    assert caps["mode"] == "HOSTED"
    assert caps["supports_multi_turn"] is True

    desc = connector.redacted_description()
    assert desc["endpoint_url"] == "https://api.acmefin.com/v1/chat"
    assert desc["has_credential"] is True
    assert "test_secret_key" not in str(desc)


@pytest.mark.asyncio
async def test_hosted_connector_invoke_success_with_mock_transport(monkeypatch):
    # Mock httpx AsyncClient post
    async def mock_post(self, url, json=None, headers=None, **kwargs):
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer mock_key_123"
        return httpx.Response(
            status_code=200,
            json={
                "choices": [
                    {"message": {"content": "Hello! I am a financial guidance bot. How can I help you?"}}
                ]
            },
            headers={"x-request-id": "prov-req-999"},
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_post)

    connector = HostedConnector(
        endpoint_url="https://api.acmefin.com/v1/chat",
        decrypted_credential="mock_key_123",
    )

    request = ConnectorRequest(
        target_id="target-123",
        request_id="req-test-456",
        message="What is the prime lending rate?",
        ordered_history=[],
    )

    response = await connector.invoke(request)
    assert response.status == "SUCCESS"
    assert response.text == "Hello! I am a financial guidance bot. How can I help you?"
    assert response.provider_request_id == "prov-req-999"
    assert len(response.response_hash) == 64
    assert response.connector_version.startswith("aegis_simple_chat") or response.connector_version == "hosted_v1.0"


@pytest.mark.asyncio
async def test_hosted_connector_normalizes_error_responses(monkeypatch):
    connector = HostedConnector(endpoint_url="https://api.acmefin.com/v1/chat")
    request = ConnectorRequest(target_id="target-1", request_id="req-1", message="test")

    # 401 Authentication Error
    async def mock_401(self, *args, **kwargs):
        return httpx.Response(status_code=401, text="Unauthorized")

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_401)
    with pytest.raises(AuthenticationError):
        await connector.invoke(request)

    # 429 Quota / Rate Limit Error
    async def mock_429(self, *args, **kwargs):
        return httpx.Response(status_code=429, text="Rate limit exceeded")

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_429)
    with pytest.raises(QuotaExhaustedError):
        await connector.invoke(request)

    # 500 Server Error
    async def mock_500(self, *args, **kwargs):
        return httpx.Response(status_code=500, text="Internal Server Error")

    monkeypatch.setattr(httpx.AsyncClient, "post", mock_500)
    with pytest.raises(TargetUnavailableError):
        await connector.invoke(request)
