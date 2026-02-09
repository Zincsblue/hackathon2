"""Tests for user isolation across all tools.

This module verifies that users cannot access other users' tasks
across all MCP tools.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from src.tools.add_task import add_task
from src.tools.list_tasks import list_tasks
from src.tools.complete_task import complete_task
from src.tools.update_task import update_task
from src.tools.delete_task import delete_task


def test_list_tasks_user_isolation(test_session):
    """Test that list_tasks only returns tasks for the specified user."""
    with patch('src.tools.add_task.get_session') as mock_add_session, \
         patch('src.tools.list_tasks.get_session') as mock_list_session:
        mock_add_session.return_value = test_session
        mock_list_session.return_value = test_session

        # Create tasks for user1
        user1_id = "user1"
        add_task(user1_id, "User1 Task 1")
        add_task(user1_id, "User1 Task 2")

        # Create tasks for user2
        user2_id = "user2"
        add_task(user2_id, "User2 Task 1")

        # Verify user1 sees only their tasks
        result1 = list_tasks(user1_id)
        assert result1["success"] is True
        assert result1["data"]["count"] == 2

        # Verify user2 sees only their tasks
        result2 = list_tasks(user2_id)
        assert result2["success"] is True
        assert result2["data"]["count"] == 1


def test_complete_task_unauthorized_access(test_session):
    """Test that users cannot complete other users' tasks."""
    with patch('src.tools.add_task.get_session') as mock_add_session, \
         patch('src.tools.complete_task.get_session') as mock_complete_session:
        mock_add_session.return_value = test_session
        mock_complete_session.return_value = test_session

        # Create task for user1
        user1_id = "user1"
        result = add_task(user1_id, "User1 Task")
        task_id = result["data"]["id"]

        # Try to complete task as user2
        user2_id = "user2"
        result = complete_task(user2_id, task_id)

        assert result["success"] is False
        assert result["error"]["code"] == "UNAUTHORIZED"


def test_update_task_unauthorized_access(test_session):
    """Test that users cannot update other users' tasks."""
    with patch('src.tools.add_task.get_session') as mock_add_session, \
         patch('src.tools.update_task.get_session') as mock_update_session:
        mock_add_session.return_value = test_session
        mock_update_session.return_value = test_session

        # Create task for user1
        user1_id = "user1"
        result = add_task(user1_id, "User1 Task")
        task_id = result["data"]["id"]

        # Try to update task as user2
        user2_id = "user2"
        result = update_task(user2_id, task_id, title="Modified by user2")

        assert result["success"] is False
        assert result["error"]["code"] == "UNAUTHORIZED"


def test_delete_task_unauthorized_access(test_session):
    """Test that users cannot delete other users' tasks."""
    with patch('src.tools.add_task.get_session') as mock_add_session, \
         patch('src.tools.delete_task.get_session') as mock_delete_session:
        mock_add_session.return_value = test_session
        mock_delete_session.return_value = test_session

        # Create task for user1
        user1_id = "user1"
        result = add_task(user1_id, "User1 Task")
        task_id = result["data"]["id"]

        # Try to delete task as user2
        user2_id = "user2"
        result = delete_task(user2_id, task_id)

        assert result["success"] is False
        assert result["error"]["code"] == "UNAUTHORIZED"


def test_cross_user_task_visibility(test_session):
    """Test that task IDs from one user are not visible to another user."""
    with patch('src.tools.add_task.get_session') as mock_add_session, \
         patch('src.tools.complete_task.get_session') as mock_complete_session:
        mock_add_session.return_value = test_session
        mock_complete_session.return_value = test_session

        # Create task for user1
        user1_id = "user1"
        result1 = add_task(user1_id, "User1 Task")
        task1_id = result1["data"]["id"]

        # Create task for user2
        user2_id = "user2"
        result2 = add_task(user2_id, "User2 Task")
        task2_id = result2["data"]["id"]

        # Verify user1 cannot see user2's task
        result = complete_task(user1_id, task2_id)
        assert result["success"] is False
        assert result["error"]["code"] == "UNAUTHORIZED"

        # Verify user2 cannot see user1's task
        result = complete_task(user2_id, task1_id)
        assert result["success"] is False
        assert result["error"]["code"] == "UNAUTHORIZED"
