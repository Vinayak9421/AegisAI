"""Backward compatibility facade re-exporting job schemas."""

from app.modules.evaluation.schemas import (
    CreateJobRequest,
    JobProgressEvent,
    JobResponse,
)

__all__ = [
    "CreateJobRequest",
    "JobProgressEvent",
    "JobResponse",
]
