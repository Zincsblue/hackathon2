"""
Custom exceptions for the task management API.
"""
from fastapi import HTTPException, status


class TaskNotFoundException(HTTPException):
    """Raised when a task is not found."""
    def __init__(self, task_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found"
        )


class TaskAccessDeniedException(HTTPException):
    """Raised when user tries to access another user's task."""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this task"
        )


class DatabaseException(HTTPException):
    """Raised for database-related errors."""
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )
