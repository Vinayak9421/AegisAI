"""Hosted HTTP target connector implementation for REST/OpenAI-compatible APIs."""

import hashlib
import json
import time
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.errors import (
    AuthenticationError,
    PolicyBlockedError,
    QuotaExhaustedError,
    TargetUnavailableError,
    ValidationError,
)
from app.core.logging import logger
from app.core.ssrf import validate_target_url
from app.domain.contracts import (
    ConnectorRequest,
    ConnectorResponse,
    ConnectorValidationReport,
    TargetConnectorPort,
)


class HostedConnector(TargetConnectorPort):
    """Adapter for hosted HTTP/HTTPS LLM application endpoints."""

    def __init__(
        self,
        endpoint_url: str,
        decrypted_credential: Optional[str] = None,
        request_profile: Optional[Dict[str, Any]] = None,
    ):
        self.raw_endpoint_url = endpoint_url
        self.decrypted_credential = decrypted_credential
        self.request_profile = request_profile or {}

    async def validate(self, configuration: Dict[str, Any]) -> ConnectorValidationReport:
        """Validate target URL safety (SSRF check) and perform lightweight connectivity probe."""
        endpoint_url = configuration.get("endpoint_url") or self.raw_endpoint_url
        if not endpoint_url:
            return ConnectorValidationReport(
                is_valid=False,
                status_message="Missing endpoint URL",
                safe_error_class="invalid_configuration",
            )

        try:
            canonical_url, host_hash = validate_target_url(endpoint_url)
        except (ValidationError, PolicyBlockedError) as e:
            return ConnectorValidationReport(
                is_valid=False,
                status_message=str(e),
                safe_error_class="ssrf_or_validation_failure",
            )

        # Build probe headers
        headers = dict(self.request_profile.get("headers", {}))
        if self.decrypted_credential:
            headers["Authorization"] = f"Bearer {self.decrypted_credential}"

        # Lightweight probe (OPTIONS or GET probe)
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(settings.TARGET_CONNECT_TIMEOUT, read=settings.TARGET_READ_TIMEOUT),
                follow_redirects=False,
            ) as client:
                resp = await client.request("OPTIONS", canonical_url, headers=headers)
                status_ok = resp.status_code < 500
                return ConnectorValidationReport(
                    is_valid=status_ok,
                    status_message=f"Endpoint responded with HTTP {resp.status_code}",
                    resolved_host_hash=host_hash,
                    capabilities={"http_status": resp.status_code, "server": resp.headers.get("server", "unknown")},
                    safe_error_class=None if status_ok else "server_error",
                )
        except httpx.ConnectTimeout:
            return ConnectorValidationReport(
                is_valid=False,
                status_message="Connection timed out",
                resolved_host_hash=host_hash,
                safe_error_class="connect_timeout",
            )
        except httpx.RequestError as e:
            return ConnectorValidationReport(
                is_valid=False,
                status_message=f"Request failed: {type(e).__name__}",
                resolved_host_hash=host_hash,
                safe_error_class="transport_error",
            )

    async def invoke(self, request: ConnectorRequest) -> ConnectorResponse:
        """Invoke hosted target application with prompt and conversation history."""
        canonical_url, _ = validate_target_url(self.raw_endpoint_url)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AegisAI-Sentinel/1.0",
            "X-Request-ID": request.request_id,
            **self.request_profile.get("headers", {}),
        }
        if self.decrypted_credential:
            headers["Authorization"] = f"Bearer {self.decrypted_credential}"

        # Form standard payload
        messages = []
        for turn in request.ordered_history:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
        messages.append({"role": "user", "content": request.message})

        payload = {
            "messages": messages,
            **self.request_profile.get("extra_body", {}),
        }

        timeout_sec = request.timeout_budget_ms / 1000.0
        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(timeout_sec, connect=settings.TARGET_CONNECT_TIMEOUT),
                follow_redirects=False,
            ) as client:
                response = await client.post(canonical_url, json=payload, headers=headers)
        except httpx.TimeoutException:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            raise TargetUnavailableError(f"Target timed out after {request.timeout_budget_ms}ms")
        except httpx.RequestError as e:
            raise TargetUnavailableError(f"Target connection failed: {type(e).__name__}")

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Normalize HTTP error statuses
        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(f"Target rejected authentication (HTTP {response.status_code})")
        elif response.status_code == 429:
            raise QuotaExhaustedError("Target rate limit exceeded (HTTP 429)")
        elif response.status_code >= 500:
            raise TargetUnavailableError(f"Target server error (HTTP {response.status_code})")

        content_bytes = response.content
        if len(content_bytes) > request.response_size_budget_bytes:
            raise ValidationError(
                f"Target response size ({len(content_bytes)} bytes) exceeded budget ({request.response_size_budget_bytes} bytes)"
            )

        response_hash = hashlib.sha256(content_bytes).hexdigest()

        # Extract text output
        text_content = ""
        structured_data = {}
        try:
            parsed_json = response.json()
            if isinstance(parsed_json, dict):
                structured_data = parsed_json
                if "choices" in parsed_json and len(parsed_json["choices"]) > 0:
                    text_content = parsed_json["choices"][0].get("message", {}).get("content", "")
                elif "response" in parsed_json:
                    text_content = str(parsed_json["response"])
                elif "output" in parsed_json:
                    text_content = str(parsed_json["output"])
                elif "content" in parsed_json:
                    text_content = str(parsed_json["content"])
                else:
                    text_content = response.text
            else:
                text_content = response.text
        except Exception:
            text_content = response.text

        provider_req_id = response.headers.get("x-request-id") or response.headers.get("request-id")

        return ConnectorResponse(
            text=text_content,
            structured_output=structured_data if structured_data else None,
            provider_request_id=provider_req_id,
            status="SUCCESS",
            duration_ms=duration_ms,
            usage_metadata={"http_status": response.status_code, "content_length": len(content_bytes)},
            response_hash=response_hash,
            connector_version="hosted_v1.0",
        )

    async def capabilities(self) -> Dict[str, Any]:
        return {
            "mode": "HOSTED",
            "supports_streaming": False,
            "supports_traces": False,
            "supports_multi_turn": True,
        }

    def redacted_description(self) -> Dict[str, Any]:
        return {
            "mode": "HOSTED",
            "endpoint_url": self.raw_endpoint_url,
            "has_credential": bool(self.decrypted_credential),
        }
