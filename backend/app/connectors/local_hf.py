"""Local HF connector implementation for isolated Hugging Face model wrappers."""

import hashlib
import time
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.errors import (
    AuthenticationError,
    QuotaExhaustedError,
    TargetUnavailableError,
    ValidationError,
)
from app.domain.contracts import (
    ConnectorRequest,
    ConnectorResponse,
    ConnectorValidationReport,
    TargetConnectorPort,
)
from app.core.model_catalog import get_model_config


class LocalHFConnector(TargetConnectorPort):
    """Adapter for isolated local Hugging Face model wrapper endpoints."""

    def __init__(
        self,
        endpoint_url: str,
        model_ref: str,
        decrypted_credential: Optional[str] = None,
    ):
        self.endpoint_url = endpoint_url
        self.model_ref = model_ref
        self.decrypted_credential = decrypted_credential

    async def validate(self, configuration: Dict[str, Any]) -> ConnectorValidationReport:
        """Ping the wrapper (we can just send an empty chat or maybe the wrapper exposes /health).
        Since we don't have a /health endpoint on our minimal wrapper, we'll just check if it rejects an empty message properly or ping /chat."""
        if not self.endpoint_url:
            return ConnectorValidationReport(
                is_valid=False,
                status_message="Missing endpoint URL for LOCAL_HF wrapper",
                safe_error_class="invalid_configuration",
            )

        model_config = get_model_config(self.model_ref)
        if not model_config:
            return ConnectorValidationReport(
                is_valid=False,
                status_message=f"Model key '{self.model_ref}' is not allowed or unknown.",
                safe_error_class="invalid_configuration",
            )

        headers = {"Content-Type": "application/json"}
        if self.decrypted_credential:
            headers["Authorization"] = f"Bearer {self.decrypted_credential}"

        # Probe payload
        probe_payload = {
            "request_id": "probe",
            "message": "ping",
            "history": [],
            "model_key": self.model_ref,
            "generation_config": {"max_new_tokens": 1}
        }

        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(settings.TARGET_CONNECT_TIMEOUT, read=settings.TARGET_READ_TIMEOUT),
                follow_redirects=False,
            ) as client:
                resp = await client.post(self.endpoint_url, json=probe_payload, headers=headers)
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                status_ok = resp.status_code < 400

                return ConnectorValidationReport(
                    is_valid=status_ok,
                    status_message=f"Local wrapper responded with HTTP {resp.status_code} ({latency_ms}ms)",
                    capabilities={
                        "http_status": resp.status_code,
                        "latency_ms": latency_ms,
                        "model_key": self.model_ref,
                    },
                    safe_error_class=None if status_ok else f"http_{resp.status_code}",
                )
        except httpx.ConnectTimeout:
            return ConnectorValidationReport(
                is_valid=False,
                status_message="Connection timed out to local wrapper",
                safe_error_class="connect_timeout",
            )
        except httpx.RequestError as e:
            return ConnectorValidationReport(
                is_valid=False,
                status_message=f"Request to local wrapper failed: {type(e).__name__}",
                safe_error_class="transport_error",
            )

    async def invoke(self, request: ConnectorRequest) -> ConnectorResponse:
        """Invoke local target application."""
        headers = {
            "Content-Type": "application/json",
            "X-Request-ID": request.request_id,
        }
        if self.decrypted_credential:
            headers["Authorization"] = f"Bearer {self.decrypted_credential}"

        # Build payload according to demo_target.local_model_api format
        model_config = get_model_config(self.model_ref)
        gen_config = model_config.get("default_generation_config", {})

        # Translate history format if needed. Aegis usually provides roles.
        # Ensure we just pass it down and the wrapper translates it properly.
        history = []
        for turn in request.ordered_history:
            history.append({
                "role": turn.get("role", "user"),
                "content": turn.get("content", turn.get("text", ""))
            })

        wrapper_request = {
            "request_id": request.request_id,
            "message": request.message,
            "history": history,
            "model_key": self.model_ref,
            "generation_config": gen_config
        }

        timeout_sec = request.timeout_budget_ms / 1000.0
        start_time = time.perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(timeout_sec, connect=settings.TARGET_CONNECT_TIMEOUT),
                follow_redirects=False,
            ) as client:
                response = await client.post(self.endpoint_url, json=wrapper_request, headers=headers)
        except httpx.TimeoutException:
            raise TargetUnavailableError(f"Local wrapper timed out after {request.timeout_budget_ms}ms")
        except httpx.RequestError as e:
            raise TargetUnavailableError(f"Local wrapper connection failed: {type(e).__name__}")

        duration_ms = int((time.perf_counter() - start_time) * 1000)

        # Normalize HTTP error statuses
        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(f"Wrapper rejected authentication (HTTP {response.status_code})")
        elif response.status_code == 429:
            raise QuotaExhaustedError("Wrapper rate limit exceeded/busy (HTTP 429)")
        elif response.status_code >= 500:
            raise TargetUnavailableError(f"Wrapper internal error (HTTP {response.status_code})")

        content_bytes = response.content
        if len(content_bytes) > request.response_size_budget_bytes:
            raise ValidationError(
                f"Wrapper response size ({len(content_bytes)} bytes) exceeded budget ({request.response_size_budget_bytes} bytes)"
            )

        try:
            parsed_json = response.json()
        except Exception:
            raise ValidationError("Malformed JSON from local wrapper")

        if "reply" not in parsed_json:
            raise ValidationError("Missing 'reply' in local wrapper response")

        response_hash = parsed_json.get("response_hash") or hashlib.sha256(content_bytes).hexdigest()

        usage_meta = parsed_json.get("usage", {})
        usage_meta["http_status"] = response.status_code
        usage_meta["content_length"] = len(content_bytes)

        # Add model metadata
        if "model" in parsed_json:
            for k, v in parsed_json["model"].items():
                usage_meta[f"model_{k}"] = v

        provider_req_id = response.headers.get("x-request-id") or request.request_id

        return ConnectorResponse(
            text=parsed_json["reply"],
            structured_output=parsed_json,
            provider_request_id=provider_req_id,
            status="SUCCESS",
            duration_ms=duration_ms,
            usage_metadata=usage_meta,
            response_hash=response_hash,
            connector_version="local_hf_v1",
        )

    async def capabilities(self) -> Dict[str, Any]:
        return {
            "mode": "LOCAL_HF",
            "supports_streaming": False,
            "supports_traces": False,
            "supports_multi_turn": True,
        }

    def redacted_description(self) -> Dict[str, Any]:
        return {
            "mode": "LOCAL_HF",
            "endpoint_url": self.endpoint_url,
            "model_ref": self.model_ref,
            "has_credential": bool(self.decrypted_credential),
        }
