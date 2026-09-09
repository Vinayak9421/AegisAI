"""Target configuration, credential, and validation DTO schemas."""

import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field, model_validator
from app.domain.enums import ConnectorProfile, CredentialKind, CredentialStatus, TargetMode, TargetStatus


class CreateTargetRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=160)
    mode: TargetMode = TargetMode.HOSTED
    connector_profile: Optional[str] = Field("aegis_simple_chat_v1", description="Connector profile name")
    connector_profile_version: Optional[str] = Field("1.0.0", description="Profile version")
    endpoint_url: Optional[str] = None
    base_url: Optional[str] = None
    target_mode: Optional[str] = None
    model_ref: Optional[str] = None
    request_profile: Dict[str, Any] = Field(default_factory=dict)
    capabilities: Dict[str, Any] = Field(default_factory=dict)
    authorization_confirmed: bool = Field(True, description="Must explicitly confirm authorized target testing")
    authorization_reference: Optional[str] = Field(None, description="Email/ticket/repo permission reference")
    authorization_expires_at: Optional[datetime.datetime] = None
    side_effect_free: bool = Field(True, description="Must confirm target has no real-world side effects")
    allowed_test_categories: Optional[List[str]] = Field(default_factory=list)
    rate_limit_requests_per_minute: int = Field(10, ge=1, le=60)
    request_budget_per_job: int = Field(100, ge=1, le=500)
    credential_payload: Optional[str] = Field(None, description="Secret credential to encrypt at rest")
    credential_value: Optional[str] = None
    credential_kind: Optional[CredentialKind] = None
    auth_header_kind: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def normalize_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "base_url" in data and "endpoint_url" not in data:
                data["endpoint_url"] = data["base_url"]
            if "target_mode" in data and "mode" not in data:
                raw_mode = str(data["target_mode"]).upper()
                if "HOSTED" in raw_mode:
                    data["mode"] = TargetMode.HOSTED
                elif "LOCAL" in raw_mode or "HF" in raw_mode:
                    data["mode"] = TargetMode.LOCAL_HF
                else:
                    data["mode"] = TargetMode.HOSTED
            if "credential_value" in data and "credential_payload" not in data:
                data["credential_payload"] = data["credential_value"]
            if "auth_header_kind" in data and "credential_kind" not in data:
                raw_kind = str(data["auth_header_kind"]).upper()
                if "BEARER" in raw_kind:
                    data["credential_kind"] = CredentialKind.BEARER_TOKEN
                else:
                    data["credential_kind"] = CredentialKind.API_KEY
        return data

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
    connector_profile: Optional[str] = None
    endpoint_url: Optional[str] = None
    model_ref: Optional[str] = None
    request_profile: Optional[Dict[str, Any]] = None
    capabilities: Optional[Dict[str, Any]] = None
    authorization_reference: Optional[str] = None
    allowed_test_categories: Optional[List[str]] = None
    rate_limit_requests_per_minute: Optional[int] = Field(None, ge=1, le=60)
    request_budget_per_job: Optional[int] = Field(None, ge=1, le=500)


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
    connector_profile: Optional[str] = "aegis_simple_chat_v1"
    connector_profile_version: Optional[str] = "1.0.0"
    endpoint_url: Optional[str] = None
    model_ref: Optional[str] = None
    status: TargetStatus
    capabilities: Dict[str, Any]
    configuration_version: int
    authorization_confirmed_at: datetime.datetime
    authorization_reference: Optional[str] = None
    authorization_expires_at: Optional[datetime.datetime] = None
    side_effect_free: bool = True
    allowed_test_categories: List[str] = Field(default_factory=list)
    rate_limit_requests_per_minute: int = 10
    request_budget_per_job: int = 100
    validation_status: Optional[TargetStatus] = None
    validation_report: Dict[str, Any] = Field(default_factory=dict)
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
