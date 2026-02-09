"""
Task API routes.
RESTful endpoints for task CRUD operations with JWT authentication.
"""
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import Session
from typing import Annotated, Optional

from ...database import get_session
from ..deps import CurrentUserFromToken
from ...services.task_service import TaskService
from ...schemas.task import TaskCreate, TaskUpdate, TaskRead, TaskListResponse
from ...models.user import User

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Type alias for database session dependency
SessionDep = Annotated[Session, Depends(get_session)]


def get_task_service(session: SessionDep) -> TaskService:
    """Dependency to get TaskService instance with database session."""
    return TaskService(session)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task for the authenticated user"
)
async def create_task(
    current_user: CurrentUserFromToken,
    task_data: TaskCreate,
    task_service: TaskServiceDep
) -> TaskRead:
    """
    Create a new task for the authenticated user.

    - **title**: Task title (required, 1-200 chars)
    - **description**: Task description (optional, max 2000 chars)
    - **completed**: Completion status (default: false)

    Returns the created task with generated ID and timestamps.
    Requires valid JWT access token in Authorization header.
    """
    task = task_service.create_task(current_user.id, task_data)
    return TaskRead.model_validate(task)


@router.get(
    "",
    response_model=TaskListResponse,
    summary="List user's tasks",
    description="Retrieve all tasks for the authenticated user with pagination"
)
async def list_tasks(
    current_user: CurrentUserFromToken,
    task_service: TaskServiceDep,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    completed: Optional[bool] = Query(None, description="Filter by completion status")
) -> TaskListResponse:
    """
    List all tasks for the authenticated user with pagination.

    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **completed**: Optional filter by completion status

    Returns paginated list of tasks with total count.
    Requires valid JWT access token in Authorization header.
    """
    skip = (page - 1) * page_size
    tasks, total = task_service.list_tasks(
        current_user.id,
        skip=skip,
        limit=page_size,
        completed=completed
    )

    return TaskListResponse(
        tasks=[TaskRead.model_validate(task) for task in tasks],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get(
    "/{task_id}",
    response_model=TaskRead,
    summary="Get a specific task",
    description="Retrieve a single task by ID"
)
async def get_task(
    task_id: int,
    current_user: CurrentUserFromToken,
    task_service: TaskServiceDep
) -> TaskRead:
    """
    Get a specific task by ID.

    Returns 404 if the task doesn't exist or doesn't belong to the user.
    Requires valid JWT access token in Authorization header.
    """
    task = task_service.get_task(task_id, current_user.id)
    return TaskRead.model_validate(task)


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
    summary="Update a task",
    description="Update an existing task (partial update supported)"
)
async def update_task(
    task_id: int,
    current_user: CurrentUserFromToken,
    task_data: TaskUpdate,
    task_service: TaskServiceDep
) -> TaskRead:
    """
    Update a task (partial update supported).

    Only provided fields will be updated.
    Returns 404 if the task doesn't exist or doesn't belong to the user.
    Requires valid JWT access token in Authorization header.
    """
    task = task_service.update_task(task_id, current_user.id, task_data)
    return TaskRead.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently delete a task"
)
async def delete_task(
    task_id: int,
    current_user: CurrentUserFromToken,
    task_service: TaskServiceDep
) -> None:
    """
    Delete a task.

    Returns 204 No Content on success.
    Returns 404 if the task doesn't exist or doesn't belong to the user.
    Requires valid JWT access token in Authorization header.
    """
    task_service.delete_task(task_id, current_user.id)
