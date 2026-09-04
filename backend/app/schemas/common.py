"""Standard API response envelopes, error structures, and pagination schemas."""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseMeta(BaseModel):
    """Metadata envelope for API responses."""

    request_id: str
    timestamp: Optional[str] = None


class ApiResponse(BaseModel, Generic[T]):
    """Standard success envelope: { 'data': ..., 'meta': {'request_id': '...'} }."""

    data: T
    meta: ResponseMeta


class ErrorDetail(BaseModel):
    """Granular field-level error detail."""

    field: Optional[str] = None
    issue: str


class ErrorBody(BaseModel):
    """Standard error body: { 'code': '...', 'message': '...', 'details': [...], 'request_id': '...' }."""

    code: str
    message: str
    details: List[Dict[str, Any]] = Field(default_factory=list)
    request_id: str


class ApiErrorResponse(BaseModel):
    """Standard top-level error envelope."""

    error: ErrorBody


class Page(BaseModel, Generic[T]):
    """Cursor or offset pagination container."""

    items: List[T]
    next_cursor: Optional[str] = None
    total_estimate: Optional[int] = None
