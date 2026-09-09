"""FastAPI application entrypoint, middleware configuration, and lifecycle event handlers."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.error_handlers import register_error_handlers
from app.api.v1.health import router as health_router
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.logging import logger
from app.core.middleware import CorrelationIdMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and graceful shutdown lifecycle."""
    logger.info(f"Starting {settings.APP_NAME} in [{settings.APP_ENV.value}] mode")
    
    # Run production safety validations
    try:
        settings.validate_production_readiness()
    except ValueError as e:
        logger.warning(f"Production readiness check: {e}")

    # Initialize database tables and seed default demonstration users and workspace
    try:
        from app.db.session import SessionLocal, init_db
        from app.modules.auth.service import AuthService
        init_db()
        db = SessionLocal()
        try:
            AuthService(db).seed_default_users()
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Database initialization / seed default users at startup: {e}")

    yield

    logger.info(f"Shutting down {settings.APP_NAME}")


def create_application() -> FastAPI:
    """Build and configure the FastAPI application instance."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "Provenance-aware, application-level red-teaming and trust/safety "
            "evaluation platform for authorized fintech LLM applications."
        ),
        version="0.1.0",
        docs_url="/docs" if settings.APP_ENV != "production" else None,
        redoc_url="/redoc" if settings.APP_ENV != "production" else None,
        lifespan=lifespan,
    )

    # Middleware: Request ID correlation and timing
    app.add_middleware(CorrelationIdMiddleware)

    # Middleware: CORS
    if settings.CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Central error handlers (domain & HTTP exceptions translated to standard envelopes)
    register_error_handlers(app)

    # Mount top-level health probes (for container orchestrators / ALBs)
    app.include_router(health_router, prefix="", tags=["Health"])

    # Mount API v1 router
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)

    return app


app = create_application()
