"""Backward compatibility facade re-exporting AuthService from app.modules.auth.service."""

from app.modules.auth.service import AuthService

__all__ = ["AuthService"]
