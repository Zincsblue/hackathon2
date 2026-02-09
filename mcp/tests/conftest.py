"""Pytest configuration and fixtures for MCP Server tests.

This module provides shared fixtures for database sessions, test users,
and test tasks.
"""

import pytest
import os
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool
from datetime import datetime

from src.models import Task


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_engine():
    """Create a test database engine with in-memory SQLite.

    Yields:
        Engine: SQLModel engine for testing
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={
            "check_same_thread": False,
            "timeout": 30.0  # Increase timeout for concurrent operations
        },
        poolclass=StaticPool  # Use StaticPool for in-memory SQLite
    )

    # Create all tables
    SQLModel.metadata.create_all(engine)

    yield engine

    # Drop all tables after test
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a test database session.

    Args:
        test_engine: Test database engine fixture

    Yields:
        Session: SQLModel session for testing
    """
    session = Session(test_engine)
    yield session
    session.close()


@pytest.fixture(scope="function")
def test_user_id():
    """Provide a test user ID.

    Returns:
        str: Test user ID
    """
    return "test_user_123"


@pytest.fixture(scope="function")
def test_task(test_session, test_user_id):
    """Create a test task in the database.

    Args:
        test_session: Test database session fixture
        test_user_id: Test user ID fixture

    Returns:
        Task: Created test task
    """
    task = Task(
        user_id=test_user_id,
        title="Test Task",
        description="Test Description",
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    test_session.add(task)
    test_session.commit()
    test_session.refresh(task)
    return task


@pytest.fixture(scope="function")
def multiple_test_tasks(test_session, test_user_id):
    """Create multiple test tasks in the database.

    Args:
        test_session: Test database session fixture
        test_user_id: Test user ID fixture

    Returns:
        List[Task]: List of created test tasks
    """
    tasks = []
    for i in range(3):
        task = Task(
            user_id=test_user_id,
            title=f"Test Task {i+1}",
            description=f"Test Description {i+1}",
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_session.add(task)
        tasks.append(task)

    test_session.commit()
    for task in tasks:
        test_session.refresh(task)

    return tasks
