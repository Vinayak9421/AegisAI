"""Central API v1 router mounting all modular domain routers."""

from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.benchmarks.router import router as benchmarks_router
from app.modules.evaluation.router import router as jobs_router
from app.modules.provenance.router import router as provenance_router
from app.modules.system.router import router as health_router
from app.modules.targets.router import router as targets_router

api_v1_router = APIRouter()

# Authentication & RBAC endpoints
api_v1_router.include_router(auth_router)

# Health endpoints mounted at v1
api_v1_router.include_router(health_router)

# Targets & credentials endpoints
api_v1_router.include_router(targets_router)

# Provenance & Identity Score endpoints
api_v1_router.include_router(provenance_router)

# Benchmark catalog & sampling endpoints
api_v1_router.include_router(benchmarks_router)

# Evaluation jobs & execution endpoints
api_v1_router.include_router(jobs_router)
