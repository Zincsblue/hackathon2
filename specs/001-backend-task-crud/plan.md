# Implementation Plan: Backend Core & Data Layer

**Branch**: `001-backend-task-crud` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-task-crud/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a persistent task management backend with RESTful API endpoints for CRUD operations. The system enforces user-scoped data isolation, persists tasks in Neon Serverless PostgreSQL using SQLModel ORM, and provides a clean API contract for future frontend integration. Authentication enforcement is deferred to Spec-2; this implementation focuses on data layer and API design with user_id-based scoping.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI, SQLModel, Pydantic, psycopg2 (Neon PostgreSQL driver)
**Storage**: Neon Serverless PostgreSQL (cloud-hosted)
**Testing**: pytest with pytest-asyncio for async endpoint testing
**Target Platform**: Linux server / Cloud deployment (platform-agnostic backend)
**Project Type**: Web application (backend API only)
**Performance Goals**: <2 second response time under normal load, support 100+ concurrent users
**Constraints**: User-scoped data isolation via user_id, no authentication enforcement (deferred to Spec-2), stateless API design
**Scale/Scope**: Multi-user system with unlimited tasks per user, single-region deployment

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **Spec-driven Development** | ✅ PASS | Approved spec exists at specs/001-backend-task-crud/spec.md |
| **Agentic Workflow Compliance** | ✅ PASS | Following spec → plan → tasks → implementation workflow |
| **Security-first Design** | ⚠️ PARTIAL | User_id scoping implemented; JWT authentication deferred to Spec-2 per project plan |
| **Deterministic Behavior** | ✅ PASS | REST API with standard HTTP semantics and consistent error responses |
| **Full-stack Coherence** | ✅ PASS | API contracts will be defined for frontend integration; backend-first approach |
| **No Manual Coding Constraint** | ✅ PASS | Implementation via Claude Code and Spec-Kit Plus only |
| **Technology Stack Requirements** | ✅ PASS | Using FastAPI, SQLModel, Neon PostgreSQL as specified |

**Gate Decision**: PROCEED - All critical gates pass. Security-first design is partially implemented (user_id scoping) with full JWT authentication planned for Spec-2.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # SQLModel database models (Task, User)
│   ├── schemas/         # Pydantic request/response schemas
│   ├── api/             # FastAPI route handlers
│   │   └── routes/      # Task CRUD endpoints
│   ├── services/        # Business logic layer
│   ├── database.py      # Database connection and session management
│   ├── config.py        # Configuration (env vars, Neon connection)
│   └── main.py          # FastAPI application entry point
└── tests/
    ├── unit/            # Unit tests for services and models
    ├── integration/     # Integration tests for API endpoints
    └── conftest.py      # Pytest fixtures and test configuration

.env                     # Environment variables (DATABASE_URL, etc.)
requirements.txt         # Python dependencies
```

**Structure Decision**: Web application backend structure selected. This is a backend-only implementation (frontend deferred to Spec-3). The structure separates concerns: models for data layer, schemas for API contracts, routes for HTTP handlers, and services for business logic. Tests are organized by scope (unit vs integration).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations requiring justification. All constitutional principles are satisfied or have acceptable partial compliance (Security-first Design deferred to Spec-2 per project plan).

---

## Phase 0: Research (COMPLETED)

**Artifacts Created**:
- `research.md` - Technical decisions and best practices

**Key Decisions**:
1. Database connection: QueuePool with conservative settings (pool_size=5)
2. Driver: psycopg2-binary (synchronous)
3. Migrations: Alembic for version control
4. Architecture: Layered (models → schemas → services → routes)
5. Schema design: Separate Pydantic schemas from SQLModel models
6. User scoping: Enforced at service layer
7. Error handling: Custom exceptions with global handlers
8. Testing: Separate PostgreSQL database with transaction isolation

---

## Phase 1: Design & Contracts (COMPLETED)

**Artifacts Created**:
- `data-model.md` - Database schema with User and Task entities
- `contracts/openapi.yaml` - REST API specification
- `quickstart.md` - Setup and development guide
- Updated `CLAUDE.md` - Agent context with technology stack

**Database Schema**:
- **User**: id (PK), email (unique), name, created_at
- **Task**: id (PK), user_id (FK), title, description, completed, created_at, updated_at
- Indexes: user_id, (user_id, completed), created_at
- Foreign key: user_id → users.id ON DELETE CASCADE

**API Endpoints**:
- `GET /health` - Health check
- `GET /users/{user_id}/tasks` - List tasks (paginated)
- `POST /users/{user_id}/tasks` - Create task
- `GET /users/{user_id}/tasks/{task_id}` - Get task
- `PATCH /users/{user_id}/tasks/{task_id}` - Update task
- `DELETE /users/{user_id}/tasks/{task_id}` - Delete task

**HTTP Status Codes**:
- 200 OK, 201 Created, 204 No Content
- 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found
- 422 Unprocessable Entity, 500 Internal Server Error

---

## Constitution Check (Post-Design Re-evaluation)

*Re-checked after Phase 1 design completion*

| Principle | Status | Notes |
|-----------|--------|-------|
| **Spec-driven Development** | ✅ PASS | Complete spec with approved requirements |
| **Agentic Workflow Compliance** | ✅ PASS | Following spec → plan → tasks workflow |
| **Security-first Design** | ✅ PASS | User_id scoping enforced at service layer; JWT auth ready for Spec-2 integration |
| **Deterministic Behavior** | ✅ PASS | REST API with standard HTTP semantics, consistent error responses, predictable state management |
| **Full-stack Coherence** | ✅ PASS | OpenAPI contract defined for frontend integration; clear separation of concerns |
| **No Manual Coding Constraint** | ✅ PASS | All implementation via Claude Code following this plan |
| **Technology Stack Requirements** | ✅ PASS | FastAPI, SQLModel, Neon PostgreSQL as specified; architecture supports Better Auth integration |

**Final Gate Decision**: ✅ APPROVED - All constitutional principles satisfied. Design is ready for task breakdown and implementation.

---

## Next Steps

1. **Run `/sp.tasks`** to generate task breakdown from this plan
2. **Run `/sp.implement`** to execute tasks via Claude Code
3. **Integration with Spec-2**: Authentication layer will add JWT validation to existing endpoints
4. **Integration with Spec-3**: Frontend will consume the REST API defined in contracts/

---

## Summary

This plan establishes a solid foundation for the task management backend:

- **Architecture**: Clean layered design with separation of concerns
- **Data Layer**: User and Task entities with proper relationships and indexes
- **API Layer**: RESTful endpoints with comprehensive OpenAPI specification
- **Security**: User-scoped queries enforced at service layer
- **Testing**: Comprehensive strategy with separate test database
- **Documentation**: Complete quickstart guide for developers

The design follows all constitutional principles and is ready for implementation via the `/sp.tasks` command.
