"""Domain interfaces / ports for connectors, judges, and provenance scoring."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ConnectorValidationReport(BaseModel):
    is_valid: bool
    status_message: str
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    resolved_host_hash: Optional[str] = None
    safe_error_class: Optional[str] = None


class ConnectorRequest(BaseModel):
    target_id: str
    request_id: str
    session_id: Optional[str] = None
    turn_number: Optional[int] = None
    message: str
    ordered_history: List[Dict[str, Any]] = Field(default_factory=list)
    timeout_budget_ms: int = 30000
    response_size_budget_bytes: int = 1048576  # 1MB
    request_trace: bool = False
    safe_metadata: Dict[str, Any] = Field(default_factory=dict)


class ConnectorResponse(BaseModel):
    text: Optional[str] = None
    structured_output: Optional[Dict[str, Any]] = None
    provider_request_id: Optional[str] = None
    session_identifier: Optional[str] = None
    status: str
    duration_ms: int
    usage_metadata: Dict[str, Any] = Field(default_factory=dict)
    trace_envelope: Optional[Dict[str, Any]] = None
    response_hash: str
    connector_version: str


class TargetConnectorPort(ABC):
    """Abstract port for all target execution adapters (Hosted, Local HF, Agent)."""

    @abstractmethod
    async def validate(self, configuration: Dict[str, Any]) -> ConnectorValidationReport:
        pass

    @abstractmethod
    async def invoke(self, request: ConnectorRequest) -> ConnectorResponse:
        pass

    @abstractmethod
    async def capabilities(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def redacted_description(self) -> Dict[str, Any]:
        pass


class JudgeInput(BaseModel):
    target_response: str
    test_case_prompt: str
    category: str
    intent: Optional[str] = None
    relevant_history: List[Dict[str, Any]] = Field(default_factory=list)
    trace_stage: Optional[Dict[str, Any]] = None
    rubric_version: str = "1.0.0"


class JudgeOutput(BaseModel):
    verdict: str
    severity: str
    category: str
    owasp_id: Optional[str] = None
    rationale: str
    confidence: Optional[float] = None
    rubric_version: str
    schema_version: str = "1.0.0"


class JudgePort(ABC):
    """Abstract port for independent judge execution."""

    @abstractmethod
    async def evaluate(self, input_data: JudgeInput) -> JudgeOutput:
        pass
