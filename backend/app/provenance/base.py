"""Base provenance normalizer and scorer interface."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple


class ProvenanceScorerPort(ABC):
    """Port for computing versioned Identity Scores from declared metadata."""

    @abstractmethod
    def calculate_identity_score(
        self,
        model_metadata: Dict[str, Any],
        data_sources: Dict[str, Any],
        system_prompt_metadata: Dict[str, Any],
        operational_metadata: Dict[str, Any],
    ) -> Tuple[float, List[str]]:
        pass
