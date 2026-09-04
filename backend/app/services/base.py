"""Base service interface for Aegis AI domain services."""

from abc import ABC
from sqlalchemy.orm import Session


class BaseService(ABC):
    """Abstract base service carrying database session."""

    def __init__(self, db: Session):
        self.db = db
