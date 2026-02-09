"""Tests for add_task tool.

This module tests the add_task tool functionality including:
- Successful task creation
- Missing title error
- Invalid user error
- Title too long error
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.tools.add_task import add_task


def test_add_task_success(test_session, test_user_id):
    """Test successful task creation."""
    with patch('src.tools.add_task.get_session') as mock_get_session:
        mock_get_session.return_value = test_session

        result = add_task(
            user_id=test_user_id,
            title="Buy groceries",
            description="Milk, eggs, bread"
        )

        assert result["success"] is True
        assert "data" in result
        assert result["data"]["user_id"] == test_user_id
        assert result["data"]["title"] == "Buy groceries"
        assert result["data"]["description"] == "Milk, eggs, bread"
        assert result["data"]["completed"] is False
        assert "id" in result["data"]
        assert "created_at" in result["data"]
        assert "updated_at" in result["data"]


def test_add_task_without_description(test_session, test_user_id):
    """Test task creation without description."""
    with patch('src.tools.add_task.get_session') as mock_get_session:
        mock_get_session.return_value = test_session

        result = add_task(
            user_id=test_user_id,
            title="Call dentist"
        )

        assert result["success"] is True
        assert result["data"]["title"] == "Call dentist"
        assert result["data"]["description"] is None


def test_add_task_missing_title(test_session, test_user_id):
    """Test task creation with missing title."""
    with patch('src.tools.add_task.get_session') as mock_get_session:
        mock_get_session.return_value = test_session

        result = add_task(
            user_id=test_user_id,
            title=""
        )

        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


def test_add_task_title_too_long(test_session, test_user_id):
    """Test task creation with title exceeding 200 characters."""
    with patch('src.tools.add_task.get_session') as mock_get_session:
        mock_get_session.return_value = test_session

        long_title = "A" * 201
        result = add_task(
            user_id=test_user_id,
            title=long_title
        )

        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


def test_add_task_description_too_long(test_session, test_user_id):
    """Test task creation with description exceeding 1000 characters."""
    with patch('src.tools.add_task.get_session') as mock_get_session:
        mock_get_session.return_value = test_session

        long_description = "A" * 1001
        result = add_task(
            user_id=test_user_id,
            title="Valid title",
            description=long_description
        )

        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == "INVALID_INPUT"


def test_add_task_invalid_user(test_session):
    """Test task creation with invalid user_id."""
    with patch('src.tools.add_task.get_session') as mock_get_session:
        mock_get_session.return_value = test_session

        result = add_task(
            user_id="",
            title="Test task"
        )

        assert result["success"] is False
        assert "error" in result
        assert result["error"]["code"] == "USER_NOT_FOUND"
