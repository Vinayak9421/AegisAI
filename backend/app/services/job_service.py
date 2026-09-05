"""Backward compatibility facade re-exporting JobService."""

from app.modules.evaluation.service import JobService

__all__ = ["JobService"]
