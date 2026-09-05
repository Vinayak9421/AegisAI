"""Benchmark service facade for backward compatibility."""

from app.modules.benchmarks.service import (
    BenchmarkService,
    compute_content_hash,
    compute_manifest_hash,
)

__all__ = ["BenchmarkService", "compute_content_hash", "compute_manifest_hash"]
