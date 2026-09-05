"""Backward compatibility facade re-exporting health router."""

from app.modules.system.router import router

__all__ = ["router"]
