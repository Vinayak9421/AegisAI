"""Base provenance normalizer and scorer interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Tuple


@dataclass
class ProvenanceScoreResult:
    """Rich container for provenance calculation results."""

    identity_score: float
    quality_flags: List[str] = field(default_factory=list)
    dimension_scores: Dict[str, float] = field(default_factory=dict)
    score_version: str = "identity_v1.0"

    def __iter__(self) -> Iterator[Any]:
        """Support unpacking as (identity_score, quality_flags)."""
        yield self.identity_score
        yield self.quality_flags


class ProvenanceScorerPort(ABC):
    """Port for computing versioned Identity Scores from declared metadata."""

    @abstractmethod
    def calculate_identity_score(
        self,
        model_metadata: Dict[str, Any],
        data_sources: Dict[str, Any],
        system_prompt_metadata: Dict[str, Any],
        operational_metadata: Dict[str, Any],
    ) -> ProvenanceScoreResult:
        pass

