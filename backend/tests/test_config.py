"""Configuration and environment validation tests."""

import pytest
from app.core.config import Settings
from app.domain.enums import AppEnvironment


def test_settings_default_load():
    settings = Settings(
        APP_ENV=AppEnvironment.DEVELOPMENT,
        AUTH_SECRET="test_secret_key_for_unit_tests_12345",
    )
    assert settings.APP_NAME.startswith("Aegis AI")
    assert settings.API_V1_STR == "/api/v1"
    assert settings.DATABASE_POOL_SIZE == 10
    assert settings.KEY_VERSION == "v1"


def test_settings_cors_origins_parsing():
    settings = Settings(
        CORS_ORIGINS="http://localhost:3000,http://app.aegis.local",
        AUTH_SECRET="test_secret_key_for_unit_tests_12345",
    )
    assert len(settings.CORS_ORIGINS) == 2
    assert "http://localhost:3000" in settings.CORS_ORIGINS
    assert "http://app.aegis.local" in settings.CORS_ORIGINS


def test_production_readiness_rejects_insecure_defaults():
    settings = Settings(
        APP_ENV=AppEnvironment.PRODUCTION,
        AUTH_SECRET="change_this_default_secret_key",
        ALLOW_LOCAL_TARGETS_DEV=True,
    )
    with pytest.raises(ValueError, match="AUTH_SECRET"):
        settings.validate_production_readiness()
