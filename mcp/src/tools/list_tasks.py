"""List Tasks MCP Tool.

This tool retrieves all tasks for a specified user.
"""

from sqlmodel import Session, select
from typing import Dict, Any, List

from ..database import get_session
from ..models import Task
from ..schemas import ListTasksInput, TaskOutput, TaskListOutput


def list_tasks(user_id: str) -> Dict[str, Any]:
    """Retrieve all tasks for the specified user.

    Args:
        user_id: ID of the user whose tasks to retrieve

    Returns:
        Dict containing success status and list of tasks or error

    Example:
        >>> result = list_tasks("user123")
        >>> print(result)
        {
            "success": True,
            "data": {
                "tasks": [
                    {
                        "id": 1,
                        "user_id": "user123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-02-09T10:30:00Z",
                        "updated_at": "2026-02-09T10:30:00Z"
                    }
                ],
                "count": 1
            }
        }
    """
    try:
        # Validate input using Pydantic schema
        input_data = ListTasksInput(user_id=user_id)
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "INVALID_INPUT",
                "message": f"Input validation failed: {str(e)}",
                "details": {"user_id": user_id}
            }
        }

    # Create database session
    session = get_session()

    try:
        # Verify user exists
        if not user_id or not isinstance(user_id, str):
            return {
                "success": False,
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": f"User with id {user_id} does not exist",
                    "details": {"user_id": user_id}
                }
            }

        # Query tasks with user_id filter (user isolation)
        statement = select(Task).where(Task.user_id == input_data.user_id)
        tasks = session.exec(statement).all()

        # Convert to output schema
        task_outputs = [TaskOutput.model_validate(task) for task in tasks]

        return {
            "success": True,
            "data": {
                "tasks": [task.model_dump() for task in task_outputs],
                "count": len(task_outputs)
            }
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
