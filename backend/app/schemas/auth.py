"""Backward compatibility facade re-exporting auth schemas from app.modules.auth.schemas."""

from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    UserSummary,
    TokenResponse,
    LoginResponse,
    UserResponse,
)

__all__ = [
    "LoginRequest",
    "RegisterRequest",
    "UserSummary",
    "TokenResponse",
    "LoginResponse",
    "UserResponse",
]
