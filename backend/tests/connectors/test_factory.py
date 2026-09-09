import pytest
from app.connectors.factory import ConnectorFactory
from app.connectors.hosted import HostedConnector
from app.connectors.local_hf import LocalHFConnector
from app.core.errors import ValidationError
from app.db.models.target import Target
from app.domain.enums import TargetMode

def test_factory_hosted():
    target = Target(
        mode=TargetMode.HOSTED,
        endpoint_url="http://example.com/api",
        connector_profile="aegis_simple_chat_v1"
    )
    connector = ConnectorFactory.get_connector(target)
    assert isinstance(connector, HostedConnector)
    assert connector.raw_endpoint_url == "http://example.com/api"

def test_factory_local_hf():
    target = Target(
        mode=TargetMode.LOCAL_HF,
        endpoint_url="http://localhost:8001/chat",
        model_ref="small_instruct_local_v1"
    )
    connector = ConnectorFactory.get_connector(target)
    assert isinstance(connector, LocalHFConnector)
    assert connector.endpoint_url == "http://localhost:8001/chat"
    assert connector.model_ref == "small_instruct_local_v1"

def test_factory_local_hf_missing_endpoint():
    target = Target(
        mode=TargetMode.LOCAL_HF,
        model_ref="small_instruct_local_v1"
    )
    with pytest.raises(ValidationError, match="endpoint_url specified"):
        ConnectorFactory.get_connector(target)

def test_factory_local_hf_missing_model_ref():
    target = Target(
        mode=TargetMode.LOCAL_HF,
        endpoint_url="http://localhost:8001/chat"
    )
    with pytest.raises(ValidationError, match="model_ref specified"):
        ConnectorFactory.get_connector(target)
