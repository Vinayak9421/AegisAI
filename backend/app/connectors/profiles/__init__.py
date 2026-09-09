"""Connector profiles package for Aegis AI target integration."""

from app.connectors.profiles.base import (
    BaseConnectorProfile,
    NormalizedTargetRequest,
    NormalizedTargetResponse,
)
from app.connectors.profiles.aegis_simple_chat import AegisSimpleChatProfile
from app.connectors.profiles.openai_chat import OpenAIChatProfile
from app.connectors.profiles.registry import get_connector_profile

__all__ = [
    "BaseConnectorProfile",
    "NormalizedTargetRequest",
    "NormalizedTargetResponse",
    "AegisSimpleChatProfile",
    "OpenAIChatProfile",
    "get_connector_profile",
]
