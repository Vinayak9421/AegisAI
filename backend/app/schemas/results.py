"""Test result, attempt, and session result schemas."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.domain.enums import (
    AttemptPhase,
    AttemptStatus,
    JudgeStatus,
    SessionState,
    SeverityLevel,
    TargetResponseStatus,
    TurnRole,
    TurnState,
    Verdict,
)


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
