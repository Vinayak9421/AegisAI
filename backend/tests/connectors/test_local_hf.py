import pytest
import httpx
from unittest.mock import AsyncMock, patch
from app.connectors.local_hf import LocalHFConnector
from app.domain.contracts import ConnectorRequest
from app.core.errors import (
    AuthenticationError,
    QuotaExhaustedError,
    TargetUnavailableError,
    ValidationError,
)

@pytest.fixture
def connector():
    return LocalHFConnector(
        endpoint_url="http://localhost:8001/chat",
        model_ref="small_instruct_local_v1",
        decrypted_credential="test-secret"
    )

@pytest.fixture
def valid_request():
    return ConnectorRequest(
        target_id="tgt_123",
        request_id="req_123",
        message="Hello",
        ordered_history=[{"role": "user", "content": "hi"}],
        timeout_budget_ms=30000,
        response_size_budget_bytes=1048576,
    )

@pytest.mark.asyncio
async def test_invoke_success(connector, valid_request):
    mock_response = httpx.Response(
        200,
        json={
            "request_id": "req_123",
            "reply": "Mocked reply",
            "model": {"repo_id": "mock_repo", "revision": "main"},
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
            "response_hash": "hash123",
            "latency_ms": 100
        },
        request=httpx.Request("POST", "http://localhost:8001/chat")
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        response = await connector.invoke(valid_request)

        assert response.status == "SUCCESS"
        assert response.text == "Mocked reply"
        assert response.response_hash == "hash123"
        assert response.usage_metadata["prompt_tokens"] == 10

@pytest.mark.asyncio
async def test_invoke_timeout(connector, valid_request):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.side_effect = httpx.TimeoutException("Timeout")

        with pytest.raises(TargetUnavailableError, match="Local wrapper timed out"):
            await connector.invoke(valid_request)

@pytest.mark.asyncio
async def test_invoke_401(connector, valid_request):
    mock_response = httpx.Response(401, request=httpx.Request("POST", "url"))

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(AuthenticationError):
            await connector.invoke(valid_request)

@pytest.mark.asyncio
async def test_invoke_429(connector, valid_request):
    mock_response = httpx.Response(429, request=httpx.Request("POST", "url"))

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(QuotaExhaustedError):
            await connector.invoke(valid_request)

@pytest.mark.asyncio
async def test_invoke_500(connector, valid_request):
    mock_response = httpx.Response(500, request=httpx.Request("POST", "url"))

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(TargetUnavailableError, match="Wrapper internal error"):
            await connector.invoke(valid_request)

@pytest.mark.asyncio
async def test_invoke_malformed_json(connector, valid_request):
    mock_response = httpx.Response(200, content=b"invalid json", request=httpx.Request("POST", "url"))

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        with pytest.raises(ValidationError, match="Malformed JSON"):
            await connector.invoke(valid_request)

@pytest.mark.asyncio
async def test_validate_success(connector):
    mock_response = httpx.Response(200, request=httpx.Request("POST", "url"))

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        report = await connector.validate({"endpoint_url": connector.endpoint_url})

        assert report.is_valid is True

@pytest.mark.asyncio
async def test_validate_failure(connector):
    mock_response = httpx.Response(500, request=httpx.Request("POST", "url"))

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        report = await connector.validate({"endpoint_url": connector.endpoint_url})

        assert report.is_valid is False
