"""Backward compatibility facade re-exporting Session and SessionTurn."""

from app.modules.evaluation.models import Session, SessionTurn

__all__ = ["Session", "SessionTurn"]
