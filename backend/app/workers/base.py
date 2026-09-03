"""Base evaluation worker interfaces."""

from abc import ABC, abstractmethod
import uuid


class EvaluationWorkerPort(ABC):
    """Port for evaluation worker task execution and recovery."""

    @abstractmethod
    async def process_job(self, job_id: uuid.UUID) -> None:
        pass

    @abstractmethod
    async def recover_expired_leases(self) -> int:
        pass
