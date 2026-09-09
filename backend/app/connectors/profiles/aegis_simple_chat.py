"""Aegis Simple Chat Profile (aegis_simple_chat_v1).

Format:
  Request: POST /chat { "message": "...", "session_id": "...", "history": [...], "request_id": "..." }
  Response: { "reply": "...", "session_id": "...", "metadata": {...}, "trace": null }
"""

from typing import Any, Dict, List, Optional, Tuple
from app.connectors.profiles.base import (
    BaseConnectorProfile,
    NormalizedTargetRequest,
    NormalizedTargetResponse,
)


class AegisSimpleChatProfile(BaseConnectorProfile):
    """Profile handler for custom FastAPI/Flask/Node chatbots conforming to the Aegis chat contract."""

    profile_name = "aegis_simple_chat_v1"
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
        payload: Dict[str, Any] = {
            "message": prompt,
            "session_id": session_id,
            "history": history or [],
            "request_id": request_id,
        }
        if extra_config and "extra_body" in extra_config:
            payload.update(extra_config["extra_body"])

        return NormalizedTargetRequest(
            url_path=endpoint_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            json_payload=payload,
        )

    def parse_response(self, response_json: Any, raw_text: str) -> NormalizedTargetResponse:
        if isinstance(response_json, dict):
            reply_text = (
                response_json.get("answer")
                or response_json.get("reply")
                or response_json.get("response")
                or response_json.get("message")
            )
            if not reply_text and "choices" in response_json and isinstance(response_json["choices"], list) and len(response_json["choices"]) > 0:
                choice = response_json["choices"][0]
                if isinstance(choice, dict):
                    msg = choice.get("message", {})
                    reply_text = msg.get("content") if isinstance(msg, dict) else choice.get("text")
            if not reply_text:
                reply_text = response_json.get("output") or response_json.get("content")

            if reply_text is not None:
                return NormalizedTargetResponse(
                    text=str(reply_text).strip(),
                    raw_json=response_json,
                    usage_metadata=response_json.get("metadata", {}),
                    trace_data=response_json.get("trace"),
                )
        return NormalizedTargetResponse(
            text=raw_text.strip(),
            raw_json=response_json if isinstance(response_json, dict) else None,
        )

    def get_probe_payload(self) -> Tuple[str, Dict[str, Any]]:
        return "Hello", {"message": "Hello", "session_id": "validation-probe", "history": []}
