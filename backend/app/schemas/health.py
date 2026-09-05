"""Backward compatibility facade re-exporting health schemas."""

from app.modules.system.schemas import HealthLiveResponse, HealthReadyResponse

__all__ = ["HealthLiveResponse", "HealthReadyResponse"]
