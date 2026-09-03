"""Base target connector port and registry foundation."""

from app.domain.contracts import (
    ConnectorRequest,
    ConnectorResponse,
    ConnectorValidationReport,
    TargetConnectorPort,
)

__all__ = [
    "TargetConnectorPort",
    "ConnectorRequest",
    "ConnectorResponse",
    "ConnectorValidationReport",
]
