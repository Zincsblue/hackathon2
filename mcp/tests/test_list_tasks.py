"""Tests for list_tasks tool.

This module tests the list_tasks tool functionality including:
- Successful task listing
- Empty list scenario
- Invalid user error
"""

import pytest

from src.tools.list_tasks import list_tasks


def test_list_tasks_success(test_user_id, multiple_test_tasks):
    """Test successful task listing with multiple tasks."""
    result = list_tasks(user_id=test_user_id)

    assert result["success"] is True
    assert "data" in result
    assert "tasks" in result["data"]
    assert "count" in result["data"]
    assert result["data"]["count"] == 3
    assert len(result["data"]["tasks"]) == 3


def test_list_tasks_empty(test_user_id):
    """Test task listing with no tasks."""
    result = list_tasks(user_id=test_user_id)

    assert result["success"] is True
    assert result["data"]["tasks"] == []
    assert result["data"]["count"] == 0


def test_list_tasks_invalid_user():
    """Test task listing with invalid user_id."""
    result = list_tasks(user_id="")

    assert result["success"] is False
    assert "error" in result
    assert result["error"]["code"] == "USER_NOT_FOUND"


def test_list_tasks_user_isolation(test_user_id, test_task):
    """Test that users can only see their own tasks."""
    # Create task for test_user_id
    result1 = list_tasks(user_id=test_user_id)
    assert result1["success"] is True
    assert result1["data"]["count"] == 1

    # Try to list tasks for different user
    result2 = list_tasks(user_id="different_user")
    assert result2["success"] is True
    assert result2["data"]["count"] == 0
