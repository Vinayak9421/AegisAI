"""Job creation, execution control, and progress schemas."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.domain.enums import JobMode, JobState


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
    authorization_confirmed: bool = Field(..., description="Must confirm authorization for red-team job execution")


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
