"""Certificate schemas for trust and safety evaluation reports."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.domain.enums import CertificateStatus


class CertificateResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    target_name: Optional[str] = None
    certificate_number: str
    status: CertificateStatus
    version: int
    identity_score: Optional[float] = None
    trust_score: Optional[float] = None
    aer: Optional[float] = None
    shr: Optional[float] = None
    cmr: Optional[float] = None
    coverage_summary: Dict[str, Any]
    category_breakdown: Dict[str, Any]
    pillars: Optional[Dict[str, Any]] = None
    failures: List[Dict[str, Any]]
    recommendations: List[str]
    limitations: List[str]
    formula_versions: Dict[str, Any]
    trust_grade: Optional[str] = None
    report_hash: Optional[str] = None
    created_at: datetime.datetime
