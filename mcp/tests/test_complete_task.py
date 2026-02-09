"""Tests for complete_task tool.

This module tests the complete_task tool functionality including:
- Successful task completion
- Task not found error
- Unauthorized access error
"""

import pytest

from src.tools.add_task import add_task
from src.tools.complete_task import complete_task


def test_complete_task_success(test_user_id):
    """Test successful task completion."""
    # Create a task first
    result = add_task(test_user_id, "Buy groceries")
    task_id = result["data"]["id"]

    # Complete the task
    result = complete_task(test_user_id, task_id)

    assert result["success"] is True
    assert result["data"]["completed"] is True
    assert result["data"]["id"] == task_id


def test_complete_task_not_found(test_user_id):
    """Test completing a non-existent task."""
    result = complete_task(test_user_id, 99999)

    assert result["success"] is False
    assert result["error"]["code"] == "TASK_NOT_FOUND"


def test_complete_task_unauthorized():
    """Test completing another user's task."""
    # Create task for user1
    user1_id = "user1"
    result = add_task(user1_id, "User1 Task")
    task_id = result["data"]["id"]

    # Try to complete as user2
    user2_id = "user2"
    result = complete_task(user2_id, task_id)

    assert result["success"] is False
    assert result["error"]["code"] == "UNAUTHORIZED"


def test_complete_task_already_completed(test_user_id):
    """Test completing an already completed task."""
    # Create and complete a task
    result = add_task(test_user_id, "Buy groceries")
    task_id = result["data"]["id"]
    complete_task(test_user_id, task_id)

    # Complete again
    result = complete_task(test_user_id, task_id)

    assert result["success"] is True
    assert result["data"]["completed"] is True
