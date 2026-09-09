"""Typed application configuration for Aegis AI."""

import json
from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.domain.enums import AppEnvironment


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # General / Application
    APP_NAME: str = "Aegis AI — Trust & Safety Red-Teaming Platform"
    APP_ENV: AppEnvironment = AppEnvironment.DEVELOPMENT
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/aegis_ai"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_ECHO: bool = False
    DATABASE_SSL_MODE: Optional[str] = None

    # Authentication & Session
    AUTH_SECRET: str = "change_this_in_production_super_secret_key_minimum_32_bytes_long"
    AUTH_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14

    # Data Encryption (Envelope encryption for target credentials)
    ENCRYPTION_KEY: str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    KEY_VERSION: str = "v1"

    # Queue & Worker (Redis optional for Phase 1)
    REDIS_URL: Optional[str] = None
    QUEUE_NAME: str = "aegis_jobs"
    WORKER_CONCURRENCY: int = 4
    LEASE_DURATION_SECONDS: int = 300

    # Target Connector Defaults
    TARGET_CONNECT_TIMEOUT: float = 10.0
    TARGET_READ_TIMEOUT: float = 30.0
    TARGET_MAX_RESPONSE_BYTES: int = 1048576  # 1MB
    TARGET_DEFAULT_RATE_LIMIT: int = 60  # requests per minute
    ALLOW_LOCAL_TARGETS_DEV: bool = True
    ALLOWED_EGRESS_DOMAINS: Union[List[str], str] = ["api.openai.com", "api.groq.com", "api.anthropic.com"]

    # Judge Configuration
    JUDGE_PROVIDER: str = "groq"
    JUDGE_API_KEY: Optional[str] = None
    JUDGE_MODEL: str = "llama-3.3-70b-versatile"
    JUDGE_TIMEOUT: float = 30.0
    JUDGE_RETRY_BUDGET: int = 2

    # Retention & Privacy
    RAW_EVIDENCE_RETENTION_DAYS: int = 90
    AUDIT_RETENTION_DAYS: int = 365
    EXPORT_TTL_SECONDS: int = 3600

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [i.strip() for i in v_stripped.split(",") if i.strip()]
        return v

    @field_validator("ALLOWED_EGRESS_DOMAINS", mode="after")
    @classmethod
    def assemble_egress_domains(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            v_stripped = v.strip()
            if v_stripped.startswith("[") and v_stripped.endswith("]"):
                try:
                    return json.loads(v_stripped)
                except Exception:
                    pass
            return [i.strip() for i in v_stripped.split(",") if i.strip()]
        return v

    def validate_production_readiness(self) -> None:
        """Validate safety constraints for production deployment."""
        if self.APP_ENV == AppEnvironment.PRODUCTION:
            if "change_this" in self.AUTH_SECRET or len(self.AUTH_SECRET) < 32:
                raise ValueError("AUTH_SECRET must be set to a cryptographically secure key in production")
            if self.ALLOW_LOCAL_TARGETS_DEV:
                raise ValueError("ALLOW_LOCAL_TARGETS_DEV must be False in production to prevent SSRF vulnerabilities")


settings = Settings()
