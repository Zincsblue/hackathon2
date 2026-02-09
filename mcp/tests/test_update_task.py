"""Tests for update_task tool.

This module tests the update_task tool functionality including:
- Successful task update
- Partial update
- Task not found error
- Unauthorized access error
"""

import pytest

from src.tools.add_task import add_task
from src.tools.update_task import update_task


def test_update_task_title(test_user_id):
    """Test updating task title."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries", "Milk, eggs")
    task_id = result["data"]["id"]

    # Update title
    result = update_task(test_user_id, task_id, title="Buy groceries and cook dinner")

    assert result["success"] is True
    assert result["data"]["title"] == "Buy groceries and cook dinner"
    assert result["data"]["description"] == "Milk, eggs"


def test_update_task_description(test_user_id):
    """Test updating task description."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries", "Milk, eggs")
    task_id = result["data"]["id"]

    # Update description
    result = update_task(test_user_id, task_id, description="Milk, eggs, bread, chicken")

    assert result["success"] is True
    assert result["data"]["title"] == "Buy groceries"
    assert result["data"]["description"] == "Milk, eggs, bread, chicken"


def test_update_task_completed_status(test_user_id):
    """Test updating task completion status."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries")
    task_id = result["data"]["id"]

    # Update completion status
    result = update_task(test_user_id, task_id, completed=True)

    assert result["success"] is True
    assert result["data"]["completed"] is True


def test_update_task_multiple_fields(test_user_id):
    """Test updating multiple fields at once."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries", "Milk, eggs")
    task_id = result["data"]["id"]

    # Update multiple fields
    result = update_task(
        test_user_id,
        task_id,
        title="Buy groceries and cook",
        description="Milk, eggs, bread",
        completed=True
    )

    assert result["success"] is True
    assert result["data"]["title"] == "Buy groceries and cook"
    assert result["data"]["description"] == "Milk, eggs, bread"
    assert result["data"]["completed"] is True


def test_update_task_not_found(test_user_id):
    """Test updating a non-existent task."""
    result = update_task(test_user_id, 99999, title="New title")

    assert result["success"] is False
    assert result["error"]["code"] == "TASK_NOT_FOUND"


def test_update_task_unauthorized():
    """Test updating another user's task."""
    # Create task for user1
    user1_id = "user1"
    result = add_task(user1_id, "User1 Task")
    task_id = result["data"]["id"]

    # Try to update as user2
    user2_id = "user2"
    result = update_task(user2_id, task_id, title="Modified by user2")

    assert result["success"] is False
    assert result["error"]["code"] == "UNAUTHORIZED"


def test_update_task_title_too_long(test_user_id):
    """Test updating with title exceeding 200 characters."""
    # Create a task
    result = add_task(test_user_id, "Buy groceries")
    task_id = result["data"]["id"]

    # Try to update with long title
    long_title = "A" * 201
    result = update_task(test_user_id, task_id, title=long_title)

    assert result["success"] is False
    assert result["error"]["code"] == "INVALID_INPUT"
