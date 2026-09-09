"""Base profile interface for target connectors."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel


class NormalizedTargetRequest(BaseModel):
    url_path: str = ""
    method: str = "POST"
    headers: Dict[str, str] = {}
    json_payload: Dict[str, Any] = {}


class NormalizedTargetResponse(BaseModel):
    text: str
    raw_json: Optional[Dict[str, Any]] = None
    finish_reason: Optional[str] = None
    usage_metadata: Dict[str, Any] = {}
    trace_data: Optional[Dict[str, Any]] = None


class BaseConnectorProfile(ABC):
    """Abstract connector profile defining request shaping and response parsing."""

    profile_name: str
    profile_version: str = "1.0.0"

    @abstractmethod
    def build_request(
        self,
        endpoint_url: str,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        extra_config: Optional[Dict[str, Any]] = None,
    ) -> NormalizedTargetRequest:
        """Format request payload and headers according to connector profile."""
        pass

    @abstractmethod
    def parse_response(self, response_json: Any, raw_text: str) -> NormalizedTargetResponse:
        """Extract assistant text and metadata from target response."""
        pass

    @abstractmethod
    def get_probe_payload(self) -> Tuple[str, Dict[str, Any]]:
        """Return benign test prompt and minimal payload for target validation."""
        pass
