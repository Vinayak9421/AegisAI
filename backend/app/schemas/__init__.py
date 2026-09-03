"""Consolidated schemas export."""

from app.schemas.common import (
    ApiErrorResponse,
    ApiResponse,
    ErrorBody,
    ErrorDetail,
    Page,
    ResponseMeta,
)
from app.schemas.health import HealthLiveResponse, HealthReadyResponse
from app.schemas.auth import LoginRequest, LoginResponse, UserResponse
from app.schemas.targets import (
    CreateTargetRequest,
    CredentialMetadataResponse,
    TargetResponse,
    TargetValidationResponse,
)
from app.schemas.provenance import ProvenanceRequest, ProvenanceResponse
from app.schemas.jobs import CreateJobRequest, JobProgressEvent, JobResponse
from app.schemas.results import (
    ResultAttemptResponse,
    SessionResponse,
    SessionTurnResponse,
    TestResultResponse,
)
from app.schemas.certificates import CertificateResponse
from app.schemas.benchmarks import BenchmarkSourceResponse, TestCaseResponse

__all__ = [
    "ApiResponse",
    "ApiErrorResponse",
    "ResponseMeta",
    "ErrorBody",
    "ErrorDetail",
    "Page",
    "HealthLiveResponse",
    "HealthReadyResponse",
    "LoginRequest",
    "LoginResponse",
    "UserResponse",
    "CreateTargetRequest",
    "TargetResponse",
    "TargetValidationResponse",
    "CredentialMetadataResponse",
    "ProvenanceRequest",
    "ProvenanceResponse",
    "CreateJobRequest",
    "JobResponse",
    "JobProgressEvent",
    "TestResultResponse",
    "ResultAttemptResponse",
    "SessionResponse",
    "SessionTurnResponse",
    "CertificateResponse",
    "BenchmarkSourceResponse",
    "TestCaseResponse",
]
