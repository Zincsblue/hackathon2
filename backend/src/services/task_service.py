"""
Task service layer.
Business logic for task CRUD operations with user-scoped data isolation.
"""
import logging
from sqlmodel import Session, select, func
from datetime import datetime
from typing import Optional

from ..models.task import Task
from ..schemas.task import TaskCreate, TaskUpdate
from ..exceptions import TaskNotFoundException, TaskAccessDeniedException

# Configure logger
logger = logging.getLogger(__name__)


class TaskService:
    """
    Service layer for task business logic.
    Enforces user isolation - all operations are scoped by user_id.
    """

    def __init__(self, session: Session):
        """
        Initialize TaskService with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create_task(self, user_id: str, task_data: TaskCreate) -> Task:
        """
        Create a new task for the authenticated user.

        Args:
            user_id: ID of the authenticated user (task owner)
            task_data: Task creation data (title, description, completed)

        Returns:
            Created task with generated ID and timestamps

        Raises:
            DatabaseException: If database operation fails
        """
        logger.info(f"Creating task for user_id={user_id}, title={task_data.title}")

        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            completed=task_data.completed,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        logger.info(f"Task created successfully: task_id={task.id}, user_id={user_id}")
        return task

    def get_task(self, task_id: int, user_id: str) -> Task:
        """
        Get a task by ID, ensuring it belongs to the user.

        Args:
            task_id: Task ID
            user_id: ID of the authenticated user

        Returns:
            Task if found and owned by user

        Raises:
            TaskNotFoundException: If task doesn't exist or doesn't belong to user
        """
        logger.debug(f"Fetching task_id={task_id} for user_id={user_id}")

        statement = select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id
        )
        task = self.session.exec(statement).first()

        if not task:
            logger.warning(f"Task not found: task_id={task_id}, user_id={user_id}")
            raise TaskNotFoundException(task_id)

        logger.debug(f"Task retrieved successfully: task_id={task_id}")
        return task

    def list_tasks(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None
    ) -> tuple[list[Task], int]:
        """
        List tasks for the authenticated user with pagination.

        Args:
            user_id: ID of the authenticated user
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            completed: Optional filter by completion status

        Returns:
            Tuple of (tasks list, total count)
        """
        logger.info(f"Listing tasks for user_id={user_id}, skip={skip}, limit={limit}, completed={completed}")

        # Base query with user filter
        statement = select(Task).where(Task.user_id == user_id)

        # Apply optional completed filter
        if completed is not None:
            statement = statement.where(Task.completed == completed)

        # Get total count
        count_statement = select(func.count()).select_from(
            statement.subquery()
        )
        total = self.session.exec(count_statement).one()

        # Apply pagination and ordering
        statement = (
            statement
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        tasks = self.session.exec(statement).all()

        logger.info(f"Retrieved {len(tasks)} tasks (total={total}) for user_id={user_id}")
        return list(tasks), total

    def update_task(
        self,
        task_id: int,
        user_id: str,
        task_data: TaskUpdate
    ) -> Task:
        """
        Update a task, ensuring it belongs to the user.

        Args:
            task_id: Task ID
            user_id: ID of the authenticated user
            task_data: Update data (partial update supported)

        Returns:
            Updated task

        Raises:
            TaskNotFoundException: If task doesn't exist or doesn't belong to user
        """
        logger.info(f"Updating task_id={task_id} for user_id={user_id}")

        task = self.get_task(task_id, user_id)

        # Update only provided fields
        update_data = task_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update timestamp
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        logger.info(f"Task updated successfully: task_id={task_id}")
        return task

    def delete_task(self, task_id: int, user_id: str) -> None:
        """
        Delete a task, ensuring it belongs to the user.

        Args:
            task_id: Task ID
            user_id: ID of the authenticated user

        Raises:
            TaskNotFoundException: If task doesn't exist or doesn't belong to user
        """
        logger.info(f"Deleting task_id={task_id} for user_id={user_id}")

        task = self.get_task(task_id, user_id)
        self.session.delete(task)
        self.session.commit()

        logger.info(f"Task deleted successfully: task_id={task_id}")
