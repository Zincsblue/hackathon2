# API Client Contract: Frontend & Integration

**Feature**: 003-frontend-integration
**Date**: 2026-02-09
**Status**: Complete

---

## Overview

This document defines the contract for the frontend API client that communicates with the FastAPI backend. The API client is responsible for:

1. Making HTTP requests to backend endpoints
2. Automatically attaching JWT access tokens to requests
3. Handling token refresh when access tokens expire
4. Providing type-safe methods for all API operations
5. Consistent error handling across the application

---

## API Client Interface

### Class: ApiClient

**Location**: `frontend/lib/api-client.ts`

**Purpose**: Centralized HTTP client for all backend API communication

**Constructor**:
```typescript
constructor(config: ApiClientConfig)

interface ApiClientConfig {
  baseUrl: string;                              // Backend API base URL
  getAccessToken: () => string | null;          // Function to get current access token
  setAccessToken: (token: string) => void;      // Function to update access token
  onUnauthorized: () => void;                   // Callback when auth fails (redirect to login)
}
```

---

## Core Methods

### Generic Request Method

```typescript
async request<T>(
  endpoint: string,
  options?: RequestOptions
): Promise<T>

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE';
  body?: any;                                   // Request body (will be JSON stringified)
  headers?: Record<string, string>;             // Additional headers
  skipAuth?: boolean;                           // Skip Authorization header (for login/register)
}
```

**Behavior**:
1. Constructs full URL: `${baseUrl}${endpoint}`
2. Gets access token via `getAccessToken()`
3. Adds `Authorization: Bearer {token}` header (unless `skipAuth: true`)
4. Adds `Content-Type: application/json` header
5. Makes fetch request
6. If response is 401 Unauthorized:
   - Attempts token refresh via `POST /api/v1/auth/refresh`
   - If refresh succeeds: updates token via `setAccessToken()` and retries original request
   - If refresh fails: calls `onUnauthorized()` callback
7. If response is 2xx: parses JSON and returns typed result
8. If response is 4xx/5xx: throws ApiError with details

**Error Handling**:
```typescript
class ApiError extends Error {
  status: number;                               // HTTP status code
  statusText: string;                           // HTTP status text
  body: any;                                    // Response body (parsed JSON)

  constructor(status: number, statusText: string, body: any) {
    super(`API Error ${status}: ${statusText}`);
    this.status = status;
    this.statusText = statusText;
    this.body = body;
  }
}
```

---

## Convenience Methods

### GET Request

```typescript
async get<T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T>
```

**Example**:
```typescript
const tasks = await apiClient.get<TasksResponse>('/tasks');
const user = await apiClient.get<User>('/auth/me');
```

---

### POST Request

```typescript
async post<T>(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T>
```

**Example**:
```typescript
const task = await apiClient.post<Task>('/tasks', {
  title: 'New Task',
  description: 'Task description'
});

const tokens = await apiClient.post<TokenResponse>('/auth/login', {
  email: 'user@example.com',
  password: 'password123'
}, { skipAuth: true });
```

---

### PATCH Request

```typescript
async patch<T>(endpoint: string, data?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T>
```

**Example**:
```typescript
const updatedTask = await apiClient.patch<Task>('/tasks/123', {
  completed: true
});
```

---

### DELETE Request

```typescript
async delete<T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T>
```

**Example**:
```typescript
await apiClient.delete('/tasks/123');
```

---

## Authentication Endpoints

### Register User

**Endpoint**: `POST /api/v1/auth/register`

**Request**:
```typescript
interface RegisterRequest {
  email: string;
  password: string;
  name: string;
}
```

**Response**:
```typescript
interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
```

**Cookies Set**: `refresh_token` (httpOnly, 7-day expiration)

**Usage**:
```typescript
const tokens = await apiClient.post<TokenResponse>('/auth/register', {
  email: 'user@example.com',
  password: 'password123',
  name: 'John Doe'
}, { skipAuth: true });
```

**Error Responses**:
- `409 Conflict`: Email already registered
- `422 Unprocessable Entity`: Validation error (invalid email, weak password)

---

### Login User

**Endpoint**: `POST /api/v1/auth/login`

**Request**:
```typescript
interface LoginRequest {
  email: string;
  password: string;
}
```

**Response**:
```typescript
interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
```

**Cookies Set**: `refresh_token` (httpOnly, 7-day expiration)

**Usage**:
```typescript
const tokens = await apiClient.post<TokenResponse>('/auth/login', {
  email: 'user@example.com',
  password: 'password123'
}, { skipAuth: true });
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials
- `403 Forbidden`: Account locked (too many failed attempts)
- `422 Unprocessable Entity`: Validation error

---

### Refresh Access Token

**Endpoint**: `POST /api/v1/auth/refresh`

**Request**: None (uses refresh token from httpOnly cookie)

**Response**:
```typescript
interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}
```

**Cookies Set**: `refresh_token` (httpOnly, new token - rotation)

**Usage**:
```typescript
// Called automatically by API client on 401 response
const tokens = await apiClient.post<TokenResponse>('/auth/refresh', null, { skipAuth: true });
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired refresh token

---

### Logout User

**Endpoint**: `POST /api/v1/auth/logout`

**Request**: None (uses refresh token from httpOnly cookie)

**Response**: `204 No Content`

**Cookies Cleared**: `refresh_token`

**Usage**:
```typescript
await apiClient.post('/auth/logout');
```

**Error Responses**:
- `401 Unauthorized`: Invalid refresh token

---

### Get Current User

**Endpoint**: `GET /api/v1/auth/me`

**Request**: None (uses access token from Authorization header)

**Response**:
```typescript
interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}
```

**Usage**:
```typescript
const user = await apiClient.get<User>('/auth/me');
```

**Error Responses**:
- `401 Unauthorized`: Invalid or expired access token

---

## Task Endpoints

### Create Task

**Endpoint**: `POST /api/v1/tasks`

**Request**:
```typescript
interface CreateTaskRequest {
  title: string;
  description?: string;
  completed?: boolean;
}
```

**Response**:
```typescript
interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}
```

**Usage**:
```typescript
const task = await apiClient.post<Task>('/tasks', {
  title: 'New Task',
  description: 'Task description'
});
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `422 Unprocessable Entity`: Validation error (title too long, etc.)

---

### List Tasks

**Endpoint**: `GET /api/v1/tasks`

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50)

**Response**:
```typescript
interface TasksResponse {
  tasks: Task[];
  total: number;
  page: number;
  page_size: number;
}
```

**Usage**:
```typescript
const response = await apiClient.get<TasksResponse>('/tasks');
const response = await apiClient.get<TasksResponse>('/tasks?page=2&page_size=20');
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated

---

### Get Task

**Endpoint**: `GET /api/v1/tasks/{id}`

**Path Parameters**:
- `id`: Task UUID

**Response**:
```typescript
interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}
```

**Usage**:
```typescript
const task = await apiClient.get<Task>('/tasks/123e4567-e89b-12d3-a456-426614174000');
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Task belongs to another user
- `404 Not Found`: Task does not exist

---

### Update Task

**Endpoint**: `PATCH /api/v1/tasks/{id}`

**Path Parameters**:
- `id`: Task UUID

**Request**:
```typescript
interface UpdateTaskRequest {
  title?: string;
  description?: string;
  completed?: boolean;
}
```

**Response**:
```typescript
interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}
```

**Usage**:
```typescript
const task = await apiClient.patch<Task>('/tasks/123e4567-e89b-12d3-a456-426614174000', {
  completed: true
});
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Task belongs to another user
- `404 Not Found`: Task does not exist
- `422 Unprocessable Entity`: Validation error

---

### Delete Task

**Endpoint**: `DELETE /api/v1/tasks/{id}`

**Path Parameters**:
- `id`: Task UUID

**Response**: `204 No Content`

**Usage**:
```typescript
await apiClient.delete('/tasks/123e4567-e89b-12d3-a456-426614174000');
```

**Error Responses**:
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Task belongs to another user
- `404 Not Found`: Task does not exist

---

## Token Refresh Flow

The API client automatically handles token refresh when an access token expires:

```
1. Component calls apiClient.get('/tasks')
   ↓
2. API client attaches Authorization header with access token
   ↓
3. Backend returns 401 Unauthorized (token expired)
   ↓
4. API client detects 401 response
   ↓
5. API client calls POST /auth/refresh (with refresh token cookie)
   ↓
6. Backend validates refresh token and returns new access token
   ↓
7. API client updates access token via setAccessToken()
   ↓
8. API client retries original GET /tasks request with new token
   ↓
9. Backend returns 200 OK with tasks
   ↓
10. API client returns tasks to component
```

**If refresh fails**:
```
1. API client calls POST /auth/refresh
   ↓
2. Backend returns 401 Unauthorized (refresh token invalid/expired)
   ↓
3. API client calls onUnauthorized() callback
   ↓
4. AuthContext clears user and token state
   ↓
5. Middleware redirects to login page
```

---

## Error Handling Contract

All API errors are thrown as `ApiError` instances with the following structure:

```typescript
try {
  const task = await apiClient.post<Task>('/tasks', data);
} catch (error) {
  if (error instanceof ApiError) {
    // HTTP error from backend
    console.error(`Status: ${error.status}`);
    console.error(`Message: ${error.message}`);
    console.error(`Body:`, error.body);

    if (error.status === 422) {
      // Validation error - display field errors
      const fieldErrors = error.body.detail;
      // Map to form fields
    } else if (error.status === 401) {
      // Unauthorized - user will be redirected to login
    } else {
      // Other error - display general error message
    }
  } else {
    // Network error or other exception
    console.error('Network error:', error);
  }
}
```

---

## Rate Limiting

The backend enforces rate limits on all endpoints:

- **Registration**: 3 requests/minute per IP
- **Login**: 5 requests/minute per IP
- **Token Refresh**: 20 requests/minute per IP
- **Other Endpoints**: 100 requests/minute per user

**Rate Limit Response**: `429 Too Many Requests`

**Frontend Handling**:
- Display error message: "Too many requests. Please try again later."
- Optionally implement exponential backoff for retries

---

## CORS Configuration

The backend is configured to accept requests from the frontend origin:

**Development**: `http://localhost:3000`
**Production**: (to be configured)

**Allowed Methods**: GET, POST, PATCH, DELETE, OPTIONS
**Allowed Headers**: Authorization, Content-Type
**Credentials**: Included (for httpOnly cookies)

---

## Summary

The API client contract defines:

1. **Type-safe interface** for all backend API operations
2. **Automatic token management** with refresh handling
3. **Consistent error handling** across the application
4. **11 API endpoints** covering authentication and task management
5. **Clear request/response formats** for all operations

This contract ensures the frontend integrates seamlessly with the existing backend (Spec-1 and Spec-2) without requiring any backend modifications.

**Next Steps**: Create quickstart guide for developers.
