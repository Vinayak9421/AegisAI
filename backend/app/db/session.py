from pathlib import Path
from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings
from app.core.logging import logger
from app.db.base import Base

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
SQLITE_DB_PATH = BACKEND_DIR / "aegis.db"
FALLBACK_SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH.as_posix()}"


import sqlite3


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable WAL mode, foreign keys, and busy timeout for concurrent SQLite stability."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        try:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=15000")
            cursor.close()
        except Exception:
            pass


def _create_database_engine():
    """Create database engine with resilient fallback to SQLite if PostgreSQL is unreachable."""
    db_url = settings.DATABASE_URL
    is_sqlite = db_url.startswith("sqlite")
    connect_args = {"check_same_thread": False, "timeout": 30.0} if is_sqlite else {"connect_timeout": 3}

    try:
        eng = create_engine(
            db_url,
            pool_size=settings.DATABASE_POOL_SIZE if not is_sqlite else 5,
            max_overflow=settings.DATABASE_MAX_OVERFLOW if not is_sqlite else 10,
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
        logger.warning(f"Failed to connect to configured DATABASE_URL ({e}). Falling back to local SQLite database at {FALLBACK_SQLITE_URL}.")
        eng = create_engine(
            FALLBACK_SQLITE_URL,
            connect_args={"check_same_thread": False, "timeout": 30.0},
            echo=settings.DATABASE_ECHO,
            pool_pre_ping=True,
        )
        return eng


engine = _create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create all database tables if they do not exist."""
    import app.db.models  # noqa: F401
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

