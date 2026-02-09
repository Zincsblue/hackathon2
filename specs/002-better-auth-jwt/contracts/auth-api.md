# Authentication API Contract

**Version**: 1.0.0
**Base URL**: `/api/v1/auth`
**Date**: 2026-02-08

## Overview

This document defines the REST API contract for authentication operations including user registration, login, token refresh, logout, and password reset.

---

## Authentication Flow

```
1. Registration: POST /auth/register → Returns access token + sets refresh token cookie
2. Login: POST /auth/login → Returns access token + sets refresh token cookie
3. API Access: Include "Authorization: Bearer {access_token}" header
4. Token Refresh: POST /auth/refresh → Returns new access token + new refresh token cookie
5. Logout: POST /auth/logout → Revokes refresh token, clears cookie
```

---

## Endpoints

### 1. User Registration

**Endpoint**: `POST /api/v1/auth/register`

**Description**: Create a new user account with email and password.

**Rate Limit**: 3 requests per minute per IP

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| email | string | Yes | Valid email format, max 255 chars | User's email address |
| password | string | Yes | Min 8 chars, max 128 chars | User's password |

**Success Response** (201 Created):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-02-08T10:30:00Z"
  }
}
```

**Response Headers**:
```
Set-Cookie: refresh_token={token}; HttpOnly; Secure; SameSite=Strict; Max-Age=604800; Path=/api/v1/auth
```

**Error Responses**:

**400 Bad Request** - Invalid input:
```json
{
  "detail": "Invalid email format"
}
```

**409 Conflict** - Email already exists:
```json
{
  "detail": "Email already registered"
}
```

**422 Unprocessable Entity** - Validation error:
```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Password must be at least 8 characters",
      "type": "value_error"
    }
  ]
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "detail": "Too many registration attempts. Please try again later."
}
```

---

### 2. User Login

**Endpoint**: `POST /api/v1/auth/login`

**Description**: Authenticate user with email and password, receive access token.

**Rate Limit**: 5 requests per minute per IP

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| email | string | Yes | Valid email format | User's email address |
| password | string | Yes | Any length | User's password |

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "is_active": true,
    "is_verified": false,
    "last_login_at": "2026-02-08T10:30:00Z"
  }
}
```

**Response Headers**:
```
Set-Cookie: refresh_token={token}; HttpOnly; Secure; SameSite=Strict; Max-Age=604800; Path=/api/v1/auth
```

**Error Responses**:

**401 Unauthorized** - Invalid credentials:
```json
{
  "detail": "Invalid email or password"
}
```

**403 Forbidden** - Account locked:
```json
{
  "detail": "Account locked due to too many failed login attempts. Try again in 15 minutes.",
  "locked_until": "2026-02-08T10:45:00Z"
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "detail": "Too many login attempts. Please try again later."
}
```

---

### 3. Refresh Access Token

**Endpoint**: `POST /api/v1/auth/refresh`

**Description**: Exchange refresh token for new access token (token rotation).

**Rate Limit**: 20 requests per minute per user

**Request Headers**:
```
Cookie: refresh_token={token}
```

**Request Body**: None (empty)

**Success Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

**Response Headers**:
```
Set-Cookie: refresh_token={new_token}; HttpOnly; Secure; SameSite=Strict; Max-Age=604800; Path=/api/v1/auth
```

**Error Responses**:

**401 Unauthorized** - Invalid or expired refresh token:
```json
{
  "detail": "Invalid or expired refresh token"
}
```

**401 Unauthorized** - Revoked refresh token:
```json
{
  "detail": "Refresh token has been revoked"
}
```

---

### 4. Logout

**Endpoint**: `POST /api/v1/auth/logout`

**Description**: Revoke refresh token and clear session.

**Rate Limit**: 10 requests per minute per user

**Request Headers**:
```
Cookie: refresh_token={token}
```

**Request Body**: None (empty)

**Success Response** (204 No Content):
- Empty body
- Refresh token cookie cleared

**Response Headers**:
```
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0; Path=/api/v1/auth
```

**Error Responses**:

**401 Unauthorized** - No refresh token provided:
```json
{
  "detail": "No refresh token provided"
}
```

---

### 5. Get Current User

**Endpoint**: `GET /api/v1/auth/me`

**Description**: Get current authenticated user's profile.

**Authentication**: Required (Bearer token)

**Rate Limit**: 100 requests per minute per user

**Request Headers**:
```
Authorization: Bearer {access_token}
```

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "is_active": true,
  "is_verified": false,
  "last_login_at": "2026-02-08T10:30:00Z",
  "created_at": "2026-02-01T08:00:00Z"
}
```

**Error Responses**:

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 6. Request Password Reset

**Endpoint**: `POST /api/v1/auth/password-reset/request`

**Description**: Request password reset email with reset token.

**Rate Limit**: 3 requests per hour per email

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Success Response** (200 OK):
```json
{
  "message": "If an account exists with this email, a password reset link has been sent."
}
```

**Note**: Always returns success to prevent email enumeration attacks.

**Error Responses**:

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "detail": "Too many password reset requests. Please try again later."
}
```

---

### 7. Reset Password

**Endpoint**: `POST /api/v1/auth/password-reset/confirm`

**Description**: Reset password using token from email.

**Rate Limit**: 5 requests per minute per IP

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "token": "a1b2c3d4e5f6...",
  "new_password": "newsecurepassword456"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| token | string | Yes | 64 hex characters | Reset token from email |
| new_password | string | Yes | Min 8 chars, max 128 chars | New password |

**Success Response** (200 OK):
```json
{
  "message": "Password has been reset successfully"
}
```

**Error Responses**:

**400 Bad Request** - Invalid or expired token:
```json
{
  "detail": "Invalid or expired reset token"
}
```

**400 Bad Request** - Token already used:
```json
{
  "detail": "Reset token has already been used"
}
```

**422 Unprocessable Entity** - Weak password:
```json
{
  "detail": "Password does not meet security requirements"
}
```

---

## Common Response Fields

### User Object
```json
{
  "id": "string (UUID)",
  "email": "string",
  "is_active": "boolean",
  "is_verified": "boolean",
  "last_login_at": "string (ISO 8601) | null",
  "created_at": "string (ISO 8601)"
}
```

### Token Response
```json
{
  "access_token": "string (JWT)",
  "token_type": "string (always 'bearer')",
  "expires_in": "integer (seconds)"
}
```

### Error Response
```json
{
  "detail": "string (error message)"
}
```

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request (login, refresh, password reset) |
| 201 | Created | Resource created (registration) |
| 204 | No Content | Successful request with no body (logout) |
| 400 | Bad Request | Invalid input or business logic error |
| 401 | Unauthorized | Missing, invalid, or expired authentication |
| 403 | Forbidden | Valid auth but insufficient permissions (locked account) |
| 409 | Conflict | Resource already exists (duplicate email) |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected server error |

---

## Authentication Header Format

All protected endpoints require the `Authorization` header:

```
Authorization: Bearer {access_token}
```

Example:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NTBlODQwMC1lMjliLTQxZDQtYTcxNi00NDY2NTU0NDAwMDAiLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJleHAiOjE3MDczOTg0MDAsImlhdCI6MTcwNzM5NzUwMCwidHlwZSI6ImFjY2VzcyJ9.signature
```

---

## JWT Token Structure

### Access Token Payload
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "exp": 1707398400,
  "iat": 1707397500,
  "type": "access"
}
```

### Refresh Token Payload
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "exp": 1708002300,
  "iat": 1707397500,
  "type": "refresh",
  "jti": "unique-token-id"
}
```

**Token Claims**:
- `sub` (subject): User ID
- `email`: User's email address (access token only)
- `exp` (expiration): Unix timestamp when token expires
- `iat` (issued at): Unix timestamp when token was issued
- `type`: Token type ("access" or "refresh")
- `jti` (JWT ID): Unique token identifier (refresh token only)

---

## Cookie Configuration

### Refresh Token Cookie

**Name**: `refresh_token`

**Attributes**:
- `HttpOnly`: true (prevents JavaScript access)
- `Secure`: true (HTTPS only in production)
- `SameSite`: Strict (CSRF protection)
- `Max-Age`: 604800 (7 days in seconds)
- `Path`: /api/v1/auth (scoped to auth endpoints)

**Example**:
```
Set-Cookie: refresh_token=a1b2c3d4...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800; Path=/api/v1/auth
```

---

## Rate Limiting

Rate limits are enforced per endpoint to prevent abuse:

| Endpoint | Limit | Window | Key |
|----------|-------|--------|-----|
| POST /auth/register | 3 requests | 1 minute | IP address |
| POST /auth/login | 5 requests | 1 minute | IP address |
| POST /auth/refresh | 20 requests | 1 minute | User ID |
| POST /auth/logout | 10 requests | 1 minute | User ID |
| GET /auth/me | 100 requests | 1 minute | User ID |
| POST /auth/password-reset/request | 3 requests | 1 hour | Email |
| POST /auth/password-reset/confirm | 5 requests | 1 minute | IP address |

**Rate Limit Headers** (included in all responses):
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1707397560
```

**Rate Limit Exceeded Response** (429):
```json
{
  "detail": "Rate limit exceeded. Try again in 45 seconds."
}
```

---

## Security Considerations

### Password Security
- Minimum 8 characters required
- Check against common password list (Have I Been Pwned)
- Hash with Argon2id before storage
- Never return password or hash in responses

### Token Security
- Access tokens expire in 15 minutes
- Refresh tokens expire in 7 days
- Refresh tokens stored in httpOnly cookies
- Token rotation on refresh (old token invalidated)
- All tokens signed with HS256 algorithm

### Account Security
- Account locked after 10 failed login attempts
- Lockout duration: 15 minutes
- Failed attempts counter reset on successful login
- Password reset tokens expire in 1 hour
- Password reset tokens are single-use

### API Security
- All endpoints use HTTPS in production
- CORS configured for allowed origins only
- Rate limiting on all endpoints
- Input validation on all requests
- SQL injection prevention via parameterized queries

---

## Error Handling

All errors follow consistent format:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors (422):
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "type": "error_type"
    }
  ]
}
```

**Error Messages**:
- Never reveal whether email exists (registration/password reset)
- Use generic "Invalid email or password" for login failures
- Don't specify which field was incorrect
- Provide helpful messages without security details

---

## Testing Checklist

### Registration
- [ ] Valid registration creates user and returns tokens
- [ ] Duplicate email returns 409 Conflict
- [ ] Invalid email format returns 422
- [ ] Short password returns 422
- [ ] Rate limit enforced (3/min per IP)

### Login
- [ ] Valid credentials return tokens
- [ ] Invalid credentials return 401
- [ ] Account lockout after 10 failures
- [ ] Locked account returns 403
- [ ] Rate limit enforced (5/min per IP)

### Token Refresh
- [ ] Valid refresh token returns new access token
- [ ] Expired refresh token returns 401
- [ ] Revoked refresh token returns 401
- [ ] Token rotation invalidates old token

### Logout
- [ ] Logout revokes refresh token
- [ ] Logout clears cookie
- [ ] Revoked token cannot be used

### Password Reset
- [ ] Request sends email (if account exists)
- [ ] Request doesn't reveal if email exists
- [ ] Valid token resets password
- [ ] Expired token returns 400
- [ ] Used token returns 400
- [ ] Reset revokes all refresh tokens

---

**Document Status**: Contract Complete
**Last Updated**: 2026-02-08
**Next Steps**: Implement endpoints in FastAPI
