"""Job, evaluation, and test result schemas."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.domain.enums import (
    AttemptPhase,
    AttemptStatus,
    JobMode,
    JobState,
    JudgeStatus,
    SessionState,
    SeverityLevel,
    TargetResponseStatus,
    TurnRole,
    TurnState,
    Verdict,
)


class CreateJobRequest(BaseModel):
    target_id: uuid.UUID
    mode: JobMode = JobMode.QUICK
    source_ids: List[uuid.UUID] = Field(default_factory=list)
    sampling_seed: Optional[int] = None
    category_filters: List[str] = Field(default_factory=list)
    include_sessions: bool = False
    include_traces: bool = False
    judge_profile: Dict[str, Any] = Field(default_factory=dict)
    retention_profile: Dict[str, Any] = Field(default_factory=dict)
    authorization_confirmed: bool = Field(True, description="Must confirm authorization for red-team job execution")


class JobResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    target_id: uuid.UUID
    created_by: uuid.UUID
    mode: JobMode
    state: JobState
    total_items: int
    completed_items: int
    failed_items: int
    progress_percentage: float = 0.0
    scoring_version: str
    sampling_seed: int
    started_at: Optional[datetime.datetime] = None
    finished_at: Optional[datetime.datetime] = None
    error_summary: Optional[Dict[str, Any]] = None
    trust_score: Optional[float] = None
    trust_grade: Optional[str] = None
    created_at: datetime.datetime


class JobProgressEvent(BaseModel):
    job_id: uuid.UUID
    state: JobState
    completed_items: int
    total_items: int
    failed_items: int
    current_category: Optional[str] = None
    event_time: datetime.datetime
    safe_error_class: Optional[str] = None


class TestResultResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    job_item_id: uuid.UUID
    test_case_id: uuid.UUID
    session_id: Optional[uuid.UUID] = None
    turn_number: Optional[int] = None
    target_status: TargetResponseStatus
    judge_status: JudgeStatus
    verdict: Optional[Verdict] = None
    severity: Optional[SeverityLevel] = None
    category: Optional[str] = None
    owasp_id: Optional[str] = None
    rationale: Optional[str] = None
    confidence: Optional[float] = None
    rubric_version: Optional[str] = None
    judge_model: Optional[str] = None
    logical_key: str
    attack_prompt: Optional[str] = None
    target_response: Optional[str] = None
    response_text: Optional[str] = None
    created_at: datetime.datetime


class ResultAttemptResponse(BaseModel):
    id: uuid.UUID
    job_item_id: uuid.UUID
    attempt_no: int
    phase: AttemptPhase
    status: AttemptStatus
    provider_request_id: Optional[str] = None
    error_class: Optional[str] = None
    started_at: datetime.datetime
    finished_at: Optional[datetime.datetime] = None


class SessionResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    target_id: uuid.UUID
    test_case_id: uuid.UUID
    state: SessionState
    script_version: str
    current_turn: int
    max_turns: int
    termination_reason: Optional[str] = None
    created_at: datetime.datetime


class SessionTurnResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    turn_number: int
    role: TurnRole
    prompt_text: str
    state: TurnState
    created_at: datetime.datetime
