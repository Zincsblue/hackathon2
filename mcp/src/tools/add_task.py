"""Add Task MCP Tool.

This tool creates a new task for a specified user.
"""

from datetime import datetime
from sqlmodel import Session, select
from typing import Dict, Any

from ..database import get_session
from ..models import Task
from ..schemas import AddTaskInput, TaskOutput, ErrorResponse


def add_task(user_id: str, title: str, description: str = None) -> Dict[str, Any]:
    """Create a new task for the specified user.

    Args:
        user_id: ID of the user creating the task
        title: Task title (1-200 characters)
        description: Optional task description (max 1000 characters)

    Returns:
        Dict containing success status and task data or error

    Example:
        >>> result = add_task("user123", "Buy groceries", "Milk, eggs, bread")
        >>> print(result)
        {
            "success": True,
            "data": {
                "id": 1,
                "user_id": "user123",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-02-09T10:30:00Z",
                "updated_at": "2026-02-09T10:30:00Z"
            }
        }
    """
    try:
        # Validate input using Pydantic schema
        input_data = AddTaskInput(user_id=user_id, title=title, description=description)
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": f"Input validation failed: {str(e)}",
                "details": {"user_id": user_id, "title": title}
            }
        }

    # Create database session
    session_gen = get_session()
    session = next(session_gen)

    try:
        # Verify user exists (user_id validation)
        # Note: In production, this would query the users table
        # For now, we'll assume user_id is valid if it's a non-empty string
        if not user_id or not isinstance(user_id, str):
            return {
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": f"User with id {user_id} does not exist",
                    "details": {"user_id": user_id}
                }
            }

        # Create new task
        new_task = Task(
            user_id=input_data.user_id,
            title=input_data.title,
            description=input_data.description,
            completed=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Insert into database
        session.add(new_task)
        session.commit()
        session.refresh(new_task)

        # Convert to output schema
        task_output = TaskOutput.model_validate(new_task)

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
        try:
            next(session_gen, None)
        except StopIteration:
            pass
