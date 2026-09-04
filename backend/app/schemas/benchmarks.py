"""Benchmark source, test case ingestion, and sampling schemas."""

import datetime
import uuid
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.domain.enums import (
    BenchmarkSourceStatus,
    BenchmarkSourceType,
    JobMode,
    ReviewStatus,
    SeverityLevel,
    TestCaseMode,
)


# -----------------------------------------------------------------------------
# Input Schemas
# -----------------------------------------------------------------------------

class CreateBenchmarkSourceRequest(BaseModel):
    """Request payload to register an immutable benchmark source manifest."""

    name: str = Field(..., description="Display name, e.g. 'Finred Financial Red-Teaming Benchmark'")
    source_type: BenchmarkSourceType = Field(BenchmarkSourceType.DOMAIN_CUSTOM, description="EXTERNAL or DOMAIN_CUSTOM")
    external_ref: Optional[str] = Field(None, description="External reference URL or paper citation")
    revision: Optional[str] = Field("v1.0.0", description="Source revision tag or dataset commit")
    license_text: Optional[str] = Field(None, description="Dataset license, e.g. 'Apache-2.0' or 'Research Use Only'")


class CreateTestCaseRequest(BaseModel):
    """Request payload for a single test case prompt."""

    external_case_ref: Optional[str] = Field(None, description="Source-specific ID, e.g. 'R1_1_001'")
    category: str = Field(..., description="E.g. 'CYBERSECURITY_AUTH', 'FRAUD_FACILITATION', 'MARKET_MANIPULATION'")
    subcategory: str = Field(..., description="E.g. 'R1_1_2FA_BYPASS', 'R2_1_VISHING_EXTORTION'")
    prompt_template: str = Field(..., description="Raw attack prompt or template with placeholders")
    mode: TestCaseMode = Field(TestCaseMode.SINGLE, description="'SINGLE' turn or 'SESSION' multi-turn")
    variables_schema: Dict[str, Any] = Field(default_factory=dict, description="Variables schema for template rendering")
    session_script: Optional[Dict[str, Any]] = Field(None, description="Scripted multi-turn tree if mode is SESSION")
    owasp_ids: List[str] = Field(default_factory=list, description="List of mapped OWASP IDs (e.g. ['LLM01:PromptInjection'])")
    severity_ceiling: SeverityLevel = Field(SeverityLevel.HIGH, description="Max expected severity: CRITICAL, HIGH, MEDIUM, LOW")
    review_status: ReviewStatus = Field(ReviewStatus.APPROVED, description="APPROVED, PENDING, or REJECTED")
    language: Optional[str] = Field("en", description="Prompt language, default 'en'")
    metadata_payload: Dict[str, Any] = Field(default_factory=dict, description="Custom dataset tags and context")


class BatchIngestTestCasesRequest(BaseModel):
    """Batch ingestion request containing multiple test case prompts."""

    source_id: uuid.UUID = Field(..., description="Benchmark source UUID to associate test cases with")
    test_cases: List[CreateTestCaseRequest] = Field(..., description="List of test cases to ingest")


class SampleTestCasesRequest(BaseModel):
    """Request to sample test cases for an evaluation job."""

    mode: JobMode = Field(JobMode.QUICK, description="'QUICK' (lightweight ~25 prompts) or 'FULL' (~150-200 prompts)")
    categories: Optional[List[str]] = Field(None, description="Optional filter to specific risk categories")
    seed: int = Field(42, description="Pseudo-random seed for deterministic, reproducible sampling")
    sample_size: Optional[int] = Field(None, description="Explicit budget override (defaults to 25 for QUICK, 150 for FULL; capped at 200)")


# -----------------------------------------------------------------------------
# Response Schemas
# -----------------------------------------------------------------------------

class BenchmarkSourceResponse(BaseModel):
    """Details of a registered benchmark source."""

    id: uuid.UUID
    tenant_id: Optional[uuid.UUID] = None
    name: str
    source_type: BenchmarkSourceType
    external_ref: Optional[str] = None
    revision: Optional[str] = None
    manifest_hash: str
    status: BenchmarkSourceStatus
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class BenchmarkSourceSummaryResponse(BaseModel):
    """Benchmark source with aggregated statistics and category breakdown."""

    source: BenchmarkSourceResponse
    total_test_cases: int
    categories: Dict[str, int] = Field(default_factory=dict)
    severities: Dict[str, int] = Field(default_factory=dict)


class TestCaseResponse(BaseModel):
    """Individual attack test case entity."""

    id: uuid.UUID
    source_id: uuid.UUID
    external_case_ref: Optional[str] = None
    content_hash: str
    category: str
    subcategory: str
    mode: TestCaseMode
    prompt_template: str
    owasp_ids: List[str] = Field(default_factory=list)
    severity_ceiling: SeverityLevel
    review_status: ReviewStatus
    language: Optional[str] = "en"
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class IngestBatchResponse(BaseModel):
    """Outcome of a batch test case ingestion."""

    source_id: uuid.UUID
    ingested_count: int
    duplicate_count: int
    total_source_cases: int
    manifest_hash: str


class SampledTestCasesResponse(BaseModel):
    """Result of sampling test cases for an evaluation run."""

    mode: JobMode
    seed: int
    total_sampled: int
    category_distribution: Dict[str, int]
    test_cases: List[TestCaseResponse]
