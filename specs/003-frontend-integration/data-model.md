# Data Model: Frontend & Integration

**Feature**: 003-frontend-integration
**Date**: 2026-02-09
**Status**: Complete

---

## Overview

This document defines the data models used in the frontend application. These models represent the structure of data received from the backend API and managed in the frontend state. All models align with the backend schemas defined in Spec-1 and Spec-2.

---

## Frontend Data Models

### User

Represents an authenticated user in the system.

**Source**: Backend `/api/v1/auth/me` endpoint

**TypeScript Interface**:
```typescript
interface User {
  id: string;                    // UUID
  email: string;                 // User's email address
  name: string;                  // User's display name
  is_active: boolean;            // Account active status
  is_verified: boolean;          // Email verification status
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
}
```

**Validation Rules**:
- `id`: Required, UUID format
- `email`: Required, valid email format
- `name`: Required, 1-100 characters
- `is_active`: Required, boolean
- `is_verified`: Required, boolean
- `created_at`: Required, ISO 8601 timestamp
- `updated_at`: Required, ISO 8601 timestamp

**State Management**:
- Stored in: `AuthContext` (React Context)
- Lifecycle: Set on login/register, cleared on logout
- Persistence: None (fetched on app load via token refresh)

**Usage**:
- Display user name in header
- Show user email in profile
- Conditional rendering based on verification status

---

### Task

Represents a todo task belonging to a user.

**Source**: Backend `/api/v1/tasks` endpoints

**TypeScript Interface**:
```typescript
interface Task {
  id: string;                    // UUID
  title: string;                 // Task title
  description: string | null;    // Optional task description
  completed: boolean;            // Completion status
  user_id: string;               // Owner's user ID (UUID)
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
}
```

**Validation Rules**:
- `id`: Required, UUID format
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `completed`: Required, boolean
- `user_id`: Required, UUID format (matches authenticated user)
- `created_at`: Required, ISO 8601 timestamp
- `updated_at`: Required, ISO 8601 timestamp

**State Management**:
- Stored in: Component state (useState) or could use Context for global access
- Lifecycle: Fetched on dashboard load, updated on CRUD operations
- Persistence: Backend database (Neon PostgreSQL)

**State Transitions**:
```
[New Task Form] → (submit) → [Creating] → (success) → [Active Task]
                           → (error) → [Form with Error]

[Active Task] → (toggle complete) → [Updating] → (success) → [Completed Task]
                                  → (error) → [Active Task with Error]

[Active Task] → (edit) → [Editing] → (save) → [Updating] → (success) → [Active Task]
                                             → (error) → [Editing with Error]

[Active Task] → (delete) → [Deleting] → (success) → [Removed]
                                      → (error) → [Active Task with Error]
```

**Usage**:
- Display in task list
- Edit in task form
- Toggle completion status
- Delete from list

---

### Authentication Tokens

Represents JWT tokens used for authentication.

**Source**: Backend `/api/v1/auth/login` and `/api/v1/auth/register` endpoints

**TypeScript Interface**:
```typescript
interface TokenResponse {
  access_token: string;          // JWT access token
  token_type: string;            // Always "bearer"
  expires_in: number;            // Seconds until expiration (900 = 15 minutes)
}
```

**Validation Rules**:
- `access_token`: Required, JWT format (3 base64 segments separated by dots)
- `token_type`: Required, must be "bearer"
- `expires_in`: Required, positive integer (typically 900)

**State Management**:
- Stored in: `AuthContext` (React Context) - memory only
- Lifecycle: Set on login/register, refreshed before expiration, cleared on logout
- Persistence: None (memory only for security)
- Refresh token: Stored in httpOnly cookie (managed by backend, not accessible to frontend)

**Usage**:
- Attached to all API requests via `Authorization: Bearer {access_token}` header
- Automatically refreshed when expired (using refresh token cookie)
- Cleared on logout

---

### API Response Wrappers

#### TasksResponse

Paginated list of tasks.

**Source**: Backend `GET /api/v1/tasks` endpoint

**TypeScript Interface**:
```typescript
interface TasksResponse {
  tasks: Task[];                 // Array of task objects
  total: number;                 // Total number of tasks
  page: number;                  // Current page number (1-indexed)
  page_size: number;             // Number of tasks per page
}
```

**Validation Rules**:
- `tasks`: Required, array of Task objects
- `total`: Required, non-negative integer
- `page`: Required, positive integer
- `page_size`: Required, positive integer

**Usage**:
- Display task list with pagination info
- Show "X of Y tasks" counter
- Implement pagination controls (if needed)

---

#### ErrorResponse

Standard error response from backend.

**Source**: All backend API endpoints (on error)

**TypeScript Interface**:
```typescript
interface ErrorResponse {
  detail: string | ErrorDetail[];  // Error message or array of field errors
}

interface ErrorDetail {
  loc: string[];                   // Location of error (e.g., ["body", "email"])
  msg: string;                     // Error message
  type: string;                    // Error type (e.g., "value_error.email")
}
```

**Validation Rules**:
- `detail`: Required, string or array of ErrorDetail objects
- For ErrorDetail:
  - `loc`: Required, array of strings
  - `msg`: Required, string
  - `type`: Required, string

**Usage**:
- Display error messages to users
- Map field errors to form fields
- Show general error messages

---

## Form Data Models

### LoginFormData

Data submitted to login form.

**TypeScript Interface**:
```typescript
interface LoginFormData {
  email: string;                 // User's email
  password: string;              // User's password
}
```

**Validation Rules**:
- `email`: Required, valid email format
- `password`: Required, minimum 8 characters

**Usage**:
- Login form submission
- Sent to `POST /api/v1/auth/login`

---

### RegisterFormData

Data submitted to registration form.

**TypeScript Interface**:
```typescript
interface RegisterFormData {
  email: string;                 // User's email
  password: string;              // User's password
  name: string;                  // User's display name
}
```

**Validation Rules**:
- `email`: Required, valid email format
- `password`: Required, minimum 8 characters
- `name`: Required, 1-100 characters

**Usage**:
- Registration form submission
- Sent to `POST /api/v1/auth/register`

---

### TaskFormData

Data submitted to create/edit task form.

**TypeScript Interface**:
```typescript
interface TaskFormData {
  title: string;                 // Task title
  description?: string;          // Optional task description
  completed?: boolean;           // Completion status (for edit)
}
```

**Validation Rules**:
- `title`: Required, 1-200 characters
- `description`: Optional, max 1000 characters
- `completed`: Optional, boolean (only for edit)

**Usage**:
- Create task form submission → `POST /api/v1/tasks`
- Edit task form submission → `PATCH /api/v1/tasks/{id}`

---

## UI State Models

### AuthState

Authentication state managed in AuthContext.

**TypeScript Interface**:
```typescript
interface AuthState {
  user: User | null;             // Current user (null if not authenticated)
  accessToken: string | null;    // JWT access token (null if not authenticated)
  isLoading: boolean;            // Loading state (true during auth operations)
  error: string | null;          // Error message (null if no error)
}
```

**State Transitions**:
```
[Initial] → (app load) → [Loading] → (refresh success) → [Authenticated]
                                   → (refresh fail) → [Unauthenticated]

[Unauthenticated] → (login) → [Loading] → (success) → [Authenticated]
                                        → (error) → [Unauthenticated with Error]

[Authenticated] → (logout) → [Loading] → [Unauthenticated]

[Authenticated] → (token expires) → [Loading] → (refresh success) → [Authenticated]
                                              → (refresh fail) → [Unauthenticated]
```

---

### TaskListState

Task list state managed in TaskList component.

**TypeScript Interface**:
```typescript
interface TaskListState {
  tasks: Task[];                 // Array of tasks
  isLoading: boolean;            // Loading state
  error: string | null;          // Error message
  isEmpty: boolean;              // True if no tasks exist
}
```

**State Transitions**:
```
[Initial] → (load) → [Loading] → (success) → [Loaded with Tasks]
                               → (success, empty) → [Loaded Empty]
                               → (error) → [Error]

[Loaded] → (create task) → [Creating] → (success) → [Loaded with Tasks]
                                      → (error) → [Loaded with Error]

[Loaded] → (delete task) → [Deleting] → (success) → [Loaded]
                                      → (error) → [Loaded with Error]

[Loaded] → (update task) → [Updating] → (success) → [Loaded]
                                      → (error) → [Loaded with Error]
```

---

## Data Flow

### Authentication Flow

```
1. User submits login form
   ↓
2. Frontend calls POST /api/v1/auth/login
   ↓
3. Backend validates credentials
   ↓
4. Backend returns TokenResponse + sets refresh token cookie
   ↓
5. Frontend stores access token in AuthContext (memory)
   ↓
6. Frontend calls GET /api/v1/auth/me
   ↓
7. Backend returns User object
   ↓
8. Frontend stores user in AuthContext
   ↓
9. Frontend redirects to dashboard
```

### Task CRUD Flow

```
CREATE:
1. User submits task form
   ↓
2. Frontend calls POST /api/v1/tasks with TaskFormData
   ↓
3. Backend creates task in database
   ↓
4. Backend returns Task object
   ↓
5. Frontend adds task to local state
   ↓
6. Frontend displays new task in list

READ:
1. User navigates to dashboard
   ↓
2. Frontend calls GET /api/v1/tasks
   ↓
3. Backend queries user's tasks from database
   ↓
4. Backend returns TasksResponse
   ↓
5. Frontend stores tasks in local state
   ↓
6. Frontend displays task list

UPDATE:
1. User toggles task completion or edits task
   ↓
2. Frontend calls PATCH /api/v1/tasks/{id} with partial TaskFormData
   ↓
3. Backend updates task in database
   ↓
4. Backend returns updated Task object
   ↓
5. Frontend updates task in local state
   ↓
6. Frontend re-renders task

DELETE:
1. User clicks delete button
   ↓
2. Frontend calls DELETE /api/v1/tasks/{id}
   ↓
3. Backend deletes task from database
   ↓
4. Backend returns 204 No Content
   ↓
5. Frontend removes task from local state
   ↓
6. Frontend re-renders task list
```

### Token Refresh Flow

```
1. Frontend makes API request with expired access token
   ↓
2. Backend returns 401 Unauthorized
   ↓
3. Frontend API client detects 401
   ↓
4. Frontend calls POST /api/v1/auth/refresh (with refresh token cookie)
   ↓
5. Backend validates refresh token
   ↓
6. Backend returns new TokenResponse + rotates refresh token cookie
   ↓
7. Frontend stores new access token in AuthContext
   ↓
8. Frontend retries original API request with new token
   ↓
9. Backend processes request successfully
   ↓
10. Frontend receives response
```

---

## Summary

All data models are defined with clear TypeScript interfaces, validation rules, and state management strategies. The models align with backend schemas and support all required user stories:

- **User Story 1 (Authentication)**: User, TokenResponse, LoginFormData, RegisterFormData, AuthState
- **User Story 2 (Task Management)**: Task, TasksResponse, TaskFormData, TaskListState
- **User Story 3 (Responsive UX)**: All models support responsive rendering
- **User Story 4 (Error Handling)**: ErrorResponse, error states in AuthState and TaskListState

**Next Steps**: Proceed to create API contracts and quickstart guide.
