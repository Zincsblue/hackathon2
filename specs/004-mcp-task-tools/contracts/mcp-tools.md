# MCP Tool Contracts

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document defines the input/output contracts for all five MCP tools exposed by the MCP server. Each tool follows a consistent pattern with structured inputs, outputs, and error responses.

## Common Patterns

### Input Structure
All tools accept parameters as a JSON object with required and optional fields.

### Output Structure
All tools return a JSON object with either:
- **Success**: `{ "success": true, "data": {...} }`
- **Error**: `{ "success": false, "error": { "code": "ERROR_CODE", "message": "...", "details": {...} } }`

### Error Codes
- `USER_NOT_FOUND`: The specified user_id does not exist
- `TASK_NOT_FOUND`: The specified task_id does not exist
- `UNAUTHORIZED`: User attempting to access another user's task
- `TITLE_REQUIRED`: Task title is missing or empty
- `TITLE_TOO_LONG`: Task title exceeds 200 characters
- `DESCRIPTION_TOO_LONG`: Task description exceeds 1000 characters
- `INVALID_INPUT`: Input validation failed (type mismatch, missing required field)
- `DATABASE_ERROR`: Database operation failed
- `TIMEOUT`: Operation exceeded 5 second timeout

---

## Tool: add_task

**Description**: Creates a new task for the specified user.

### Input Schema

```json
{
  "user_id": 123,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread"
}
```

**Parameters**:
- `user_id` (integer, required): ID of the user creating the task
- `title` (string, required): Task title (1-200 characters)
- `description` (string, optional): Task description (max 1000 characters)

### Output Schema (Success)

```json
{
  "success": true,
  "data": {
    "id": 456,
    "user_id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T10:30:00Z"
  }
}
```

### Error Responses

**USER_NOT_FOUND**:
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with id 123 does not exist",
    "details": { "user_id": 123 }
  }
}
```

**TITLE_REQUIRED**:
```json
{
  "success": false,
  "error": {
    "code": "TITLE_REQUIRED",
    "message": "Task title is required and cannot be empty",
    "details": {}
  }
}
```

**TITLE_TOO_LONG**:
```json
{
  "success": false,
  "error": {
    "code": "TITLE_TOO_LONG",
    "message": "Task title must be 200 characters or less",
    "details": { "length": 250, "max_length": 200 }
  }
}
```

---

## Tool: list_tasks

**Description**: Retrieves all tasks for the specified user.

### Input Schema

```json
{
  "user_id": 123
}
```

**Parameters**:
- `user_id` (integer, required): ID of the user whose tasks to retrieve

### Output Schema (Success)

```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 456,
        "user_id": 123,
        "title": "Buy groceries",
        "description": "Milk, eggs, bread",
        "completed": false,
        "created_at": "2026-02-09T10:30:00Z",
        "updated_at": "2026-02-09T10:30:00Z"
      },
      {
        "id": 457,
        "user_id": 123,
        "title": "Call dentist",
        "description": null,
        "completed": true,
        "created_at": "2026-02-08T14:20:00Z",
        "updated_at": "2026-02-09T09:15:00Z"
      }
    ],
    "count": 2
  }
}
```

**Empty List**:
```json
{
  "success": true,
  "data": {
    "tasks": [],
    "count": 0
  }
}
```

### Error Responses

**USER_NOT_FOUND**:
```json
{
  "success": false,
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "User with id 123 does not exist",
    "details": { "user_id": 123 }
  }
}
```

---

## Tool: complete_task

**Description**: Marks a task as completed.

### Input Schema

```json
{
  "user_id": 123,
  "task_id": 456
}
```

**Parameters**:
- `user_id` (integer, required): ID of the user who owns the task
- `task_id` (integer, required): ID of the task to mark as completed

### Output Schema (Success)

```json
{
  "success": true,
  "data": {
    "id": 456,
    "user_id": 123,
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": true,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T11:45:00Z"
  }
}
```

### Error Responses

**TASK_NOT_FOUND**:
```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with id 456 does not exist",
    "details": { "task_id": 456 }
  }
}
```

**UNAUTHORIZED**:
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "User 123 is not authorized to access task 456",
    "details": { "user_id": 123, "task_id": 456 }
  }
}
```

---

## Tool: update_task

**Description**: Updates task title, description, or completion status.

### Input Schema

```json
{
  "user_id": 123,
  "task_id": 456,
  "title": "Buy groceries and cook dinner",
  "description": "Milk, eggs, bread, chicken",
  "completed": false
}
```

**Parameters**:
- `user_id` (integer, required): ID of the user who owns the task
- `task_id` (integer, required): ID of the task to update
- `title` (string, optional): New task title (1-200 characters)
- `description` (string, optional): New task description (max 1000 characters, null to clear)
- `completed` (boolean, optional): New completion status

**Note**: At least one of title, description, or completed must be provided.

### Output Schema (Success)

```json
{
  "success": true,
  "data": {
    "id": 456,
    "user_id": 123,
    "title": "Buy groceries and cook dinner",
    "description": "Milk, eggs, bread, chicken",
    "completed": false,
    "created_at": "2026-02-09T10:30:00Z",
    "updated_at": "2026-02-09T12:00:00Z"
  }
}
```

### Error Responses

**TASK_NOT_FOUND**:
```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with id 456 does not exist",
    "details": { "task_id": 456 }
  }
}
```

**UNAUTHORIZED**:
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "User 123 is not authorized to access task 456",
    "details": { "user_id": 123, "task_id": 456 }
  }
}
```

**TITLE_TOO_LONG**:
```json
{
  "success": false,
  "error": {
    "code": "TITLE_TOO_LONG",
    "message": "Task title must be 200 characters or less",
    "details": { "length": 250, "max_length": 200 }
  }
}
```

---

## Tool: delete_task

**Description**: Permanently deletes a task.

### Input Schema

```json
{
  "user_id": 123,
  "task_id": 456
}
```

**Parameters**:
- `user_id` (integer, required): ID of the user who owns the task
- `task_id` (integer, required): ID of the task to delete

### Output Schema (Success)

```json
{
  "success": true,
  "data": {
    "deleted": true,
    "task_id": 456,
    "message": "Task successfully deleted"
  }
}
```

### Error Responses

**TASK_NOT_FOUND**:
```json
{
  "success": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task with id 456 does not exist",
    "details": { "task_id": 456 }
  }
}
```

**UNAUTHORIZED**:
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "User 123 is not authorized to access task 456",
    "details": { "user_id": 123, "task_id": 456 }
  }
}
```

---

## Testing Contracts

### Test Scenarios

Each tool should be tested with:
1. **Happy path**: Valid inputs, successful operation
2. **Invalid user**: Non-existent user_id
3. **Invalid task**: Non-existent task_id (for tools that require it)
4. **Unauthorized access**: User attempting to access another user's task
5. **Validation errors**: Invalid input (empty title, too long, wrong type)
6. **Database errors**: Simulated database connection failure
7. **Timeout**: Operation exceeding 5 second limit

### Contract Validation

All tool responses must:
- Include `success` field (boolean)
- Include `data` field on success or `error` field on failure
- Use documented error codes
- Return proper HTTP-like status semantics (even though MCP is not HTTP)
- Complete within 5 seconds or return TIMEOUT error
