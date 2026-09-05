"""Provenance metadata ingestion and response schemas."""

import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class ModelMetadata(BaseModel):
    model_name: str = Field(..., description="Base model name, e.g. 'meta-llama/Llama-3.3-70B-Instruct'")
    model_revision: Optional[str] = Field(None, description="Commit hash, tag, or version")
    provider: Optional[str] = Field(None, description="Model provider/organization, e.g. 'Meta', 'Mistral'")
    deployment_mode: Optional[str] = Field("hosted", description="'hosted', 'self-hosted', or 'cloud_api'")
    is_fine_tuned: Optional[bool] = Field(False, description="Whether the model has downstream fine-tuning")
    fine_tuning_details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="LoRA/adapter details")
    evidence_links: Optional[List[str]] = Field(default_factory=list, description="Model card URLs or evaluation reports")
    review_notes: Optional[str] = Field(None, description="Notes on safety reviews or benchmarks")


class DataSourceItem(BaseModel):
    source_id: str = Field(..., description="Unique source identifier")
    name: Optional[str] = Field(None, description="Dataset display name")
    purpose: str = Field(..., description="E.g. 'fintech_qna', 'customer_faqs', 'product_catalog'")
    license: Optional[str] = Field(None, description="E.g. 'Apache-2.0', 'MIT', 'Proprietary'")
    owner: Optional[str] = Field(None, description="Owning organization or vendor")
    version: Optional[str] = Field(None, description="Dataset release or revision")
    last_updated: Optional[str] = Field(None, description="ISO date or collection timestamp")


class DataSourcesMetadata(BaseModel):
    sources: List[DataSourceItem] = Field(default_factory=list, description="Inventory of data sources")
    rag_enabled: Optional[bool] = Field(False, description="Whether RAG knowledge retrieval is active")
    grounding_policy: Optional[str] = Field(None, description="Grounding and chunking strategy documentation")
    retrieval_not_applicable: Optional[bool] = Field(False, description="Set true if RAG is intentionally absent")


class SystemPromptMetadata(BaseModel):
    documented: bool = Field(True, description="Whether system prompt documentation is maintained")
    prompt_version: Optional[str] = Field(None, description="Prompt iteration/version tag")
    prompt_owner: Optional[str] = Field(None, description="Author or responsible engineer")
    safety_instructions: Optional[str] = Field(None, description="Declared safety instructions and guardrails")
    tool_constraints: Optional[str] = Field(None, description="Documented authority limits and tool access rules")
    tools_enabled: Optional[bool] = Field(True, description="Whether the bot has tool/function calling access")
    change_history: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Changelog entries")
    last_reviewed_at: Optional[str] = Field(None, description="Date of last prompt security review")
    known_limitations: Optional[str] = Field(None, description="Documented edge cases and known weaknesses")
    human_escalation_path: Optional[str] = Field(None, description="Procedure for escalating to human operators")


class OperationalMetadata(BaseModel):
    application_version: str = Field(..., description="Fintech application release version (e.g. '1.0.0')")
    contact_email: Optional[str] = Field(None, description="Responsible engineering or security team contact")
    evaluation_consent: bool = Field(True, description="Explicit confirmation that evaluation is authorized")
    evidence_freshness_date: Optional[str] = Field(None, description="Date when this metadata was declared/verified")
    known_limitations: Optional[str] = Field(None, description="Known operational limitations")


class EvidenceRef(BaseModel):
    title: str = Field(..., description="Evidence title")
    uri: str = Field(..., description="URL or document reference")
    evidence_type: str = Field("document", description="'document', 'benchmark', 'audit_report', 'card'")
    content_hash: Optional[str] = Field(None, description="SHA-256 hash of referenced document")


class ProvenanceRequest(BaseModel):
    model_metadata: Dict[str, Any] = Field(..., description="Base model name, provider, fine-tuning notes")
    data_sources: Dict[str, Any] = Field(..., description="Inventory of data sources and licensing info")
    system_prompt_metadata: Dict[str, Any] = Field(..., description="System prompt documentation and safety constraints")
    operational_metadata: Dict[str, Any] = Field(..., description="Owner, version, contact, and limitations")
    evidence_refs: List[Dict[str, Any]] = Field(default_factory=list, description="Pointers to evidence documents")


class DimensionScores(BaseModel):
    model_identity: float = Field(..., description="Score M (0-100, 30% weight)")
    data_provenance: float = Field(..., description="Score D (0-100, 35% weight)")
    system_configuration: float = Field(..., description="Score S (0-100, 25% weight)")
    operational_accountability: float = Field(..., description="Score O (0-100, 10% weight)")


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
    quality_flags: List[str] = Field(default_factory=list)
    dimension_scores: Optional[DimensionScores] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True
