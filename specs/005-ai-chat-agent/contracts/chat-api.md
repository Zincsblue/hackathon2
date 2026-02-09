# API Contract: Chat Endpoint

**Feature**: 005-ai-chat-agent
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document defines the API contract for the AI Chat Agent endpoint. The endpoint enables natural language task management through conversational interactions with an AI agent.

## Endpoint

### POST /api/{user_id}/chat

Send a message to the AI agent and receive a response.

**Path Parameters**:
- `user_id` (string, required): User identifier from JWT token

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

## Request Schema

```json
{
  "message": "string (required, 1-10000 characters)",
  "conversation_id": "integer (optional)"
}
```

**Field Descriptions**:
- `message`: User's natural language message to the AI agent
- `conversation_id`: Optional conversation ID to continue existing conversation. If not provided, creates new conversation or uses existing one for the user.

**Request Validation**:
- `message` must not be empty or whitespace-only
- `message` length must be between 1 and 10,000 characters
- `conversation_id` must be a valid integer if provided
- `conversation_id` must belong to the authenticated user

**Example Request**:
```json
{
  "message": "Create a task to buy groceries",
  "conversation_id": 123
}
```

## Response Schema

### Success Response (200 OK)

```json
{
  "conversation_id": "integer",
  "message": {
    "role": "string",
    "content": "string",
    "created_at": "string (ISO 8601 datetime)"
  }
}
```

**Field Descriptions**:
- `conversation_id`: ID of the conversation (new or existing)
- `message.role`: Always "assistant" for responses
- `message.content`: AI agent's natural language response
- `message.created_at`: Timestamp when response was generated

**Example Success Response**:
```json
{
  "conversation_id": 123,
  "message": {
    "role": "assistant",
    "content": "I've created a task: 'Buy groceries'. Is there anything else you'd like me to help with?",
    "created_at": "2026-02-09T10:30:00Z"
  }
}
```

### Error Response (4xx/5xx)

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

**Field Descriptions**:
- `error.code`: Machine-readable error code (see Error Codes section)
- `error.message`: Human-readable error message
- `error.details`: Optional additional error context

## Error Codes

### Authentication Errors (401)

**UNAUTHORIZED**
- Description: Invalid or missing JWT token
- HTTP Status: 401 Unauthorized
- Example:
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing authentication token"
  }
}
```

**USER_MISMATCH**
- Description: user_id in path doesn't match JWT token
- HTTP Status: 401 Unauthorized
- Example:
```json
{
  "error": {
    "code": "USER_MISMATCH",
    "message": "User ID in path does not match authenticated user"
  }
}
```

### Client Errors (400)

**INVALID_INPUT**
- Description: Malformed request body or invalid parameters
- HTTP Status: 400 Bad Request
- Example:
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Message field is required and cannot be empty",
    "details": {
      "field": "message",
      "constraint": "required"
    }
  }
}
```

**MESSAGE_TOO_LONG**
- Description: Message exceeds maximum length
- HTTP Status: 400 Bad Request
- Example:
```json
{
  "error": {
    "code": "MESSAGE_TOO_LONG",
    "message": "Message exceeds maximum length of 10000 characters",
    "details": {
      "max_length": 10000,
      "actual_length": 15000
    }
  }
}
```

**CONVERSATION_NOT_FOUND**
- Description: Specified conversation_id doesn't exist or doesn't belong to user
- HTTP Status: 404 Not Found
- Example:
```json
{
  "error": {
    "code": "CONVERSATION_NOT_FOUND",
    "message": "Conversation not found or access denied",
    "details": {
      "conversation_id": 999
    }
  }
}
```

### MCP Tool Errors (502)

**MCP_TOOL_ERROR**
- Description: MCP tool invocation failed
- HTTP Status: 502 Bad Gateway
- Example:
```json
{
  "error": {
    "code": "MCP_TOOL_ERROR",
    "message": "Failed to create task: Task title cannot be empty",
    "details": {
      "tool": "add_task",
      "mcp_error": "INVALID_INPUT"
    }
  }
}
```

**MCP_UNAVAILABLE**
- Description: MCP server is unreachable
- HTTP Status: 503 Service Unavailable
- Example:
```json
{
  "error": {
    "code": "MCP_UNAVAILABLE",
    "message": "Task management service is temporarily unavailable",
    "details": {
      "retry_after": 30
    }
  }
}
```

### AI Agent Errors (502)

**OPENAI_API_ERROR**
- Description: OpenAI API request failed
- HTTP Status: 502 Bad Gateway
- Example:
```json
{
  "error": {
    "code": "OPENAI_API_ERROR",
    "message": "AI agent is temporarily unavailable",
    "details": {
      "openai_error": "rate_limit_exceeded"
    }
  }
}
```

**AGENT_TIMEOUT**
- Description: AI agent processing exceeded timeout
- HTTP Status: 504 Gateway Timeout
- Example:
```json
{
  "error": {
    "code": "AGENT_TIMEOUT",
    "message": "Request processing exceeded maximum time limit",
    "details": {
      "timeout_seconds": 5
    }
  }
}
```

### Server Errors (500)

**INTERNAL_ERROR**
- Description: Unexpected server error
- HTTP Status: 500 Internal Server Error
- Example:
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred. Please try again later."
  }
}
```

## Request/Response Examples

### Example 1: Create Task

**Request**:
```http
POST /api/user123/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Create a task to buy milk and eggs"
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I've created a task: 'Buy milk and eggs'. Would you like me to add any additional details or set a priority?",
    "created_at": "2026-02-09T10:30:00Z"
  }
}
```

### Example 2: List Tasks

**Request**:
```http
POST /api/user123/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "What are my tasks?",
  "conversation_id": 1
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "You have 2 tasks:\n1. Buy milk and eggs (not completed)\n2. Call the dentist (not completed)\n\nWould you like to mark any as complete or add more tasks?",
    "created_at": "2026-02-09T10:31:00Z"
  }
}
```

### Example 3: Complete Task

**Request**:
```http
POST /api/user123/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "I finished buying milk and eggs",
  "conversation_id": 1
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "Great! I've marked 'Buy milk and eggs' as completed. You now have 1 remaining task.",
    "created_at": "2026-02-09T10:32:00Z"
  }
}
```

### Example 4: Ambiguous Request

**Request**:
```http
POST /api/user123/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "groceries",
  "conversation_id": 1
}
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I'm not sure what you'd like me to do with 'groceries'. Would you like me to:\n1. Create a new task for groceries\n2. Show you existing grocery-related tasks\n3. Something else?",
    "created_at": "2026-02-09T10:33:00Z"
  }
}
```

### Example 5: Error - Unauthorized

**Request**:
```http
POST /api/user123/chat HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "message": "Create a task"
}
```

**Response**:
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing authentication token"
  }
}
```

### Example 6: Error - MCP Tool Failure

**Request**:
```http
POST /api/user123/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "message": "Complete task 999",
  "conversation_id": 1
}
```

**Response**:
```http
HTTP/1.1 502 Bad Gateway
Content-Type: application/json

{
  "error": {
    "code": "MCP_TOOL_ERROR",
    "message": "I couldn't find a task with that ID. Would you like to see your current tasks?",
    "details": {
      "tool": "complete_task",
      "mcp_error": "TASK_NOT_FOUND"
    }
  }
}
```

## Performance Characteristics

### Response Time Targets
- **p50**: < 1.5 seconds
- **p95**: < 3 seconds
- **p99**: < 5 seconds
- **Timeout**: 5 seconds (hard limit)

### Rate Limiting
- **Per User**: 60 requests per minute
- **Global**: 1000 requests per minute
- **Rate Limit Headers**:
  ```
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1675951200
  ```

## Security Requirements

### Authentication
- All requests MUST include valid JWT Bearer token
- Token MUST contain `user_id` claim
- Token MUST be verified using Better Auth secret key
- `user_id` in path MUST match `user_id` in token

### Authorization
- Users can only access their own conversations
- Conversation ownership validated on every request
- Cross-user conversation access returns 404 (not 403 to prevent enumeration)

### Input Validation
- Message content sanitized to prevent XSS
- SQL injection prevented by parameterized queries
- Maximum message length enforced (10,000 characters)
- Conversation ID validated as integer

### Data Privacy
- Conversation history never exposed across users
- Error messages don't leak sensitive information
- Logs don't contain message content (only metadata)

## Versioning

**Current Version**: v1

**Version Strategy**: URL path versioning (e.g., `/api/v1/{user_id}/chat`)

**Backward Compatibility**: Breaking changes require new version endpoint

## Testing Requirements

### Unit Tests
- Request validation (valid/invalid inputs)
- Response serialization
- Error handling for each error code
- JWT token validation

### Integration Tests
- Full conversation flow (create → continue → resume)
- MCP tool invocation success and failure
- OpenAI API integration
- Database persistence and retrieval
- User isolation enforcement

### Performance Tests
- Response time under normal load
- Concurrent request handling
- Rate limiting behavior
- Timeout handling

## OpenAPI Specification

```yaml
openapi: 3.0.0
info:
  title: AI Chat Agent API
  version: 1.0.0
  description: Natural language task management via AI agent

paths:
  /api/{user_id}/chat:
    post:
      summary: Send message to AI agent
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
              properties:
                message:
                  type: string
                  minLength: 1
                  maxLength: 10000
                conversation_id:
                  type: integer
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  conversation_id:
                    type: integer
                  message:
                    type: object
                    properties:
                      role:
                        type: string
                        enum: [assistant]
                      content:
                        type: string
                      created_at:
                        type: string
                        format: date-time
        '400':
          description: Invalid input
        '401':
          description: Unauthorized
        '404':
          description: Conversation not found
        '502':
          description: MCP or OpenAI error
        '503':
          description: Service unavailable
        '504':
          description: Request timeout

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```
