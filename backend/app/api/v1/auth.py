"""Backward compatibility facade re-exporting auth router from app.modules.auth.router."""

from app.modules.auth.router import router

__all__ = ["router"]
