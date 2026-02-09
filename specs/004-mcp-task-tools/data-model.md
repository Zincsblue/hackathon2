# Data Model: MCP Server & Task Tools

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Status**: Complete

## Overview

The MCP server operates on the existing Task entity from Spec-1 without introducing new database tables. All MCP tools perform CRUD operations on the Task table with user isolation enforced at the query level.

## Entities

### Task (Existing from Spec-1)

**Description**: Represents a user's todo item with title, description, and completion status.

**Attributes**:
- `id` (int, primary key): Unique identifier for the task
- `user_id` (int, foreign key): Owner of the task (references users.id from Spec-2)
- `title` (str, max 200 chars): Task title (required)
- `description` (str, max 1000 chars, nullable): Optional task description
- `completed` (bool, default false): Task completion status
- `created_at` (datetime): Timestamp when task was created
- `updated_at` (datetime): Timestamp when task was last modified

**Constraints**:
- `user_id` must reference valid user in users table
- `title` cannot be empty or null
- `title` length must be between 1 and 200 characters
- `description` length must not exceed 1000 characters if provided

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient user-scoped queries
- Composite index on `(user_id, id)` for task lookup with user validation

## MCP-Specific Concepts

### Tool Request (Conceptual)

**Description**: Represents an invocation of an MCP tool. Not persisted in database.

**Attributes**:
- `user_id` (int): User making the request
- `tool_name` (str): Name of the tool being invoked (add_task, list_tasks, etc.)
- `parameters` (dict): Tool-specific input parameters
- `timestamp` (datetime): When the tool was invoked

**Purpose**: Used for audit logging and request tracking

### Tool Response (Conceptual)

**Description**: Represents the result of a tool invocation. Not persisted in database.

**Attributes**:
- `success` (bool): Whether the tool invocation succeeded
- `data` (dict): Tool-specific output data (task object, list of tasks, etc.)
- `error` (dict, optional): Error information if success=false

**Purpose**: Standardized response format for all MCP tools

## Relationships

```
User (from Spec-2)
  |
  | 1:N
  |
Task (from Spec-1)
  |
  | operated on by
  |
MCP Tools (Spec-4)
```

**Key Relationships**:
- Each Task belongs to exactly one User (via user_id foreign key)
- Each User can have zero or more Tasks
- MCP tools operate on Tasks with user_id scoping enforced
- No new relationships introduced by MCP server

## Data Flow

### Tool Invocation Flow

1. AI agent invokes MCP tool with user_id and parameters
2. MCP server validates input parameters
3. MCP server queries database with user_id filter
4. Database returns matching Task records
5. MCP server formats response and returns to agent

### User Isolation Enforcement

All database queries include `WHERE user_id = ?` clause:

```sql
-- List tasks
SELECT * FROM tasks WHERE user_id = ?

-- Get specific task
SELECT * FROM tasks WHERE id = ? AND user_id = ?

-- Update task
UPDATE tasks SET ... WHERE id = ? AND user_id = ?

-- Delete task
DELETE FROM tasks WHERE id = ? AND user_id = ?
```

## State Management

**Stateless Architecture**:
- MCP server maintains zero in-memory state
- All state persists in PostgreSQL database
- Each tool invocation is independent
- Server can restart without data loss

**Transaction Management**:
- Each tool invocation runs in a database transaction
- Transactions are committed on success, rolled back on error
- Ensures atomic operations (all-or-nothing)

## Schema Compatibility

**No Schema Changes Required**:
- MCP server uses existing Task table from Spec-1
- No new tables, columns, or indexes needed
- Maintains backward compatibility with FastAPI backend
- Both MCP server and FastAPI backend can operate concurrently

## Validation Rules

### Task Creation (add_task)
- `user_id` must exist in users table
- `title` is required and must be 1-200 characters
- `description` is optional and must be ≤1000 characters if provided
- `completed` defaults to false

### Task Update (update_task)
- Task must exist and belong to user (user_id match)
- `title` must be 1-200 characters if provided
- `description` must be ≤1000 characters if provided
- `completed` can be true or false

### Task Deletion (delete_task)
- Task must exist and belong to user (user_id match)
- Deletion is permanent (no soft delete)

## Performance Considerations

**Query Optimization**:
- Index on `user_id` enables fast user-scoped queries
- Composite index on `(user_id, id)` optimizes task lookup with validation
- Connection pooling reduces connection overhead
- Prepared statements prevent SQL injection and improve performance

**Concurrency**:
- Database transactions ensure data consistency
- Row-level locking prevents concurrent modification conflicts
- Connection pool size (10 connections) supports 100+ concurrent tool invocations

## Data Retention

**No Special Retention Policy**:
- Tasks persist indefinitely until explicitly deleted
- No automatic cleanup or archival
- Audit logs (tool invocations) may be stored separately (implementation detail)
