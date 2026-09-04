"""Domain exceptions hierarchy for Aegis AI."""

from typing import Any, Dict, List, Optional


class AegisDomainError(Exception):
    """Base exception for all domain errors in Aegis AI."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or []


class NotFoundError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="NOT_FOUND", details=details)


class ForbiddenError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="FORBIDDEN", details=details)


class ConflictError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="CONFLICT", details=details)


class ValidationError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class PolicyBlockedError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="POLICY_BLOCKED", details=details)


class TargetUnavailableError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="TARGET_UNAVAILABLE", details=details)


class QuotaExhaustedError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="QUOTA_EXHAUSTED", details=details)


class JudgeUnavailableError(AegisDomainError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="JUDGE_UNAVAILABLE", details=details)


class AuthenticationError(AegisDomainError):
    def __init__(self, message: str = "Invalid credentials or expired session", details: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message, code="UNAUTHENTICATED", details=details)
