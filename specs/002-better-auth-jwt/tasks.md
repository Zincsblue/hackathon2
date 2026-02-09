# Tasks: Authentication & Security

**Input**: Design documents from `/specs/002-better-auth-jwt/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/auth-api.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`
- **Frontend**: `frontend/`
- **Database**: `alembic/versions/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Update project configuration for authentication dependencies

- [x] T001 [P] Add authentication dependencies to requirements.txt (python-jose, argon2-cffi, slowapi, redis)
- [x] T002 [P] Update .env.example with authentication settings (SECRET_KEY, ALGORITHM, token expiration, REDIS_URL)
- [x] T003 [P] Update backend/src/config.py to load authentication environment variables

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Alembic migration 002_add_authentication.py to extend users table and create refresh_tokens, password_reset_tokens tables
- [ ] T005 Run Alembic migration: `alembic upgrade head`
- [x] T006 [P] Create backend/src/models/refresh_token.py with RefreshToken SQLModel
- [x] T007 [P] Create backend/src/models/password_reset.py with PasswordResetToken SQLModel
- [x] T008 [P] Update backend/src/models/user.py to add authentication fields (email, password_hash, is_active, is_verified, failed_login_attempts, locked_until, last_login_at)
- [x] T009 [P] Create backend/src/services/password_service.py with Argon2id password hashing and verification
- [x] T010 [P] Create backend/src/services/token_service.py with JWT token generation and verification using python-jose
- [x] T011 [P] Create backend/src/middleware/rate_limit.py with slowapi rate limiting configuration
- [x] T012 Update backend/src/main.py to register rate limiting middleware

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: New users can create accounts with email and password, receive JWT tokens, and be automatically logged in

**Independent Test**: Submit registration form with valid credentials, verify account creation in database, verify access token returned, verify refresh token cookie set

### Implementation for User Story 1

- [x] T013 [P] [US1] Create backend/src/schemas/auth.py with UserRegister, UserLogin, TokenResponse schemas
- [x] T014 [P] [US1] Create backend/src/schemas/user.py with UserProfile schema
- [x] T015 [US1] Create backend/src/services/auth_service.py with register_user method (depends on T009, T010)
- [x] T016 [US1] Create backend/src/api/routes/auth.py with POST /api/v1/auth/register endpoint
- [x] T017 [US1] Register auth routes in backend/src/main.py with prefix /api/v1/auth
- [ ] T018 [US1] Test registration with valid email and password via curl or API docs
- [ ] T019 [US1] Test registration with duplicate email returns 409 Conflict
- [ ] T020 [US1] Test registration with invalid password returns 422 Validation Error
- [ ] T021 [US1] Verify user record created in database with hashed password
- [ ] T022 [US1] Verify access token returned in response body
- [ ] T023 [US1] Verify refresh token set in httpOnly cookie

**Checkpoint**: At this point, User Story 1 should be fully functional - users can register and receive tokens

---

## Phase 4: User Story 2 - User Login (Priority: P2)

**Goal**: Registered users can log in with email and password, receive JWT tokens, and access their account

**Independent Test**: Log in with valid credentials, verify access token returned, verify refresh token cookie set, verify failed login tracking works

### Implementation for User Story 2

- [x] T024 [US2] Add login_user method to backend/src/services/auth_service.py with password verification and token generation
- [x] T025 [US2] Add POST /api/v1/auth/login endpoint to backend/src/api/routes/auth.py
- [x] T026 [US2] Implement failed login attempt tracking in auth_service.py (increment failed_login_attempts on failure)
- [x] T027 [US2] Implement account lockout logic in auth_service.py (lock account for 15 minutes after 10 failed attempts)
- [x] T028 [US2] Add last_login_at timestamp update on successful login
- [ ] T029 [US2] Test login with valid credentials returns tokens
- [ ] T030 [US2] Test login with invalid credentials returns 401 Unauthorized
- [ ] T031 [US2] Test account lockout after 10 failed login attempts returns 403 Forbidden
- [ ] T032 [US2] Verify failed_login_attempts counter increments on failed login
- [ ] T033 [US2] Verify failed_login_attempts resets to 0 on successful login

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can register and login

---

## Phase 5: User Story 3 - Secure API Access (Priority: P3)

**Goal**: All API endpoints require valid JWT tokens, unauthenticated requests return 401, user data is properly scoped

**Independent Test**: Make API requests with and without tokens, verify authenticated requests succeed and unauthenticated requests return 401, verify users can only access their own data

### Implementation for User Story 3

- [x] T034 [US3] Create get_current_user_from_token dependency in backend/src/api/deps.py that extracts and validates JWT from Authorization header
- [x] T035 [US3] Update backend/src/api/routes/tasks.py to use get_current_user_from_token instead of get_current_user_id
- [x] T036 [US3] Add GET /api/v1/auth/me endpoint to backend/src/api/routes/auth.py to return current user profile
- [ ] T037 [US3] Test task endpoints without Authorization header return 401 Unauthorized
- [ ] T038 [US3] Test task endpoints with invalid token return 401 Unauthorized
- [ ] T039 [US3] Test task endpoints with expired token return 401 Unauthorized
- [ ] T040 [US3] Test task endpoints with valid token return user's tasks only
- [ ] T041 [US3] Test user cannot access another user's tasks (403 Forbidden)
- [ ] T042 [US3] Test GET /auth/me returns current user profile

**Checkpoint**: All user stories should now be independently functional - registration, login, and secure API access work

---

## Phase 6: User Story 4 - Session Management (Priority: P4)

**Goal**: Users can refresh tokens, logout to end sessions, and handle token expiration gracefully

**Independent Test**: Refresh access token using refresh token cookie, logout and verify token revoked, verify expired tokens are rejected

### Implementation for User Story 4

- [x] T043 [US4] Add refresh_access_token method to backend/src/services/auth_service.py with token rotation logic
- [x] T044 [US4] Add POST /api/v1/auth/refresh endpoint to backend/src/api/routes/auth.py
- [x] T045 [US4] Add logout_user method to backend/src/services/auth_service.py to revoke refresh token
- [x] T046 [US4] Add POST /api/v1/auth/logout endpoint to backend/src/api/routes/auth.py
- [ ] T047 [US4] Test token refresh with valid refresh token returns new access token
- [ ] T048 [US4] Test token refresh with invalid refresh token returns 401 Unauthorized
- [ ] T049 [US4] Test token refresh with expired refresh token returns 401 Unauthorized
- [ ] T050 [US4] Test token rotation: old refresh token is invalidated after refresh
- [ ] T051 [US4] Test logout revokes refresh token in database
- [ ] T052 [US4] Test logout clears refresh token cookie
- [ ] T053 [US4] Test revoked refresh token cannot be used for refresh

**Checkpoint**: All core authentication features complete - registration, login, secure access, and session management

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Additional features and improvements that affect multiple user stories

- [ ] T054 [P] Add POST /api/v1/auth/password-reset/request endpoint for password reset email
- [ ] T055 [P] Add POST /api/v1/auth/password-reset/confirm endpoint to reset password with token
- [ ] T056 [P] Create backend/src/services/email_service.py for sending password reset emails
- [x] T057 [P] Add security logging for authentication events (login success/failure, token refresh, logout)
- [x] T058 [P] Add CORS configuration in backend/src/main.py for frontend origin
- [x] T059 [P] Update IMPLEMENTATION_STATUS.md with authentication setup instructions
- [x] T060 Validate all endpoints match contracts/auth-api.md specifications
- [x] T061 Run quickstart.md validation: test complete registration → login → API access → logout flow
- [x] T062 [P] Add rate limiting to all authentication endpoints per contracts/auth-api.md
- [x] T063 [P] Add security headers (Content-Security-Policy, X-Frame-Options, etc.)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - No dependencies on other stories (independent)
  - User Story 3 (P3): Depends on User Story 1 and 2 (needs users to exist and login to work)
  - User Story 4 (P4): Depends on User Story 1 and 2 (needs authentication to work)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Independent of US1 but typically done after
- **User Story 3 (P3)**: Requires US1 and US2 complete (needs users and login to test secure access)
- **User Story 4 (P4)**: Requires US1 and US2 complete (needs authentication to test session management)

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before testing
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001, T002, T003)
- All Foundational tasks marked [P] can run in parallel after migration (T006-T011)
- Within User Story 1: T013 and T014 can run in parallel (different schema files)
- Once Foundational phase completes, User Story 1 and User Story 2 can start in parallel (if team capacity allows)
- All Polish tasks marked [P] can run in parallel (T054-T058, T062-T063)

---

## Parallel Example: Foundational Phase

```bash
# After migration (T004, T005), launch all model and service tasks together:
Task: "Create backend/src/models/refresh_token.py with RefreshToken SQLModel"
Task: "Create backend/src/models/password_reset.py with PasswordResetToken SQLModel"
Task: "Update backend/src/models/user.py to add authentication fields"
Task: "Create backend/src/services/password_service.py with Argon2id"
Task: "Create backend/src/services/token_service.py with JWT"
Task: "Create backend/src/middleware/rate_limit.py with slowapi"
```

---

## Parallel Example: User Story 1

```bash
# Launch schema creation tasks together:
Task: "Create backend/src/schemas/auth.py with UserRegister, UserLogin, TokenResponse schemas"
Task: "Create backend/src/schemas/user.py with UserProfile schema"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T012) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T013-T023)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready - users can now register!

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP - registration works!)
3. Add User Story 2 → Test independently → Deploy/Demo (users can login!)
4. Add User Story 3 → Test independently → Deploy/Demo (API is secured!)
5. Add User Story 4 → Test independently → Deploy/Demo (session management works!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Registration)
   - Developer B: User Story 2 (Login) - can work in parallel with US1
3. After US1 and US2 complete:
   - Developer A: User Story 3 (Secure API Access)
   - Developer B: User Story 4 (Session Management)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Password reset (T054-T056) is optional - can be deferred to later iteration
- Rate limiting (T062) should be added early for security
- Security headers (T063) should be added before production deployment

---

## Task Summary

- **Total Tasks**: 63
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 9 tasks (BLOCKING)
- **User Story 1 (Registration)**: 11 tasks
- **User Story 2 (Login)**: 10 tasks
- **User Story 3 (Secure API Access)**: 9 tasks
- **User Story 4 (Session Management)**: 11 tasks
- **Polish Phase**: 10 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-3 (23 tasks) delivers user registration with JWT authentication

**Independent Test Criteria**:
- US1: Register new user → verify account created → verify tokens returned
- US2: Login with credentials → verify tokens returned → verify failed login tracking
- US3: Make API requests with/without tokens → verify 401 for unauthenticated → verify data isolation
- US4: Refresh token → verify new token → logout → verify token revoked
