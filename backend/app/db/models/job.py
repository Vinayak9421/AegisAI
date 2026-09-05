"""Backward compatibility facade re-exporting Job and JobItem models."""

from app.modules.evaluation.models import Job, JobItem

__all__ = ["Job", "JobItem"]
