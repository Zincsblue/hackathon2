"""Delete Task MCP Tool.

This tool permanently deletes a task.
"""

from sqlmodel import Session, select
from typing import Dict, Any

from ..database import get_session
from ..models import Task
from ..schemas import DeleteTaskInput, DeleteTaskOutput


def delete_task(user_id: str, task_id: int) -> Dict[str, Any]:
    """Permanently delete a task.

    Args:
        user_id: ID of the user who owns the task
        task_id: ID of the task to delete

    Returns:
        Dict containing success status and deletion confirmation or error

    Example:
        >>> result = delete_task("user123", 1)
        >>> print(result)
        {
            "success": True,
            "data": {
                "deleted": True,
                "task_id": 1,
                "message": "Task successfully deleted"
            }
        }
    """
    try:
        # Validate input using Pydantic schema
        input_data = DeleteTaskInput(user_id=user_id, task_id=task_id)
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
    session_gen = get_session()
    session = next(session_gen)

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

        # Delete task from database
        session.delete(task)
        session.commit()

        return {
            "success": True,
            "data": {
                "deleted": True,
                "task_id": input_data.task_id,
                "message": "Task successfully deleted"
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
        try:
            next(session_gen, None)
        except StopIteration:
            pass
