"""Database connection and session management for MCP Server.

This module provides database connectivity to Neon Serverless PostgreSQL
with connection pooling and transaction support.
"""

import os
from typing import Generator
from sqlmodel import Session, create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create engine with connection pooling
# pool_size=10 supports 100+ concurrent tool invocations
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
)


def get_engine():
    """Get the database engine instance.

    Returns:
        Engine: SQLModel engine instance
    """
    return engine


def get_session() -> Generator[Session, None, None]:
    """Create a new database session with automatic cleanup.

    This function provides a database session that automatically commits
    on success and rolls back on error. Use with context manager or
    dependency injection.

    Yields:
        Session: SQLModel database session

    Example:
        with get_session() as session:
            task = session.get(Task, task_id)
    """
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db():
    """Initialize database connection and verify connectivity.

    This function should be called on server startup to ensure
    database is accessible before accepting tool invocations.

    Raises:
        Exception: If database connection fails
    """
    try:
        with Session(engine) as session:
            # Test connection with simple query
            session.exec("SELECT 1")
        print("[INFO] Database connection established")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        raise


def close_db():
    """Close database connection pool.

    This function should be called on server shutdown to ensure
    all connections are properly closed.
    """
    engine.dispose()
    print("[INFO] Database connection pool closed")
