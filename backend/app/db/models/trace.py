"""Backward compatibility facade re-exporting TraceResult and TraceStage."""

from app.modules.evaluation.models import TraceResult, TraceStage

__all__ = ["TraceResult", "TraceStage"]
