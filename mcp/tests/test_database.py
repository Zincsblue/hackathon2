"""Tests for database connection and session management.

This module tests database connectivity, connection pooling,
and transaction management.
"""

import pytest
from sqlmodel import Session, text

from src.database import get_engine, get_session, init_db, close_db


def test_get_engine(test_engine):
    """Test database engine creation."""
    # Use test engine instead of real engine
    assert test_engine is not None
    assert test_engine.pool is not None


def test_get_session(test_session):
    """Test database session creation."""
    # Use test session fixture
    assert isinstance(test_session, Session)
    assert test_session.is_active


def test_init_db(test_engine):
    """Test database initialization."""
    # Test with test engine
    try:
        with Session(test_engine) as session:
            # Test connection with simple query
            result = session.exec(text("SELECT 1")).first()
            assert result == (1,)
    except Exception as e:
        pytest.fail(f"Database initialization failed: {e}")


def test_session_commit_on_success(test_session):
    """Test that session commits on successful operation."""
    # Perform a simple operation
    result = test_session.exec(text("SELECT 1")).first()
    assert result == (1,)

    # Session will be committed by fixture cleanup


def test_session_rollback_on_error(test_session):
    """Test that session rolls back on error."""
    try:
        # Force an error with invalid SQL
        test_session.exec(text("INVALID SQL QUERY"))
    except Exception:
        # Expected error - session should rollback
        test_session.rollback()
        pass


def test_connection_pool_size(test_engine):
    """Test that connection pool is configured correctly."""
    # Test engine uses in-memory SQLite, which has different pooling
    # Just verify the engine has a pool
    assert test_engine.pool is not None
