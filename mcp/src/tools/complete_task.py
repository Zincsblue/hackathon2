"""Complete Task MCP Tool.

This tool marks a task as completed.
"""

from datetime import datetime
from sqlmodel import Session, select
from typing import Dict, Any

from ..database import get_session
from ..models import Task
from ..schemas import CompleteTaskInput, TaskOutput


def complete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """Mark a task as completed.

    Args:
        user_id: ID of the user who owns the task
        task_id: ID of the task to mark as completed

    Returns:
        Dict containing success status and updated task data or error

    Example:
        >>> result = complete_task("user123", 1)
        >>> print(result)
        {
            "success": True,
            "data": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": True,
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T11:00:00Z"
            }
        }
    """
    try:
        # Validate input using Pydantic schema
        input_data = CompleteTaskInput(user_id=user_id, task_id=task_id)
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": f"Input validation failed: {str(e)}",
                "details": {"user_id": user_id, "task_id": task_id}
            }
        }

    # Create database session
    session = get_session()

    try:
        # Query task with user_id validation (user isolation)
        statement = select(Task).where(
            Task.id == input_data.task_id,
            Task.user_id == input_data.user_id
        )
        task = session.exec(statement).first()

        # Check if task exists
        if not task:
            # Check if task exists for another user (unauthorized access)
            task_exists = session.exec(
                select(Task).where(Task.id == input_data.task_id)
            ).first()

            if task_exists:
                return {
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": f"User {user_id} is not authorized to access task {task_id}",
                        "details": {"user_id": user_id, "task_id": task_id}
                    }
                }
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "TASK_NOT_FOUND",
                        "message": f"Task with id {task_id} does not exist",
                        "details": {"task_id": task_id}
                    }
                }

        # Update task completion status
        task.completed = True
        task.updated_at = datetime.utcnow()

        session.add(task)
        session.commit()
        session.refresh(task)

        # Convert to output schema
        task_output = TaskOutput.model_validate(task)

        return {
            "success": True,
            "data": task_output.model_dump()
        }

    except Exception as e:
        session.rollback()
        return {
            "success": False,
            "error": {
                "code": "DATABASE_ERROR",
                "message": f"Database operation failed: {str(e)}",
                "details": {}
            }
        }
    finally:
        session.close()
