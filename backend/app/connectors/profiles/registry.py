"""Connector profile registry for resolving profile handlers."""

from typing import Dict, Optional
from app.connectors.profiles.aegis_simple_chat import AegisSimpleChatProfile
from app.connectors.profiles.base import BaseConnectorProfile
from app.connectors.profiles.openai_chat import OpenAIChatProfile
from app.domain.enums import ConnectorProfile


_REGISTRY: Dict[str, BaseConnectorProfile] = {
    ConnectorProfile.AEGIS_SIMPLE_CHAT_V1.value: AegisSimpleChatProfile(),
    ConnectorProfile.OPENAI_CHAT_V1.value: OpenAIChatProfile(),
    "aegis_simple_chat_v1": AegisSimpleChatProfile(),
    "openai_chat_v1": OpenAIChatProfile(),
}


def get_connector_profile(profile_name: Optional[str]) -> BaseConnectorProfile:
    """Resolve connector profile instance by name with fallback to AegisSimpleChatProfile."""
    if not profile_name:
        return _REGISTRY[ConnectorProfile.AEGIS_SIMPLE_CHAT_V1.value]

    normalized = str(profile_name).lower().strip()
    if normalized in _REGISTRY:
        return _REGISTRY[normalized]

    # Flexible matching
    if "openai" in normalized or "completions" in normalized:
        return _REGISTRY[ConnectorProfile.OPENAI_CHAT_V1.value]

    return _REGISTRY[ConnectorProfile.AEGIS_SIMPLE_CHAT_V1.value]
