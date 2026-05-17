"""
database.py — PostgreSQL database engine, session factory, and Base.

Uses SQLAlchemy 2.x with a connection pool tuned for production workloads.
The `get_db` dependency is used by FastAPI route handlers via Depends().
"""

from __future__ import annotations

import logging

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from typing import Generator

from config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


# ─── Engine ────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,      # Detect broken connections before use
    pool_size=10,            # Baseline persistent connections
    max_overflow=20,         # Extra connections under high load
    pool_recycle=1800,       # Recycle connections every 30 minutes
    echo=settings.db_echo,   # SQL logging (set DB_ECHO=true in .env for debug)
)


# ─── Session factory ───────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ─── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this base class."""
    pass


# ─── Dependency ────────────────────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session per request.
    Always closes the session after the request, even on errors.
    """
    db: Session = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ─── Startup utility ───────────────────────────────────────────────────────────
def create_tables() -> None:
    """
    Create all registered ORM tables if they do not already exist.
    Called once at application startup.
    """
    # Import models here to ensure they are registered with Base
    from models import Ticket  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified / created successfully.")


def verify_connection() -> bool:
    """Verify the database connection is reachable. Used in health checks."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.error(f"Database connection check failed: {exc}")
        return False
