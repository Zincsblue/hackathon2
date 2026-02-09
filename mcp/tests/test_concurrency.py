"""Tests for concurrent tool invocations.

This module tests that the MCP server can handle 100+ concurrent
tool invocations without data corruption or errors.
"""

import pytest
import concurrent.futures
from typing import List

from src.tools.add_task import add_task
from src.tools.list_tasks import list_tasks
from src.tools.complete_task import complete_task


def test_concurrent_add_tasks():
    """Test 100+ concurrent task creations."""
    user_id = "concurrent_user"
    num_tasks = 100

    def create_task(i):
        return add_task(user_id, f"Task {i}", f"Description {i}")

    # Create tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(create_task, i) for i in range(num_tasks)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Verify all tasks were created successfully
    successful = [r for r in results if r["success"]]
    assert len(successful) == num_tasks

    # Verify all tasks are in database
    list_result = list_tasks(user_id)
    assert list_result["success"] is True
    assert list_result["data"]["count"] == num_tasks


def test_concurrent_complete_tasks():
    """Test concurrent task completions."""
    user_id = "concurrent_user_2"
    num_tasks = 50

    # Create tasks first
    task_ids = []
    for i in range(num_tasks):
        result = add_task(user_id, f"Task {i}")
        task_ids.append(result["data"]["id"])

    def complete_task_by_id(task_id):
        return complete_task(user_id, task_id)

    # Complete tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(complete_task_by_id, tid) for tid in task_ids]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Verify all tasks were completed successfully
    successful = [r for r in results if r["success"]]
    assert len(successful) == num_tasks

    # Verify all tasks are marked as completed
    list_result = list_tasks(user_id)
    completed_tasks = [t for t in list_result["data"]["tasks"] if t["completed"]]
    assert len(completed_tasks) == num_tasks


def test_concurrent_mixed_operations():
    """Test concurrent mixed operations (add, list, complete)."""
    user_id = "concurrent_user_3"
    num_operations = 100

    def mixed_operation(i):
        if i % 3 == 0:
            return add_task(user_id, f"Task {i}")
        elif i % 3 == 1:
            return list_tasks(user_id)
        else:
            # Try to complete a task (may fail if task doesn't exist)
            return complete_task(user_id, i)

    # Execute mixed operations concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(mixed_operation, i) for i in range(num_operations)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Verify no database corruption occurred
    list_result = list_tasks(user_id)
    assert list_result["success"] is True
    # Should have created approximately num_operations/3 tasks
    assert list_result["data"]["count"] > 0


def test_concurrent_user_isolation():
    """Test that concurrent operations maintain user isolation."""
    num_users = 10
    tasks_per_user = 10

    def create_user_tasks(user_index):
        user_id = f"user_{user_index}"
        results = []
        for i in range(tasks_per_user):
            result = add_task(user_id, f"User {user_index} Task {i}")
            results.append(result)
        return user_id, results

    # Create tasks for multiple users concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_user_tasks, i) for i in range(num_users)]
        user_results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Verify each user has exactly their tasks
    for user_id, _ in user_results:
        list_result = list_tasks(user_id)
        assert list_result["success"] is True
        assert list_result["data"]["count"] == tasks_per_user
        # Verify all tasks belong to this user
        for task in list_result["data"]["tasks"]:
            assert task["user_id"] == user_id
