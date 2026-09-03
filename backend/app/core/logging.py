"""Structured logging configuration with secret redaction and correlation ID tracking."""

import logging
import re
import sys
from typing import Any, Dict
from contextvars import ContextVar

# ContextVar for request correlation ID
correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")

# Sensitive patterns for redaction
REDACTION_PATTERNS = [
    re.compile(r"(api[-_]?key|password|secret|token|ciphertext|authorization)[\"']?\s*[:=]\s*[\"']?([^\s\"',]+)", re.IGNORECASE),
    re.compile(r"Bearer\s+([a-zA-Z0-9\-_.]+)", re.IGNORECASE),
]


class SensitiveDataFilter(logging.Filter):
    """Logging filter that scrubs tokens, passwords, and sensitive keys from log messages."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in REDACTION_PATTERNS:
                msg = pattern.sub(r"\1=***REDACTED***", msg)
            record.msg = msg
        return True


class CorrelationIdFormatter(logging.Formatter):
    """Formatter that appends the current request correlation ID to log lines."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = correlation_id_ctx.get()
        record.request_id = req_id if req_id else "system"
        return super().format(record)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("aegis")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid duplicate handlers on re-init
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = CorrelationIdFormatter(
            fmt="%(asctime)s [%(levelname)s] [req:%(request_id)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)
        logger.propagate = False
        
    return logger


logger = setup_logging()
