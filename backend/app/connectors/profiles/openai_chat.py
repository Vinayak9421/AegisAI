"""OpenAI-Compatible Chat Profile (openai_chat_v1).

Format:
  Request: POST /v1/chat/completions { "model": "...", "messages": [...], "temperature": 0.2, "max_tokens": 512 }
  Response: { "choices": [{ "message": { "role": "assistant", "content": "..." }, "finish_reason": "stop" }], "usage": {...} }
"""

from typing import Any, Dict, List, Optional, Tuple
from app.connectors.profiles.base import (
    BaseConnectorProfile,
    NormalizedTargetRequest,
    NormalizedTargetResponse,
)


class OpenAIChatProfile(BaseConnectorProfile):
    """Profile handler for OpenAI, Groq, Together, OpenRouter, and standard v1/chat/completions targets."""

    profile_name = "openai_chat_v1"
    profile_version = "1.0.0"

    def build_request(
        self,
        endpoint_url: str,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        extra_config: Optional[Dict[str, Any]] = None,
    ) -> NormalizedTargetRequest:
        messages: List[Dict[str, str]] = []
        if history:
            for turn in history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})

        config = extra_config or {}
        model = config.get("model") or "llama-3.3-70b-versatile"

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": config.get("temperature", 0.2),
            "max_tokens": config.get("max_tokens", 512),
        }
        if "extra_body" in config and isinstance(config["extra_body"], dict):
            payload.update(config["extra_body"])

        return NormalizedTargetRequest(
            url_path=endpoint_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            json_payload=payload,
        )

    def parse_response(self, response_json: Any, raw_text: str) -> NormalizedTargetResponse:
        if isinstance(response_json, dict):
            choices = response_json.get("choices")
            if choices and isinstance(choices, list) and len(choices) > 0:
                first_choice = choices[0]
                msg = first_choice.get("message", {}) if isinstance(first_choice, dict) else {}
                content = msg.get("content") or msg.get("reasoning_content") or ""
                finish_reason = first_choice.get("finish_reason") if isinstance(first_choice, dict) else None
                usage = response_json.get("usage", {})
                return NormalizedTargetResponse(
                    text=str(content or "").strip(),
                    raw_json=response_json,
                    finish_reason=finish_reason,
                    usage_metadata=usage if isinstance(usage, dict) else {},
                )
            elif "content" in response_json:
                return NormalizedTargetResponse(
                    text=str(response_json["content"]).strip(),
                    raw_json=response_json,
                )
        return NormalizedTargetResponse(
            text=raw_text.strip(),
            raw_json=response_json if isinstance(response_json, dict) else None,
        )

    def get_probe_payload(self) -> Tuple[str, Dict[str, Any]]:
        return "Hello", {
            "model": "default",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 16,
        }
