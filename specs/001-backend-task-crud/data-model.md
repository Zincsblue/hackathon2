# Data Model: Backend Core & Data Layer

**Feature**: 001-backend-task-crud
**Date**: 2026-02-08
**Phase**: 1 - Design

## Overview

This document defines the database schema for the task management system. The data model supports user-scoped task management with proper isolation and relationships.

## Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│─────────────────│
│ id (PK)         │◄─────┐
│ email           │      │
│ name            │      │
│ created_at      │      │
└─────────────────┘      │
                         │ 1:N
                         │
                    ┌────┴────────────┐
                    │      Task       │
                    │─────────────────│
                    │ id (PK)         │
                    │ user_id (FK)    │
                    │ title           │
                    │ description     │
                    │ completed       │
                    │ created_at      │
                    │ updated_at      │
                    └─────────────────┘
```

## Entities

### User

Represents an authenticated user who owns tasks. User management and authentication are handled externally (deferred to Spec-2); this entity exists to establish task ownership relationships.

**Table Name**: `users`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | VARCHAR(255) | PRIMARY KEY | Unique user identifier (from auth system) |
| email | VARCHAR(255) | NOT NULL, UNIQUE | User's email address |
| name | VARCHAR(255) | NOT NULL | User's display name |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`

**Validation Rules**:
- email: Must be valid email format
- name: 1-255 characters
- id: Non-empty string

**Notes**:
- User records are created by the authentication system (Spec-2)
- This spec assumes user_id is provided with each request
- No password or authentication fields (handled externally)

---

### Task

Represents a user's to-do item with title, description, and completion status.

**Table Name**: `tasks`

**Fields**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique task identifier |
| user_id | VARCHAR(255) | NOT NULL, FOREIGN KEY → users.id | Owner of the task |
| title | VARCHAR(200) | NOT NULL | Task title |
| description | TEXT | NULLABLE | Detailed task description |
| completed | BOOLEAN | NOT NULL, DEFAULT FALSE | Completion status |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- PRIMARY KEY on `id`
- INDEX on `user_id` (for fast user-scoped queries)
- COMPOSITE INDEX on `(user_id, completed)` (for filtering by status)
- INDEX on `created_at` (for sorting)

**Foreign Keys**:
- `user_id` REFERENCES `users(id)` ON DELETE CASCADE

**Validation Rules**:
- title: 1-200 characters, required
- description: 0-2000 characters, optional
- completed: Boolean (true/false)
- user_id: Must reference existing user

**State Transitions**:
```
┌─────────┐
│ Created │
│completed│
│ = false │
└────┬────┘
     │
     │ User marks complete
     ▼
┌─────────┐
│Completed│
│completed│
│ = true  │
└────┬────┘
     │
     │ User marks incomplete
     ▼
┌─────────┐
│ Created │
│completed│
│ = false │
└─────────┘
```

**Business Rules**:
1. Tasks can only be accessed by their owner (user_id match required)
2. Tasks can be toggled between completed and incomplete states
3. updated_at timestamp is automatically updated on any modification
4. Deleting a user cascades to delete all their tasks
5. Task title cannot be empty
6. Task description is optional

---

## SQLModel Implementation

### User Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task Model

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="users.id", index=True, max_length=255)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Database Migrations

### Initial Migration (Alembic)

**Migration Name**: `001_initial_schema`

**Up Migration**:
```sql
-- Create users table
CREATE TABLE users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Create tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
CREATE INDEX idx_tasks_created_at ON tasks(created_at);
```

**Down Migration**:
```sql
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;
```

## Query Patterns

### Common Queries

**Get all tasks for a user (with pagination)**:
```python
statement = (
    select(Task)
    .where(Task.user_id == user_id)
    .order_by(Task.created_at.desc())
    .offset(skip)
    .limit(limit)
)
```

**Get specific task with ownership check**:
```python
statement = select(Task).where(
    Task.id == task_id,
    Task.user_id == user_id
)
```

**Filter tasks by completion status**:
```python
statement = (
    select(Task)
    .where(Task.user_id == user_id, Task.completed == True)
    .order_by(Task.created_at.desc())
)
```

**Count user's tasks**:
```python
statement = select(func.count()).select_from(Task).where(Task.user_id == user_id)
```

## Performance Considerations

### Index Strategy

1. **user_id index**: Critical for user-scoped queries (all queries filter by user)
2. **Composite (user_id, completed) index**: Optimizes status filtering
3. **created_at index**: Supports chronological sorting
4. **email unique index**: Fast user lookup by email

### Query Optimization

1. **Always filter by user_id first**: Reduces result set immediately
2. **Use pagination**: Limit result sets to prevent memory issues
3. **Selective column loading**: Load only needed columns for list views
4. **Connection pooling**: Reuse database connections efficiently

### Expected Query Performance

- Get user's tasks (paginated): <50ms
- Get single task: <10ms
- Create task: <20ms
- Update task: <20ms
- Delete task: <15ms

## Data Integrity

### Constraints

1. **Foreign Key Constraint**: Ensures tasks always belong to valid users
2. **NOT NULL Constraints**: Prevents incomplete records
3. **Unique Constraint**: Prevents duplicate user emails
4. **Check Constraints**: (Future) Could add constraints for title length, etc.

### Cascade Behavior

- **ON DELETE CASCADE**: When a user is deleted, all their tasks are automatically deleted
- Rationale: Tasks have no meaning without an owner

### Transaction Boundaries

All multi-step operations should be wrapped in transactions:
- Creating task with related data
- Updating multiple tasks
- Bulk operations

## Data Retention

**Assumptions** (from spec):
- No automatic deletion of completed tasks
- No archival strategy (all tasks remain active)
- Users can manually delete tasks at any time
- No soft-delete (tasks are permanently removed)

**Future Considerations**:
- Add `deleted_at` field for soft deletes
- Add `archived` boolean for completed task archival
- Implement data retention policies

## Security Considerations

1. **User Isolation**: All queries MUST filter by user_id
2. **Input Validation**: Title and description length limits prevent abuse
3. **SQL Injection**: SQLModel parameterizes all queries automatically
4. **Cascade Deletes**: Ensure user deletion properly cleans up tasks

## Testing Data

### Sample User

```python
test_user = User(
    id="test-user-123",
    email="test@example.com",
    name="Test User"
)
```

### Sample Tasks

```python
task1 = Task(
    user_id="test-user-123",
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False
)

task2 = Task(
    user_id="test-user-123",
    title="Finish project",
    description="Complete backend implementation",
    completed=True
)
```

## Migration Commands

```bash
# Create new migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

## References

- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- PostgreSQL Data Types: https://www.postgresql.org/docs/current/datatype.html
- Alembic Documentation: https://alembic.sqlalchemy.org/
