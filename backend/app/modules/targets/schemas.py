"""Target configuration, credential, and validation DTO schemas."""

import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, model_validator
from app.domain.enums import CredentialKind, CredentialStatus, TargetMode, TargetStatus


class CreateTargetRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=160)
    mode: TargetMode
    endpoint_url: Optional[str] = None
    model_ref: Optional[str] = None
    request_profile: Dict[str, Any] = Field(default_factory=dict)
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    authorization_confirmed: bool = Field(..., description="Must explicitly confirm authorized target testing")
    credential_payload: Optional[str] = Field(None, description="Secret credential to encrypt at rest")
    credential_kind: Optional[CredentialKind] = None

    @model_validator(mode="after")
    def validate_target_mode_shape(self) -> "CreateTargetRequest":
        if not self.authorization_confirmed:
            raise ValueError("Evaluation authorization must be explicitly confirmed")
        if self.mode == TargetMode.HOSTED and not self.endpoint_url:
            raise ValueError("endpoint_url is required for HOSTED mode targets")
        if self.mode == TargetMode.LOCAL_HF and not self.model_ref:
            raise ValueError("model_ref is required for LOCAL_HF mode targets")
        return self


class PatchTargetRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=160)
    endpoint_url: Optional[str] = None
    model_ref: Optional[str] = None
    request_profile: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None


class AddCredentialRequest(BaseModel):
    kind: CredentialKind = CredentialKind.API_KEY
    secret: str = Field(..., min_length=1, description="Secret API key / token to encrypt at rest")


class TargetValidationRequest(BaseModel):
    check_capabilities: bool = True
    timeout_override_seconds: Optional[float] = None


class TargetResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    mode: TargetMode
    endpoint_url: Optional[str] = None
    model_ref: Optional[str] = None
    status: TargetStatus
    capabilities: Dict[str, Any]
    configuration_version: int
    authorization_confirmed_at: datetime.datetime
    verified_at: Optional[datetime.datetime] = None
    last_validated_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class TargetValidationResponse(BaseModel):
    target_id: uuid.UUID
    status: TargetStatus
    resolved_host_hash: Optional[str] = None
    capability_report: Dict[str, Any] = Field(default_factory=dict)
    safe_error_class: Optional[str] = None
    latency_ms: Optional[float] = None
    checked_at: datetime.datetime


class CredentialMetadataResponse(BaseModel):
    id: uuid.UUID
    target_id: uuid.UUID
    kind: CredentialKind
    secret_last4: Optional[str] = None
    status: CredentialStatus
    expires_at: Optional[datetime.datetime] = None
    revoked_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
