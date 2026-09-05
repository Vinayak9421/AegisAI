"""Backward compatibility facade re-exporting jobs router."""

from app.modules.evaluation.router import router

__all__ = ["router"]
