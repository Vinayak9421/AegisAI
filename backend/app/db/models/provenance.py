"""Backward compatibility facade re-exporting ProvenanceRecord from app.modules.provenance.models."""

from app.modules.provenance.models import ProvenanceRecord

__all__ = ["ProvenanceRecord"]
