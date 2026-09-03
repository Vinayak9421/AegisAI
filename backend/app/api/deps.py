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
