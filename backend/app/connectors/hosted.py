"""Hosted HTTP target connector implementation for REST/OpenAI-compatible APIs."""

import asyncio
import hashlib
import json
import time
from typing import Any, Dict, Optional
import httpx

from app.connectors.profiles.registry import get_connector_profile
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
    """Adapter for hosted HTTP/HTTPS LLM application endpoints supporting profile-based request/response shaping."""

    def __init__(
        self,
        endpoint_url: str,
        decrypted_credential: Optional[str] = None,
        request_profile: Optional[Dict[str, Any]] = None,
        connector_profile_name: Optional[str] = None,
    ):
        self.raw_endpoint_url = endpoint_url
        self.decrypted_credential = decrypted_credential
        self.request_profile = request_profile or {}
        self.connector_profile_name = connector_profile_name or self.request_profile.get("connector_profile", "aegis_simple_chat_v1")
        self.profile = get_connector_profile(self.connector_profile_name)

    async def validate(self, configuration: Dict[str, Any]) -> ConnectorValidationReport:
        """Validate target URL safety (SSRF check) and perform lightweight connectivity/schema probe."""
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
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AegisAI-Validator/1.0",
            **self.request_profile.get("headers", {}),
        }
        if self.decrypted_credential:
            headers["Authorization"] = f"Bearer {self.decrypted_credential}"

        probe_prompt, probe_payload = self.profile.get_probe_payload()
        probe_req = self.profile.build_request(
            endpoint_url=canonical_url,
            prompt=probe_prompt,
            extra_config=self.request_profile,
        )
        if probe_req.json_payload:
            payload = probe_req.json_payload
        else:
            payload = probe_payload

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(settings.TARGET_CONNECT_TIMEOUT, read=settings.TARGET_READ_TIMEOUT),
                follow_redirects=False,
            ) as client:
                resp = await client.post(canonical_url, json=payload, headers=headers)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                status_ok = resp.status_code < 400

                parsed_json = None
                schema_valid = False
                try:
                    parsed_json = resp.json()
                    parsed = self.profile.parse_response(parsed_json, resp.text)
                    schema_valid = bool(parsed.text)
                except Exception:
                    schema_valid = False

                return ConnectorValidationReport(
                    is_valid=status_ok,
                    status_message=f"Endpoint responded with HTTP {resp.status_code} ({latency_ms}ms)",
                    resolved_host_hash=host_hash,
                    capabilities={
                        "http_status": resp.status_code,
                        "server": resp.headers.get("server", "unknown"),
                        "latency_ms": latency_ms,
                        "response_size_bytes": len(resp.content),
                        "schema_valid": schema_valid,
                        "connector_profile": self.profile.profile_name,
                    },
                    safe_error_class=None if status_ok else f"http_{resp.status_code}",
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
        """Invoke hosted target application with prompt and conversation history using active profile."""
        canonical_url, _ = validate_target_url(self.raw_endpoint_url)

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AegisAI-Sentinel/1.0",
            "X-Request-ID": request.request_id,
            **self.request_profile.get("headers", {}),
        }
        if self.decrypted_credential:
            headers["Authorization"] = f"Bearer {self.decrypted_credential}"

        # Build normalized profile payload
        norm_req = self.profile.build_request(
            endpoint_url=canonical_url,
            prompt=request.message,
            history=request.ordered_history,
            session_id=None,
            request_id=request.request_id,
            extra_config=self.request_profile,
        )

        timeout_sec = request.timeout_budget_ms / 1000.0
        start_time = time.perf_counter()
        response = None
        max_retries = 3

        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(timeout_sec, connect=settings.TARGET_CONNECT_TIMEOUT),
                    follow_redirects=False,
                ) as client:
                    response = await client.post(canonical_url, json=norm_req.json_payload, headers=headers)
            except httpx.TimeoutException:
                raise TargetUnavailableError(f"Target timed out after {request.timeout_budget_ms}ms")
            except httpx.RequestError as e:
                raise TargetUnavailableError(f"Target connection failed: {type(e).__name__}")

            # If rate limited (HTTP 429) or transient server busy (HTTP 503/502/504), back off and retry before failing
            if response.status_code in (429, 502, 503, 504) and attempt < max_retries:
                retry_after = response.headers.get("retry-after")
                delay = float(retry_after) if retry_after and retry_after.isdigit() else (3.0 * (attempt + 1))
                logger.warning(
                    f"Target returned HTTP {response.status_code}. Backing off for {delay:.1f}s before retry ({attempt + 1}/{max_retries})..."
                )
                await asyncio.sleep(delay)
                continue
            break

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

        # Parse response using active profile
        raw_json = None
        try:
            raw_json = response.json()
        except Exception:
            raw_json = None

        parsed = self.profile.parse_response(raw_json, response.text)
        provider_req_id = response.headers.get("x-request-id") or response.headers.get("request-id")

        return ConnectorResponse(
            text=parsed.text,
            structured_output=parsed.raw_json,
            provider_request_id=provider_req_id,
            status="SUCCESS",
            duration_ms=duration_ms,
            usage_metadata={"http_status": response.status_code, "content_length": len(content_bytes), **parsed.usage_metadata},
            response_hash=response_hash,
            connector_version=f"{self.profile.profile_name}_{self.profile.profile_version}",
        )

    async def capabilities(self) -> Dict[str, Any]:
        return {
            "mode": "HOSTED",
            "connector_profile": self.profile.profile_name,
            "supports_streaming": False,
            "supports_traces": False,
            "supports_multi_turn": True,
        }

    def redacted_description(self) -> Dict[str, Any]:
        return {
            "mode": "HOSTED",
            "endpoint_url": self.raw_endpoint_url,
            "connector_profile": self.profile.profile_name,
            "has_credential": bool(self.decrypted_credential),
        }
