"""Backward compatibility facade re-exporting result schemas."""

from app.modules.evaluation.schemas import (
    ResultAttemptResponse,
    SessionResponse,
    SessionTurnResponse,
    TestResultResponse,
)

__all__ = [
    "ResultAttemptResponse",
    "SessionResponse",
    "SessionTurnResponse",
    "TestResultResponse",
]
