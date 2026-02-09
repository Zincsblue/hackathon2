"""
Exceptions package.
Exports custom exception classes.
"""
from .handlers import (
    TaskNotFoundException,
    TaskAccessDeniedException,
    DatabaseException
)

__all__ = [
    "TaskNotFoundException",
    "TaskAccessDeniedException",
    "DatabaseException"
]
