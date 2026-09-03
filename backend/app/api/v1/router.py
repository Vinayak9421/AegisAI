"""Central API v1 router registering all domain sub-routers."""

from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.targets import router as targets_router

api_v1_router = APIRouter()

# Health endpoints mounted at v1
api_v1_router.include_router(health_router)

# Targets & credentials endpoints
api_v1_router.include_router(targets_router)
