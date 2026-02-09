"""
Task request/response schemas.
Pydantic models for API validation and serialization.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    """
    Schema for creating a new task.
    Used in POST /users/{user_id}/tasks request body.
    """
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    completed: bool = Field(default=False, description="Completion status")


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    All fields are optional for partial updates.
    Used in PATCH /users/{user_id}/tasks/{task_id} request body.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    completed: Optional[bool] = Field(None, description="Completion status")


class TaskRead(BaseModel):
    """
    Schema for reading a task.
    Used in all response bodies that return task data.
    """
    id: int = Field(description="Unique task identifier")
    user_id: str = Field(description="Owner's user ID")
    title: str = Field(description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(description="Completion status")
    created_at: datetime = Field(description="Task creation timestamp (UTC)")
    updated_at: datetime = Field(description="Last update timestamp (UTC)")

    class Config:
        from_attributes = True  # Allows conversion from SQLModel ORM objects


class TaskListResponse(BaseModel):
    """
    Schema for paginated task list response.
    Used in GET /users/{user_id}/tasks response body.
    """
    tasks: list[TaskRead] = Field(description="Array of tasks")
    total: int = Field(description="Total number of tasks matching the query")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
