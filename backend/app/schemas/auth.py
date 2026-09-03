"""Authentication and user session DTOs."""

import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.domain.enums import UserRole, UserStatus


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
    user_id: uuid.UUID
    tenant_id: uuid.UUID
    role: UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    role: UserRole
    status: UserStatus
    last_login_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
