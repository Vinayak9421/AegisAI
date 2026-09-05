"""Backward compatibility facade re-exporting ProvenanceService from app.modules.provenance.service."""

from app.modules.provenance.service import ProvenanceService

__all__ = ["ProvenanceService"]
