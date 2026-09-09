"""Connector factory resolving target connector implementations by mode."""

from typing import Optional
from app.connectors.hosted import HostedConnector
from app.core.errors import ValidationError
from app.db.models.target import Target
from app.domain.contracts import TargetConnectorPort
from app.domain.enums import TargetMode


class ConnectorFactory:
    """Instantiates appropriate TargetConnectorPort for a target."""

    @staticmethod
    def get_connector(target: Target, decrypted_credential: Optional[str] = None) -> TargetConnectorPort:
        if target.mode == TargetMode.HOSTED:
            if not target.endpoint_url:
                raise ValidationError("Hosted target must have endpoint_url specified")
            return HostedConnector(
                endpoint_url=target.endpoint_url,
                decrypted_credential=decrypted_credential,
                request_profile=target.request_profile,
                connector_profile_name=getattr(target, "connector_profile", "aegis_simple_chat_v1"),
            )
        elif target.mode == TargetMode.LOCAL_HF:
            raise ValidationError("LOCAL_HF mode connector will be enabled in a later phase")
        elif target.mode == TargetMode.AGENT:
            raise ValidationError("AGENT mode connector will be enabled in a later phase")
        else:
            raise ValidationError(f"Unknown target mode: {target.mode}")
