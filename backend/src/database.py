"""
Database connection and session management.
Uses SQLAlchemy engine with QueuePool for Neon Serverless PostgreSQL.
"""
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import QueuePool
from typing import Generator

from .config import get_settings

settings = get_settings()

# Create engine with QueuePool settings optimized for Neon Serverless PostgreSQL
# Based on research.md recommendations
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=5,              # Conservative for Neon free tier
    max_overflow=10,          # Total max: 15 connections
    pool_timeout=30,          # Wait 30s for available connection
    pool_recycle=1800,        # Recycle connections every 30 minutes (Neon idle timeout)
    pool_pre_ping=True,       # Verify connection health before use
    echo=settings.debug,      # Log SQL in debug mode
    connect_args={
        "connect_timeout": 10,
        "options": "-c statement_timeout=30000"  # 30 second query timeout
    }
)


def create_db_and_tables():
    """
    Create all database tables.
    Used for development; production uses Alembic migrations.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session.
    Session is automatically closed after request.
    """
    with Session(engine) as session:
        yield session
