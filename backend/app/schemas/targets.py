"""Backward compatibility facade re-exporting Target schemas from app.modules.targets.schemas."""

from app.modules.targets.schemas import (
    CreateTargetRequest,
    PatchTargetRequest,
    AddCredentialRequest,
    TargetValidationRequest,
    TargetResponse,
    TargetValidationResponse,
    CredentialMetadataResponse,
)

__all__ = [
    "CreateTargetRequest",
    "PatchTargetRequest",
    "AddCredentialRequest",
    "TargetValidationRequest",
    "TargetResponse",
    "TargetValidationResponse",
    "CredentialMetadataResponse",
]
