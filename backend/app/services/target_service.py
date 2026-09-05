"""Backward compatibility facade re-exporting TargetService from app.modules.targets.service."""

from app.modules.targets.service import TargetService

__all__ = ["TargetService"]
