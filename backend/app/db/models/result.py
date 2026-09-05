"""Backward compatibility facade re-exporting TestResult, ResultAttempt, and JudgeEvaluation."""

from app.modules.evaluation.models import TestResult, ResultAttempt, JudgeEvaluation

__all__ = ["TestResult", "ResultAttempt", "JudgeEvaluation"]
