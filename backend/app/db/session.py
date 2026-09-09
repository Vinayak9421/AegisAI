"""Database engine initialization, session factory, and FastAPI DB dependency."""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base


def _create_database_engine():
    """Create database engine with resilient fallback to SQLite if PostgreSQL is unreachable."""
    db_url = settings.DATABASE_URL
    connect_args = {}
    if db_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    try:
        eng = create_engine(
            db_url,
            pool_size=settings.DATABASE_POOL_SIZE if not db_url.startswith("sqlite") else 5,
            max_overflow=settings.DATABASE_MAX_OVERFLOW if not db_url.startswith("sqlite") else 10,
            echo=settings.DATABASE_ECHO,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        # Test connection
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"Database connected successfully via {db_url.split('@')[-1] if '@' in db_url else 'SQLite'}")
        return eng
    except Exception as e:
        logger.warning(f"Failed to connect to configured DATABASE_URL ({e}). Falling back to local SQLite database.")
        sqlite_url = "sqlite:///./aegis.db"
        eng = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
        )
        return eng


engine = _create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables if they do not exist."""
    import app.db.models  # noqa
    Base.metadata.create_all(bind=engine)



def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency yielding short-lived database session.
    Automatically closes session upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Check database liveness without leaking internals."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

