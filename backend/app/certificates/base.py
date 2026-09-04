"""Base certificate generator and masking interfaces."""

from abc import ABC, abstractmethod
import uuid
from typing import Any, Dict


class CertificateBuilderPort(ABC):
    """Port for building immutable Trust & Safety certificates."""

    @abstractmethod
    def build_certificate_data(self, job_id: uuid.UUID) -> Dict[str, Any]:
        pass

    @abstractmethod
    def mask_evidence(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        pass
