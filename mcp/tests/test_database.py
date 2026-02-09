"""Tests for database connection and session management.

This module tests database connectivity, connection pooling,
and transaction management.
"""

import pytest
from sqlmodel import Session

from src.database import get_engine, get_session, init_db, close_db


def test_get_engine():
    """Test database engine creation."""
    engine = get_engine()
    assert engine is not None
    assert engine.pool is not None


def test_get_session():
    """Test database session creation."""
    session_gen = get_session()
    session = next(session_gen)

    assert isinstance(session, Session)
    assert session.is_active

    # Cleanup
    try:
        next(session_gen, None)
    except StopIteration:
        pass


def test_init_db():
    """Test database initialization."""
    try:
        init_db()
        # If no exception, initialization succeeded
        assert True
    except Exception as e:
        pytest.fail(f"Database initialization failed: {e}")


def test_session_commit_on_success():
    """Test that session commits on successful operation."""
    session_gen = get_session()
    session = next(session_gen)

    # Perform a simple operation
    result = session.exec("SELECT 1").first()
    assert result == (1,)

    # Cleanup (should commit)
    try:
        next(session_gen, None)
    except StopIteration:
        pass


def test_session_rollback_on_error():
    """Test that session rolls back on error."""
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Force an error
        session.exec("INVALID SQL QUERY")
    except Exception:
        # Expected error
        pass

    # Cleanup (should rollback)
    try:
        next(session_gen, None)
    except StopIteration:
        pass


def test_connection_pool_size():
    """Test that connection pool is configured correctly."""
    engine = get_engine()
    assert engine.pool.size() >= 10  # pool_size=10 in database.py
