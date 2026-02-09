"""Update Task MCP Tool.

This tool updates task details (title, description, completion status).
"""

from datetime import datetime
from sqlmodel import Session, select
from typing import Dict, Any, Optional

from ..database import get_session
from ..models import Task
from ..schemas import UpdateTaskInput, TaskOutput


def update_task(
    user_id: str,
    task_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    completed: Optional[bool] = None
) -> Dict[str, Any]:
    """Update task details.

    Args:
        user_id: ID of the user who owns the task
        task_id: ID of the task to update
        title: New task title (optional)
        description: New task description (optional)
        completed: New completion status (optional)

    Returns:
        Dict containing success status and updated task data or error

    Example:
        >>> result = update_task("user123", 1, title="Buy groceries and cook dinner")
        >>> print(result)
        {
            "success": True,
            "data": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries and cook dinner",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T12:00:00Z"
            }
        }
    """
    try:
        # Validate input using Pydantic schema
        input_data = UpdateTaskInput(
            user_id=user_id,
            task_id=task_id,
            title=title,
            description=description,
            completed=completed
        )
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

        # Update only provided fields (partial update)
        if input_data.title is not None:
            task.title = input_data.title
        if input_data.description is not None:
            task.description = input_data.description
        if input_data.completed is not None:
            task.completed = input_data.completed

        # Always update the updated_at timestamp
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
