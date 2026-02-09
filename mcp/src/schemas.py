"""Pydantic schemas for MCP tool input/output validation.

This module defines all input and output schemas for the five MCP tools,
ensuring type safety and validation.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


# Tool Input Schemas

class AddTaskInput(BaseModel):
    """Input schema for add_task tool."""
    user_id: str = Field(..., description="ID of the user creating the task")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional task description")


class ListTasksInput(BaseModel):
    """Input schema for list_tasks tool."""
    user_id: str = Field(..., description="ID of the user whose tasks to retrieve")


class CompleteTaskInput(BaseModel):
    """Input schema for complete_task tool."""
    user_id: str = Field(..., description="ID of the user who owns the task")
    task_id: int = Field(..., description="ID of the task to mark as completed")


class UpdateTaskInput(BaseModel):
    """Input schema for update_task tool."""
    user_id: str = Field(..., description="ID of the user who owns the task")
    task_id: int = Field(..., description="ID of the task to update")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="New task title")
    description: Optional[str] = Field(None, max_length=1000, description="New task description")
    completed: Optional[bool] = Field(None, description="New completion status")


class DeleteTaskInput(BaseModel):
    """Input schema for delete_task tool."""
    user_id: str = Field(..., description="ID of the user who owns the task")
    task_id: int = Field(..., description="ID of the task to delete")


# Tool Output Schemas

class TaskOutput(BaseModel):
    """Output schema for a single task."""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListOutput(BaseModel):
    """Output schema for list_tasks tool."""
    tasks: List[TaskOutput]
    count: int


class DeleteTaskOutput(BaseModel):
    """Output schema for delete_task tool."""
    deleted: bool
    task_id: int
    message: str


# Error Response Schema

class ErrorResponse(BaseModel):
    """Structured error response format."""
    code: str = Field(..., description="Error code (e.g., USER_NOT_FOUND, TASK_NOT_FOUND)")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[dict] = Field(None, description="Additional error context")


# Unified Response Schemas

class SuccessResponse(BaseModel):
    """Unified success response wrapper."""
    success: bool = True
    data: dict


class ErrorResponseWrapper(BaseModel):
    """Unified error response wrapper."""
    success: bool = False
    error: ErrorResponse
