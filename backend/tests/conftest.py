"""
Pytest configuration and fixtures.
Provides test database session and test client for integration tests.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from backend.src.main import app
from backend.src.database import get_session

# Create in-memory SQLite database for testing
# Using StaticPool to maintain single connection across test
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Creates all tables before test and drops them after.
    """
    # Create all tables
    SQLModel.metadata.create_all(test_engine)

    # Create session
    with Session(test_engine) as session:
        yield session

    # Drop all tables after test
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create test client with overridden database dependency.
    """
    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
