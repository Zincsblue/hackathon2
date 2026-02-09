---
description: "Task list for Backend Core & Data Layer implementation"
---

# Tasks: Backend Core & Data Layer

**Input**: Design documents from `/specs/001-backend-task-crud/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/openapi.yaml

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are excluded per the optional testing policy.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md, this project uses:
- **Backend**: `backend/src/` for source code
- **Tests**: `backend/tests/` for test files
- **Root**: `.env`, `requirements.txt`, `alembic/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create backend directory structure with src/, tests/, and subdirectories per plan.md
- [X] T002 Create requirements.txt with FastAPI, SQLModel, psycopg2-binary, Pydantic, python-jose, Alembic, uvicorn dependencies
- [X] T003 Create requirements-dev.txt with pytest, pytest-asyncio, httpx, pytest-cov, black, ruff dependencies
- [X] T004 [P] Create .env.example file with DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, ENVIRONMENT template
- [X] T005 [P] Create .gitignore for Python project (venv/, __pycache__/, .env, *.pyc, .pytest_cache/, htmlcov/)
- [X] T006 [P] Create README.md with project overview and setup instructions

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create backend/src/config.py with Pydantic Settings for environment configuration (DATABASE_URL, JWT settings)
- [X] T008 Create backend/src/database.py with SQLAlchemy engine, session factory, and get_session dependency using QueuePool settings from research.md
- [X] T009 [P] Create backend/src/models/__init__.py as package initializer
- [X] T010 [P] Create backend/src/models/user.py with User SQLModel (id, email, name, created_at) per data-model.md
- [X] T011 [P] Create backend/src/models/task.py with Task SQLModel (id, user_id, title, description, completed, created_at, updated_at) per data-model.md
- [X] T012 Initialize Alembic in project root with alembic init alembic command
- [X] T013 Configure alembic/env.py to import SQLModel metadata and use DATABASE_URL from config
- [X] T014 Create initial Alembic migration for users and tasks tables with indexes per data-model.md
- [X] T015 [P] Create backend/src/exceptions/__init__.py as package initializer
- [X] T016 [P] Create backend/src/exceptions/handlers.py with custom exceptions (TaskNotFoundException, TaskAccessDeniedException, DatabaseException) and global exception handlers
- [X] T017 [P] Create backend/src/api/__init__.py as package initializer
- [X] T018 [P] Create backend/src/api/deps.py with get_current_user_id dependency (mock implementation for now, returns user_id from path)
- [X] T019 Create backend/src/main.py with FastAPI app initialization, CORS middleware, exception handler registration, and health endpoint
- [X] T020 [P] Create backend/tests/conftest.py with pytest fixtures for database session and test client

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Task (Priority: P1) 🎯 MVP

**Goal**: Enable users to create new tasks with title, description, and completion status

**Independent Test**: Send POST request to /users/{user_id}/tasks with valid task data and verify task is persisted in database with proper user scoping

**Acceptance Criteria**:
- User can create task with title "Buy groceries" and receive 201 Created response
- Task is linked to correct user_id
- Invalid data (missing title) returns 400 Bad Request with validation errors

### Implementation for User Story 1

- [X] T021 [P] [US1] Create backend/src/schemas/__init__.py as package initializer
- [X] T022 [P] [US1] Create backend/src/schemas/task.py with TaskCreate schema (title, description, completed fields) per contracts/openapi.yaml
- [X] T023 [P] [US1] Add TaskRead schema to backend/src/schemas/task.py (id, user_id, title, description, completed, created_at, updated_at)
- [X] T024 [P] [US1] Create backend/src/services/__init__.py as package initializer
- [X] T025 [US1] Create backend/src/services/task_service.py with TaskService class and create_task method enforcing user_id scoping
- [X] T026 [P] [US1] Create backend/src/api/routes/__init__.py as package initializer
- [X] T027 [US1] Create backend/src/api/routes/tasks.py with POST /users/{user_id}/tasks endpoint using TaskService.create_task
- [X] T028 [US1] Register tasks router in backend/src/main.py with /api/v1 prefix
- [X] T029 [US1] Add request validation and error handling for create task endpoint (400 for invalid data, 422 for validation errors)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via POST endpoint

---

## Phase 4: User Story 2 - Retrieve Tasks (Priority: P1)

**Goal**: Enable users to view all their tasks or retrieve a specific task by ID

**Independent Test**: Send GET request to /users/{user_id}/tasks and verify only tasks belonging to authenticated user are returned

**Acceptance Criteria**:
- User can retrieve list of their tasks with pagination
- User can retrieve specific task by ID
- User cannot access tasks belonging to other users (returns 404)
- List endpoint supports filtering by completion status

### Implementation for User Story 2

- [X] T030 [P] [US2] Add TaskListResponse schema to backend/src/schemas/task.py (tasks array, total, page, page_size)
- [X] T031 [US2] Add list_tasks method to backend/src/services/task_service.py with pagination (skip, limit) and optional status filter, enforcing user_id scoping
- [X] T032 [US2] Add get_task method to backend/src/services/task_service.py with user_id ownership check, raising TaskNotFoundException if not found
- [X] T033 [US2] Add GET /users/{user_id}/tasks endpoint to backend/src/api/routes/tasks.py with pagination query parameters (page, page_size, completed filter)
- [X] T034 [US2] Add GET /users/{user_id}/tasks/{task_id} endpoint to backend/src/api/routes/tasks.py using TaskService.get_task
- [X] T035 [US2] Add error handling for retrieve endpoints (404 for not found, 403 for access denied)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create and retrieve tasks

---

## Phase 5: User Story 3 - Update Task (Priority: P2)

**Goal**: Enable users to update their existing tasks (title, description, completion status)

**Independent Test**: Send PATCH request to update a task and verify only the task owner can modify it

**Acceptance Criteria**:
- User can update task title and receive 200 OK response
- User can toggle task completion status
- User cannot update tasks belonging to other users (returns 404)
- Partial updates are supported (only provided fields are updated)

### Implementation for User Story 3

- [X] T036 [P] [US3] Add TaskUpdate schema to backend/src/schemas/task.py with optional fields (title, description, completed) per contracts/openapi.yaml
- [X] T037 [US3] Add update_task method to backend/src/services/task_service.py with user_id ownership check and partial update support, updating updated_at timestamp
- [X] T038 [US3] Add PATCH /users/{user_id}/tasks/{task_id} endpoint to backend/src/api/routes/tasks.py using TaskService.update_task
- [X] T039 [US3] Add error handling for update endpoint (404 for not found, 403 for access denied, 422 for validation errors)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - users can create, retrieve, and update tasks

---

## Phase 6: User Story 4 - Delete Task (Priority: P2)

**Goal**: Enable users to permanently delete their tasks

**Independent Test**: Send DELETE request to remove a task and verify only the task owner can delete it

**Acceptance Criteria**:
- User can delete their own task and receive 204 No Content response
- User cannot delete tasks belonging to other users (returns 404)
- Deleted task is permanently removed from database

### Implementation for User Story 4

- [X] T040 [US4] Add delete_task method to backend/src/services/task_service.py with user_id ownership check
- [X] T041 [US4] Add DELETE /users/{user_id}/tasks/{task_id} endpoint to backend/src/api/routes/tasks.py using TaskService.delete_task
- [X] T042 [US4] Add error handling for delete endpoint (404 for not found, 403 for access denied)

**Checkpoint**: All user stories should now be independently functional - complete CRUD operations available

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T043 [P] Add logging to all TaskService methods using Python logging module
- [X] T044 [P] Add API documentation docstrings to all endpoints in backend/src/api/routes/tasks.py
- [X] T045 [P] Verify all HTTP status codes match contracts/openapi.yaml specification (200, 201, 204, 400, 401, 403, 404, 422, 500)
- [ ] T046 Run Alembic migration (alembic upgrade head) to create database tables
- [ ] T047 Test health endpoint (GET /health) returns correct status and database connection info
- [ ] T048 Validate all endpoints against contracts/openapi.yaml using manual testing or API client
- [ ] T049 [P] Run code formatting with black backend/
- [ ] T050 [P] Run linting with ruff check backend/
- [ ] T051 Verify quickstart.md instructions work end-to-end (setup, run server, test endpoints)
- [X] T052 Create sample .env file with working Neon DATABASE_URL for development
- [ ] T046 Run Alembic migration (alembic upgrade head) to create database tables
- [ ] T047 Test health endpoint (GET /health) returns correct status and database connection info
- [ ] T048 Validate all endpoints against contracts/openapi.yaml using manual testing or API client
- [ ] T049 [P] Run code formatting with black backend/
- [ ] T050 [P] Run linting with ruff check backend/
- [ ] T051 Verify quickstart.md instructions work end-to-end (setup, run server, test endpoints)
- [ ] T052 Create sample .env file with working Neon DATABASE_URL for development

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent but uses TaskRead schema from US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent but uses TaskService from US1/US2
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent but uses TaskService from US1/US2

### Within Each User Story

- Schemas before services (services use schemas)
- Services before routes (routes use services)
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: T004, T005, T006 can run in parallel

**Phase 2 (Foundational)**:
- T009, T010, T011 can run in parallel (model files)
- T015, T016, T017, T018, T020 can run in parallel (different packages)

**Phase 3 (US1)**:
- T021, T022, T023, T024 can run in parallel (different packages/files)

**Phase 4 (US2)**:
- T030 can run in parallel with T031 (schema vs service)

**Phase 5 (US3)**:
- T036 can run in parallel with T037 (schema vs service)

**Phase 7 (Polish)**:
- T043, T044, T045, T049, T050 can run in parallel (different concerns)

**Cross-Story Parallelization**:
- Once Foundational (Phase 2) completes, User Stories 1-4 can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch schema tasks together:
Task T021: "Create backend/src/schemas/__init__.py"
Task T022: "Create TaskCreate schema in backend/src/schemas/task.py"
Task T023: "Add TaskRead schema to backend/src/schemas/task.py"
Task T024: "Create backend/src/services/__init__.py"

# Then launch service and route setup:
Task T025: "Create TaskService with create_task method"
Task T026: "Create backend/src/api/routes/__init__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T020) - CRITICAL
3. Complete Phase 3: User Story 1 (T021-T029)
4. **STOP and VALIDATE**: Test task creation independently
5. Deploy/demo if ready

**MVP Deliverable**: Users can create tasks via REST API with proper validation and user scoping

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Can create AND view)
4. Add User Story 3 → Test independently → Deploy/Demo (Can create, view, AND update)
5. Add User Story 4 → Test independently → Deploy/Demo (Full CRUD complete)
6. Polish → Final validation → Production ready

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T020)
2. Once Foundational is done:
   - Developer A: User Story 1 (T021-T029)
   - Developer B: User Story 2 (T030-T035)
   - Developer C: User Story 3 (T036-T039)
   - Developer D: User Story 4 (T040-T042)
3. Stories complete and integrate independently
4. Team completes Polish together (T043-T052)

---

## Task Summary

**Total Tasks**: 52
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 14 tasks
- Phase 3 (US1 - Create Task): 9 tasks
- Phase 4 (US2 - Retrieve Tasks): 6 tasks
- Phase 5 (US3 - Update Task): 4 tasks
- Phase 6 (US4 - Delete Task): 3 tasks
- Phase 7 (Polish): 10 tasks

**Parallel Opportunities**: 15 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- US1: POST task creation works with validation
- US2: GET task retrieval works with user scoping
- US3: PATCH task update works with ownership check
- US4: DELETE task removal works with ownership check

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 29 tasks

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests are NOT included per specification (not explicitly requested)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths use backend/ prefix per plan.md structure
- Database migrations handled via Alembic (T012-T014, T046)
- User scoping enforced at service layer per research.md decisions
