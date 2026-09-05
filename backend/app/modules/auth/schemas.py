"""Pydantic schemas for authentication, registration, and user identity."""

import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field

from app.domain.enums import UserRole, UserStatus


class LoginRequest(BaseModel):
    """Payload to authenticate an existing user or admin."""

    email: EmailStr = Field(..., description="User account email address")
    password: str = Field(..., min_length=6, description="Account plaintext password")


class RegisterRequest(BaseModel):
    """Payload to register a new user and create or bind to tenant."""

    email: EmailStr = Field(..., description="Corporate or user email address")
    password: str = Field(..., min_length=6, description="Account password (min 6 characters)")
    organization_name: Optional[str] = Field(
        None, max_length=160, description="Optional organization name. Defaults to personal workspace if omitted."
    )


class UserSummary(BaseModel):
    """Safe, non-sensitive summary of user identity."""

    id: uuid.UUID
    email: str
    role: UserRole
    status: UserStatus
    tenant_id: uuid.UUID
    tenant_name: str
    last_login_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Bearer access token payload returned upon successful auth."""

    access_token: str = Field(..., description="Signed JWT Bearer access token")
    token_type: str = Field("bearer", description="Token schema type")
    expires_in: int = Field(..., description="Seconds until token expiration")
    user: UserSummary = Field(..., description="Authenticated user profile")


# Aliases for compatibility
LoginResponse = TokenResponse
UserResponse = UserSummary
