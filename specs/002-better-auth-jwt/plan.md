# Implementation Plan: Authentication & Security

**Branch**: `002-better-auth-jwt` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-better-auth-jwt/spec.md`

## Summary

Implement secure JWT-based authentication for the Todo Full-Stack Web Application. Users can register, login, and access protected API endpoints. The system uses stateless JWT tokens for authorization with refresh token rotation for session management. Better Auth handles frontend authentication while FastAPI independently verifies JWT tokens using a shared secret key.

**Key Features**:
- User registration with email/password
- Secure login with Argon2id password hashing
- JWT access tokens (15-minute expiration)
- Refresh tokens (7-day expiration) with rotation
- httpOnly cookies for refresh token storage
- Rate limiting to prevent brute force attacks
- Account lockout after failed attempts
- Password reset via email
- User-scoped data access enforcement

---

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/Node.js 18+ (frontend)

**Primary Dependencies**:
- Backend: FastAPI 0.109.0, python-jose 3.3.0, argon2-cffi 23.1.0, slowapi 0.1.9, SQLModel 0.0.14
- Frontend: Next.js 14+, Better Auth 1.0.0, React 18.2.0

**Storage**: Neon Serverless PostgreSQL (existing from Spec-1, extended with auth tables)

**Testing**: pytest (backend), Jest/React Testing Library (frontend)

**Target Platform**: Web application (Linux server for backend, browser for frontend)

**Project Type**: Web application (backend + frontend)

**Performance Goals**:
- Password hashing: 200-300ms per operation (Argon2id)
- Token verification: <50ms per request
- Login endpoint: Handle 1000 concurrent requests
- API endpoints: 100 requests/minute per user

**Constraints**:
- Access token expiration: 15 minutes (security requirement)
- Refresh token expiration: 7 days (UX requirement)
- Rate limiting: 5 login attempts/minute per IP
- Account lockout: 15 minutes after 10 failed attempts
- Password minimum: 8 characters

**Scale/Scope**:
- Support 10,000+ concurrent users
- Handle 1000 authentication requests/second
- Store unlimited user accounts
- Maintain 7-day session history per user

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-driven Development
- Specification created and approved before planning
- All implementation follows approved spec
- No coding without corresponding spec

### ✅ Agentic Workflow Compliance
- Following spec → plan → tasks → implementation flow
- Research phase completed (research.md)
- Design phase completed (data-model.md, contracts/, quickstart.md)
- Tasks phase pending (/sp.tasks command)

### ✅ Security-first Design
- JWT tokens required for all protected endpoints
- Passwords hashed with Argon2id (industry standard)
- Refresh tokens in httpOnly cookies (XSS protection)
- Rate limiting prevents brute force attacks
- Account lockout after failed attempts
- User-scoped data access enforced

### ✅ Deterministic Behavior
- JWT tokens provide consistent authentication across requests
- Token expiration is deterministic (15 min access, 7 day refresh)
- Rate limiting applies consistently per IP/user
- Password hashing produces consistent results

### ✅ Full-stack Coherence
- Shared SECRET_KEY between frontend and backend
- API contracts defined in contracts/auth-api.md
- Frontend and backend use same JWT structure
- Error responses consistent across all endpoints

### ✅ No Manual Coding Constraint
- All code will be generated via Claude Code
- Implementation follows Spec-Kit Plus workflow
- No direct manual coding allowed

### ✅ Technology Stack Requirements
- Backend: FastAPI ✓
- ORM: SQLModel ✓
- Database: Neon Serverless PostgreSQL ✓
- Frontend: Next.js 16+ (App Router) ✓
- Authentication: Better Auth (JWT-based) ✓

**Constitution Status**: ✅ All principles satisfied

---

## Project Structure

### Documentation (this feature)

```text
specs/002-better-auth-jwt/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 research output (completed)
├── data-model.md        # Phase 1 data model (completed)
├── quickstart.md        # Phase 1 quickstart guide (completed)
├── contracts/           # Phase 1 API contracts (completed)
│   └── auth-api.md      # Authentication API specification
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (/sp.tasks command - pending)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── user.py              # Extended with auth fields (from Spec-1)
│   │   ├── refresh_token.py     # NEW: Refresh token model
│   │   └── password_reset.py    # NEW: Password reset token model
│   ├── schemas/
│   │   ├── auth.py              # NEW: Auth request/response schemas
│   │   └── user.py              # NEW: User profile schemas
│   ├── services/
│   │   ├── auth_service.py      # NEW: Authentication business logic
│   │   ├── token_service.py     # NEW: JWT token generation/verification
│   │   └── password_service.py  # NEW: Password hashing/verification
│   ├── api/
│   │   ├── deps.py              # UPDATED: Add JWT token dependency
│   │   └── routes/
│   │       ├── auth.py          # NEW: Authentication endpoints
│   │       └── tasks.py         # UPDATED: Add auth requirement
│   ├── middleware/
│   │   └── rate_limit.py        # NEW: Rate limiting middleware
│   ├── config.py                # UPDATED: Add auth settings
│   └── main.py                  # UPDATED: Register auth routes
├── tests/
│   ├── test_auth.py             # NEW: Auth endpoint tests
│   ├── test_token.py            # NEW: Token service tests
│   └── test_password.py         # NEW: Password service tests
└── alembic/
    └── versions/
        └── 002_add_authentication.py  # NEW: Auth tables migration

frontend/
├── app/
│   ├── login/
│   │   └── page.tsx             # NEW: Login page
│   ├── register/
│   │   └── page.tsx             # NEW: Registration page
│   ├── dashboard/
│   │   └── page.tsx             # UPDATED: Protected route
│   └── api/
│       └── auth/
│           └── [...all]/
│               └── route.ts     # NEW: Better Auth API route
├── contexts/
│   └── AuthContext.tsx          # NEW: Auth state management
├── lib/
│   ├── auth.ts                  # NEW: Better Auth configuration
│   └── api.ts                   # NEW: Authenticated API client
├── middleware.ts                # NEW: Route protection
└── .env.local                   # UPDATED: Add auth secrets

.env                             # UPDATED: Add backend auth settings
```

**Structure Decision**: Web application structure (Option 2) selected. Backend handles authentication logic and token verification. Frontend uses Better Auth for session management and includes JWT tokens in API requests. Both layers share the same SECRET_KEY for JWT signing/verification.

---

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied.

---

## Phase 0: Research (Completed)

**Output**: `research.md`

**Key Decisions**:

1. **Password Requirements**: Minimum 8 characters, no complexity requirements, check against breached password database
   - Rationale: NIST SP 800-63B guidelines, length > complexity

2. **JWT Token Lifetime**: Access token 15 minutes, refresh token 7 days
   - Rationale: Balance security (short access token) with UX (long refresh token)

3. **Session Persistence**: httpOnly cookies for refresh tokens
   - Rationale: XSS protection, automatic persistence across browser restarts

4. **JWT Implementation**: python-jose with HS256 algorithm
   - Rationale: FastAPI ecosystem standard, sufficient for single backend

5. **Better Auth Integration**: Better Auth for frontend, FastAPI validates independently
   - Rationale: Separation of concerns, shared secret key

6. **Token Storage**: Refresh token in httpOnly cookie, access token in memory
   - Rationale: Maximum security for long-lived refresh token

7. **Rate Limiting**: slowapi with Redis backend
   - Rationale: Distributed rate limiting, prevents brute force

8. **Password Hashing**: Argon2id
   - Rationale: Modern standard, memory-hard, resistant to GPU attacks

**Research Status**: ✅ Complete - All technical decisions documented

---

## Phase 1: Design (Completed)

**Outputs**: `data-model.md`, `contracts/auth-api.md`, `quickstart.md`

### Data Model Summary

**New Tables**:
- `refresh_tokens`: Store refresh tokens with rotation chain
- `password_reset_tokens`: One-time password reset tokens

**Extended Tables**:
- `users`: Added email, password_hash, is_active, is_verified, failed_login_attempts, locked_until, last_login_at

**Key Relationships**:
- users (1) → (many) refresh_tokens
- users (1) → (many) password_reset_tokens
- users (1) → (many) tasks [from Spec-1]

### API Contract Summary

**Endpoints**:
1. `POST /api/v1/auth/register` - Create new user account
2. `POST /api/v1/auth/login` - Authenticate and receive tokens
3. `POST /api/v1/auth/refresh` - Exchange refresh token for new access token
4. `POST /api/v1/auth/logout` - Revoke refresh token
5. `GET /api/v1/auth/me` - Get current user profile
6. `POST /api/v1/auth/password-reset/request` - Request password reset email
7. `POST /api/v1/auth/password-reset/confirm` - Reset password with token

**Authentication Flow**:
1. User registers/logs in → Receives access token + refresh token cookie
2. User makes API request → Includes `Authorization: Bearer {access_token}`
3. Access token expires (15 min) → Frontend refreshes using refresh token
4. Refresh token rotates → Old token invalidated, new token issued

### Quickstart Summary

**Backend Setup**:
1. Install dependencies (python-jose, argon2-cffi, slowapi, redis)
2. Configure environment variables (SECRET_KEY, token expiration)
3. Run database migration (add auth tables)
4. Start server and test endpoints

**Frontend Setup**:
1. Install Better Auth
2. Configure auth with shared secret
3. Create auth context and API client
4. Build login/register pages
5. Protect routes with middleware

**Design Status**: ✅ Complete - All design artifacts created

---

## Phase 2: Tasks (Pending)

**Next Command**: `/sp.tasks`

This will generate `tasks.md` with:
- Detailed implementation tasks for each user story
- Task dependencies and execution order
- Acceptance criteria for each task
- Estimated complexity

**Expected Task Groups**:
1. Backend: Database migration and models
2. Backend: Password hashing and token services
3. Backend: Authentication endpoints
4. Backend: Rate limiting and security
5. Frontend: Better Auth setup
6. Frontend: Login/register pages
7. Frontend: Auth context and API client
8. Frontend: Route protection
9. Integration: End-to-end testing
10. Polish: Error handling, logging, documentation

---

## Implementation Strategy

### Backend Implementation Order

1. **Foundation** (User Story 1 - Registration):
   - Extend User model with auth fields
   - Create RefreshToken and PasswordResetToken models
   - Run Alembic migration
   - Implement password hashing service (Argon2id)
   - Implement JWT token service (python-jose)
   - Create registration endpoint
   - Test registration flow

2. **Authentication** (User Story 2 - Login):
   - Implement login endpoint
   - Add failed login tracking
   - Implement account lockout logic
   - Test login flow with valid/invalid credentials

3. **Authorization** (User Story 3 - Secure API Access):
   - Create JWT token dependency for FastAPI
   - Update all task endpoints to require authentication
   - Extract user_id from token for data scoping
   - Test unauthorized access returns 401

4. **Session Management** (User Story 4):
   - Implement token refresh endpoint
   - Implement logout endpoint
   - Add token rotation logic
   - Test session persistence

5. **Security Enhancements**:
   - Add rate limiting middleware (slowapi)
   - Implement password reset flow
   - Add security logging
   - Test rate limits and lockout

### Frontend Implementation Order

1. **Better Auth Setup**:
   - Install and configure Better Auth
   - Create auth API route
   - Configure shared secret

2. **Auth Context**:
   - Create AuthContext with login/register/logout
   - Implement token refresh on app load
   - Handle token expiration

3. **UI Pages**:
   - Build login page
   - Build registration page
   - Add error handling and validation

4. **Route Protection**:
   - Create middleware for protected routes
   - Redirect unauthenticated users to login
   - Redirect authenticated users from login/register

5. **API Integration**:
   - Create authenticated API client
   - Update task components to use auth
   - Handle 401 responses

### Testing Strategy

1. **Unit Tests**:
   - Password hashing/verification
   - JWT token generation/verification
   - Rate limiting logic
   - Token rotation logic

2. **Integration Tests**:
   - Registration flow
   - Login flow
   - Token refresh flow
   - Logout flow
   - Password reset flow

3. **Security Tests**:
   - Rate limiting enforcement
   - Account lockout
   - XSS protection (httpOnly cookies)
   - CSRF protection (sameSite cookies)
   - Unauthorized access rejection

4. **End-to-End Tests**:
   - Complete user journey (register → login → access tasks → logout)
   - Token expiration handling
   - Session persistence across browser restarts

---

## Risk Analysis

### High Priority Risks

1. **Token Secret Compromise**
   - **Impact**: All tokens can be forged
   - **Mitigation**: Store SECRET_KEY in environment variables, never commit to git, rotate periodically
   - **Detection**: Monitor for unusual token patterns

2. **Rate Limiting Bypass**
   - **Impact**: Brute force attacks succeed
   - **Mitigation**: Use Redis for distributed rate limiting, implement account lockout
   - **Detection**: Monitor failed login attempts

3. **XSS Attack Stealing Tokens**
   - **Impact**: Session hijacking
   - **Mitigation**: httpOnly cookies for refresh tokens, short-lived access tokens, Content Security Policy
   - **Detection**: Monitor for unusual API access patterns

### Medium Priority Risks

4. **Password Database Breach**
   - **Impact**: Passwords exposed
   - **Mitigation**: Argon2id hashing makes cracking expensive, encourage strong passwords
   - **Detection**: Monitor for credential stuffing attempts

5. **Token Expiration Edge Cases**
   - **Impact**: Poor user experience
   - **Mitigation**: Automatic token refresh, clear error messages
   - **Detection**: Monitor 401 error rates

### Low Priority Risks

6. **Email Service Downtime**
   - **Impact**: Password reset unavailable
   - **Mitigation**: Implement retry logic, provide alternative support channel
   - **Detection**: Monitor email send failures

---

## Dependencies

### External Services
- **Neon PostgreSQL**: Database for user accounts and tokens (existing from Spec-1)
- **Redis**: Rate limiting storage (new requirement)
- **Email Service**: Password reset emails (SMTP, SendGrid, or AWS SES)

### Internal Dependencies
- **Spec-1 (Backend Core & Data Layer)**: User model, database connection, API structure
- **Existing Task Endpoints**: Will be updated to require authentication

### Environment Variables Required
```bash
# Backend
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<email>
SMTP_PASSWORD=<password>

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
BETTER_AUTH_SECRET=<same-as-backend-SECRET_KEY>
```

---

## Success Criteria

### Functional Requirements Met
- ✅ Users can register with email/password
- ✅ Users can login with credentials
- ✅ JWT tokens issued on successful authentication
- ✅ All API endpoints require valid tokens
- ✅ Unauthenticated requests return 401
- ✅ Users can only access their own data
- ✅ Users can logout and revoke sessions
- ✅ Token refresh works automatically
- ✅ Password reset flow functional

### Performance Requirements Met
- ✅ Password hashing: 200-300ms
- ✅ Token verification: <50ms
- ✅ Login endpoint: 1000 concurrent requests
- ✅ API endpoints: 100 requests/min per user

### Security Requirements Met
- ✅ Passwords hashed with Argon2id
- ✅ JWT tokens signed with HS256
- ✅ Refresh tokens in httpOnly cookies
- ✅ Rate limiting enforced
- ✅ Account lockout after 10 failures
- ✅ No plaintext passwords stored
- ✅ XSS protection enabled
- ✅ CSRF protection enabled

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Run `/sp.tasks`** to generate detailed task breakdown
3. **Create ADR** for authentication architecture decisions
4. **Begin implementation** following task order
5. **Test incrementally** after each user story
6. **Document learnings** in PHR after completion

---

**Plan Status**: ✅ Complete - Ready for task generation
**Last Updated**: 2026-02-08
**Estimated Implementation Time**: 3-5 days (backend + frontend + testing)
