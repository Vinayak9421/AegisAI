"""Backward compatibility facade re-exporting Target models from app.modules.targets.models."""

from app.modules.targets.models import Target, TargetCredential

__all__ = ["Target", "TargetCredential"]
