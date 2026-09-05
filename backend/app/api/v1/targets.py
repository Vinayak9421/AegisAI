"""Backward compatibility facade re-exporting targets router from app.modules.targets.router."""

from app.modules.targets.router import router, get_or_create_default_principal

__all__ = ["router", "get_or_create_default_principal"]
