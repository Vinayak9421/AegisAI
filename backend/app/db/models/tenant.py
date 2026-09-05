"""Backward compatibility facade re-exporting Auth & Tenant models from app.modules.auth.models."""

from app.modules.auth.models import Tenant, User, AuthSession

__all__ = ["Tenant", "User", "AuthSession"]
