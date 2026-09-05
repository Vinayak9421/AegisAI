"""System health check response schemas."""

from typing import Optional
from pydantic import BaseModel
from app.domain.enums import AppEnvironment


class HealthLiveResponse(BaseModel):
    status: str
    environment: AppEnvironment
    version: str = "0.1.0"


class HealthReadyResponse(BaseModel):
    status: str
    database: str
    environment: AppEnvironment
