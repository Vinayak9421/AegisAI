"""Provenance metadata ingestion and response schemas."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProvenanceRequest(BaseModel):
    model_metadata: Dict[str, Any] = Field(..., description="Base model name, provider, fine-tuning notes")
    data_sources: Dict[str, Any] = Field(..., description="Inventory of data sources and licensing info")
    system_prompt_metadata: Dict[str, Any] = Field(..., description="System prompt documentation and safety constraints")
    operational_metadata: Dict[str, Any] = Field(..., description="Owner, version, contact, and limitations")
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list, description="Pointers to evidence documents")


class ProvenanceResponse(BaseModel):
    id: uuid.UUID
    target_id: uuid.UUID
    version: int
    model_metadata: Dict[str, Any]
    data_sources: Dict[str, Any]
    system_prompt_metadata: Dict[str, Any]
    operational_metadata: Dict[str, Any]
    evidence_refs: List[Dict[str, Any]]
    identity_score: Optional[float] = None
    score_version: str
    quality_flags: List[str]
    created_at: datetime.datetime
