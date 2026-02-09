"""Tests for delete_task tool.

This module tests the delete_task tool functionality including:
- Successful task deletion
- Task not found error
- Unauthorized access error
"""

import pytest

from src.tools.add_task import add_task
from src.tools.delete_task import delete_task
from src.tools.list_tasks import list_tasks


def test_delete_task_success(test_user_id):
    """Test successful task deletion."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries")
    task_id = result["data"]["id"]

    # Delete the task
    result = delete_task(test_user_id, task_id)

    assert result["success"] is True
    assert result["data"]["deleted"] is True
    assert result["data"]["task_id"] == task_id
    assert "message" in result["data"]


def test_delete_task_verifies_deletion(test_user_id):
    """Test that deleted task no longer appears in list."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries")
    task_id = result["data"]["id"]

    # Verify task exists
    result = list_tasks(test_user_id)
    assert result["data"]["count"] == 1

    # Delete the task
    delete_task(test_user_id, task_id)

    # Verify task is gone
    result = list_tasks(test_user_id)
    assert result["data"]["count"] == 0


def test_delete_task_not_found(test_user_id):
    """Test deleting a non-existent task."""
    result = delete_task(test_user_id, 99999)

    assert result["success"] is False
    assert result["error"]["code"] == "TASK_NOT_FOUND"


def test_delete_task_unauthorized():
    """Test deleting another user's task."""
    # Create task for user1
    user1_id = "user1"
    result = add_task(user1_id, "User1 Task")
    task_id = result["data"]["id"]

    # Try to delete as user2
    user2_id = "user2"
    result = delete_task(user2_id, task_id)

    assert result["success"] is False
    assert result["error"]["code"] == "UNAUTHORIZED"


def test_delete_task_twice(test_user_id):
    """Test deleting the same task twice."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries")
    task_id = result["data"]["id"]

    # Delete the task
    result = delete_task(test_user_id, task_id)
    assert result["success"] is True

    # Try to delete again
    result = delete_task(test_user_id, task_id)
    assert result["success"] is False
    assert result["error"]["code"] == "TASK_NOT_FOUND"
