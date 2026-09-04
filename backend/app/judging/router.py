"""Judge router resolving independent judge adapters by provider name."""

from typing import Optional
from app.core.config import settings
from app.domain.contracts import JudgePort
from app.judging.groq_judge import GroqJudgeAdapter


class JudgeRouter:
    """Factory and router for resolving independent evaluation judges."""

    def __init__(self, default_provider: Optional[str] = None):
        self.default_provider = default_provider or settings.JUDGE_PROVIDER

    def get_judge(self, provider: Optional[str] = None) -> JudgePort:
        """Resolve judge adapter by provider name."""
        prov = (provider or self.default_provider).lower()
        if prov in ("groq", "llama-3.3-70b", "llama"):
            return GroqJudgeAdapter()
        elif prov in ("mock", "heuristic", "offline"):
            return GroqJudgeAdapter(api_key="mock_test_key")
        else:
            return GroqJudgeAdapter()


# Global judge router singleton
judge_router = JudgeRouter()
