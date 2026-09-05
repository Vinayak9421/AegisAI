"""FastAPI dependency injection providers."""

import uuid
from typing import Generator, Optional
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.logging import correlation_id_ctx
from app.db.session import get_db
from app.db.models.tenant import User, Tenant
from app.domain.enums import UserRole, UserStatus


def get_request_id(request: Request) -> str:
    """Extract or return current request correlation ID."""
    return getattr(request.state, "request_id", None) or correlation_id_ctx.get() or str(uuid.uuid4())


def get_current_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")
) -> Optional[uuid.UUID]:
    """Extract tenant ID from request header for tenant-scoped operations."""
    if x_tenant_id:
        try:
            return uuid.UUID(x_tenant_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid X-Tenant-ID header format",
            )
    return None


def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate JWT Bearer token from Authorization header.
    Returns authenticated User model.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ", 1)[1].strip()
    from app.services.auth_service import AuthService
    payload = AuthService.decode_access_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User account is {user.status.value.lower()}",
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure authenticated user has ADMIN role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required to perform this action",
        )
    return current_user
