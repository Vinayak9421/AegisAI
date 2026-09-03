"""Benchmark source and test case schemas."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.domain.enums import BenchmarkSourceStatus, BenchmarkSourceType, ReviewStatus, SeverityLevel, TestCaseMode


class BenchmarkSourceResponse(BaseModel):
    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    name: str
    source_type: BenchmarkSourceType
    external_ref: Optional[str] = None
    revision: Optional[str] = None
    manifest_hash: str
    status: BenchmarkSourceStatus
    created_at: datetime.datetime


class TestCaseResponse(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    external_case_ref: Optional[str] = None
    content_hash: str
    category: str
    subcategory: str
    mode: TestCaseMode
    prompt_template: str
    owasp_ids: List[str]
    severity_ceiling: SeverityLevel
    review_status: ReviewStatus
    created_at: datetime.datetime
