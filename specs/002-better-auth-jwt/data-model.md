# Data Model: Authentication & Security

**Feature**: Authentication & Security (002-better-auth-jwt)
**Date**: 2026-02-08
**Status**: Design Phase

## Overview

This document defines the database schema and data structures for user authentication, JWT token management, and session handling. The design supports stateless JWT authentication with refresh token rotation and secure password storage.

---

## Database Schema

### Table: users

Stores user account information with secure password hashing.

**Note**: This table already exists from Spec-1 (Backend Core & Data Layer). We're extending it with authentication-specific fields.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | VARCHAR(255) | PRIMARY KEY | Unique user identifier (UUID format) |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User's email address (used for login) |
| password_hash | VARCHAR(255) | NOT NULL | Argon2id hashed password |
| is_active | BOOLEAN | DEFAULT TRUE | Account active status (for soft deletion) |
| is_verified | BOOLEAN | DEFAULT FALSE | Email verification status (future use) |
| failed_login_attempts | INTEGER | DEFAULT 0 | Counter for rate limiting and lockout |
| locked_until | TIMESTAMP | NULLABLE | Account lockout expiration timestamp |
| last_login_at | TIMESTAMP | NULLABLE | Last successful login timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes**:
- `idx_users_email` on `email` (for login lookups)
- `idx_users_is_active` on `is_active` (for filtering active users)

**Validation Rules**:
- Email must be valid format (RFC 5322)
- Email must be unique (case-insensitive)
- Password must be at least 8 characters before hashing
- Password hash must use Argon2id algorithm

**State Transitions**:
- New user: `is_active=true`, `is_verified=false`, `failed_login_attempts=0`
- Failed login: Increment `failed_login_attempts`
- Successful login: Reset `failed_login_attempts=0`, update `last_login_at`
- Account lockout: Set `locked_until` to current time + lockout duration (15 minutes)
- Account unlock: Clear `locked_until` when timestamp expires

---

### Table: refresh_tokens

Stores refresh tokens for session management and token rotation.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique token identifier |
| user_id | VARCHAR(255) | FOREIGN KEY → users.id, NOT NULL | Owner of the token |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL | SHA-256 hash of refresh token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration timestamp |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Token creation timestamp |
| revoked_at | TIMESTAMP | NULLABLE | Token revocation timestamp (for logout) |
| replaced_by | INTEGER | FOREIGN KEY → refresh_tokens.id, NULLABLE | Token that replaced this one (rotation) |
| device_info | VARCHAR(500) | NULLABLE | User agent / device information |
| ip_address | VARCHAR(45) | NULLABLE | IP address when token was created |

**Indexes**:
- `idx_refresh_tokens_user_id` on `user_id` (for user's active tokens)
- `idx_refresh_tokens_token_hash` on `token_hash` (for token lookup)
- `idx_refresh_tokens_expires_at` on `expires_at` (for cleanup queries)

**Validation Rules**:
- Token must be cryptographically random (32 bytes minimum)
- Token hash must use SHA-256
- Expires_at must be in the future when created
- User_id must reference existing user

**State Transitions**:
- New token: `revoked_at=NULL`, `replaced_by=NULL`
- Token rotation: Set `replaced_by` to new token ID
- Token revocation: Set `revoked_at` to current timestamp
- Token expiration: Automatic when `expires_at < NOW()`

**Cleanup Strategy**:
- Delete expired tokens older than 30 days (scheduled job)
- Delete revoked tokens older than 7 days (scheduled job)
- Keep token chain history for audit purposes

---

### Table: password_reset_tokens

Stores one-time tokens for password reset functionality.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique token identifier |
| user_id | VARCHAR(255) | FOREIGN KEY → users.id, NOT NULL | User requesting password reset |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL | SHA-256 hash of reset token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration (1 hour from creation) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Token creation timestamp |
| used_at | TIMESTAMP | NULLABLE | When token was used (one-time use) |

**Indexes**:
- `idx_password_reset_tokens_token_hash` on `token_hash` (for token lookup)
- `idx_password_reset_tokens_user_id` on `user_id` (for user's reset requests)

**Validation Rules**:
- Token must be cryptographically random (32 bytes minimum)
- Token expires after 1 hour
- Token can only be used once
- Only one active token per user (invalidate previous on new request)

**State Transitions**:
- New token: `used_at=NULL`
- Token used: Set `used_at` to current timestamp
- Token expiration: Automatic when `expires_at < NOW()`

---

## Data Structures (Pydantic Schemas)

### User Registration

```python
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @validator('password')
    def validate_password(cls, v):
        # Check against common password list
        # Ensure not in breached password database
        return v
```

### User Login

```python
class UserLogin(BaseModel):
    email: EmailStr
    password: str
```

### Token Response

```python
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiration
```

### User Profile

```python
class UserProfile(BaseModel):
    id: str
    email: str
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
```

### JWT Token Payload

```python
class TokenPayload(BaseModel):
    sub: str  # user_id (subject)
    email: str
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp
    type: str  # "access" or "refresh"
```

---

## Relationships

```
users (1) ──< (many) refresh_tokens
users (1) ──< (many) password_reset_tokens
users (1) ──< (many) tasks [from Spec-1]

refresh_tokens (1) ──< (1) refresh_tokens [self-reference for rotation chain]
```

---

## Data Flow

### Registration Flow
1. User submits email + password
2. Validate email format and uniqueness
3. Validate password length (min 8 chars)
4. Check password against breached password database
5. Hash password with Argon2id
6. Create user record in database
7. Generate access token and refresh token
8. Store refresh token hash in database
9. Return access token + set refresh token cookie

### Login Flow
1. User submits email + password
2. Check if account is locked (`locked_until > NOW()`)
3. Lookup user by email
4. Verify password against stored hash
5. If invalid: increment `failed_login_attempts`, lock if >= 10
6. If valid: reset `failed_login_attempts`, update `last_login_at`
7. Generate access token and refresh token
8. Store refresh token hash in database
9. Return access token + set refresh token cookie

### Token Refresh Flow
1. Client sends refresh token (from httpOnly cookie)
2. Hash incoming token and lookup in database
3. Verify token is not expired or revoked
4. Generate new access token
5. Generate new refresh token (rotation)
6. Mark old refresh token as replaced
7. Store new refresh token hash in database
8. Return new access token + set new refresh token cookie

### Logout Flow
1. Client sends refresh token (from httpOnly cookie)
2. Hash incoming token and lookup in database
3. Mark token as revoked (`revoked_at = NOW()`)
4. Clear refresh token cookie
5. Return success response

### Password Reset Flow
1. User requests password reset with email
2. Generate reset token (32 random bytes)
3. Hash token and store in database with 1-hour expiration
4. Send reset link via email with token
5. User clicks link and submits new password
6. Verify token is valid, not expired, not used
7. Hash new password with Argon2id
8. Update user's password_hash
9. Mark reset token as used
10. Revoke all user's refresh tokens (force re-login)

---

## Security Considerations

### Password Storage
- Never store plaintext passwords
- Use Argon2id with parameters: time_cost=2, memory_cost=65536 (64MB)
- Hash time should be ~200-300ms to balance security and UX
- Support password rehashing if algorithm parameters change

### Token Storage
- Store only hashed tokens in database (SHA-256)
- Refresh tokens in httpOnly, secure, sameSite=strict cookies
- Access tokens in memory only (not persisted client-side)
- Tokens include expiration timestamp (exp claim)

### Rate Limiting
- Track failed login attempts per user
- Lock account for 15 minutes after 10 failed attempts
- Rate limit login endpoint: 5 attempts/minute per IP
- Rate limit password reset: 3 requests/hour per email

### Data Retention
- Keep user accounts indefinitely (soft delete with is_active flag)
- Delete expired refresh tokens after 30 days
- Delete used password reset tokens after 7 days
- Log authentication events for security audit

---

## Migration Strategy

### From Spec-1 Schema

The `users` table already exists from Spec-1 with columns:
- id (VARCHAR 255, PRIMARY KEY)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

**Migration Steps**:
1. Add new columns to existing `users` table:
   - email (VARCHAR 255, UNIQUE, NOT NULL)
   - password_hash (VARCHAR 255, NOT NULL)
   - is_active (BOOLEAN, DEFAULT TRUE)
   - is_verified (BOOLEAN, DEFAULT FALSE)
   - failed_login_attempts (INTEGER, DEFAULT 0)
   - locked_until (TIMESTAMP, NULLABLE)
   - last_login_at (TIMESTAMP, NULLABLE)

2. Create new tables:
   - refresh_tokens
   - password_reset_tokens

3. Create indexes as specified above

4. Backfill existing users (if any) with placeholder data:
   - Set email to "user-{id}@placeholder.local"
   - Set password_hash to invalid hash (force password reset)
   - Set is_active to TRUE

**Alembic Migration**:
```python
# alembic/versions/002_add_authentication.py
def upgrade():
    # Add columns to users table
    op.add_column('users', sa.Column('email', sa.String(255), nullable=False))
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=False))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), default=True))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), default=False))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), default=0))
    op.add_column('users', sa.Column('locked_until', sa.TIMESTAMP(), nullable=True))
    op.add_column('users', sa.Column('last_login_at', sa.TIMESTAMP(), nullable=True))

    # Create unique constraint on email
    op.create_unique_constraint('uq_users_email', 'users', ['email'])

    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])

    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_hash', sa.String(255), unique=True, nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('revoked_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('replaced_by', sa.Integer(), sa.ForeignKey('refresh_tokens.id'), nullable=True),
        sa.Column('device_info', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True)
    )

    # Create indexes for refresh_tokens
    op.create_index('idx_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    op.create_index('idx_refresh_tokens_token_hash', 'refresh_tokens', ['token_hash'])
    op.create_index('idx_refresh_tokens_expires_at', 'refresh_tokens', ['expires_at'])

    # Create password_reset_tokens table
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('token_hash', sa.String(255), unique=True, nullable=False),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.func.now()),
        sa.Column('used_at', sa.TIMESTAMP(), nullable=True)
    )

    # Create indexes for password_reset_tokens
    op.create_index('idx_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])
    op.create_index('idx_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
```

---

## Validation & Testing

### Data Integrity Tests
- [ ] Email uniqueness constraint enforced
- [ ] Foreign key constraints prevent orphaned records
- [ ] Timestamps default to current time
- [ ] Boolean fields default correctly
- [ ] Password hash length accommodates Argon2id output

### Security Tests
- [ ] Passwords are never stored in plaintext
- [ ] Token hashes are SHA-256 (64 hex characters)
- [ ] Expired tokens cannot be used
- [ ] Revoked tokens cannot be used
- [ ] Account lockout activates after 10 failed attempts
- [ ] Locked accounts cannot login until lockout expires

### Performance Tests
- [ ] Email lookup query uses index (< 10ms)
- [ ] Token lookup query uses index (< 10ms)
- [ ] Password hashing takes 200-300ms
- [ ] Token cleanup query completes in < 1 second

---

**Document Status**: Design Complete
**Last Updated**: 2026-02-08
**Next Steps**: Generate API contracts, create quickstart guide
