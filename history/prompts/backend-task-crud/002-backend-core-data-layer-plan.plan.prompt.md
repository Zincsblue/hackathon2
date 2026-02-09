---
id: 002
title: Backend Core Data Layer Plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: backend-task-crud
branch: 001-backend-task-crud
user: user
command: /sp.plan
labels: ["planning", "architecture", "backend", "database", "api-design"]
links:
  spec: specs/001-backend-task-crud/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-backend-task-crud/plan.md
 - specs/001-backend-task-crud/research.md
 - specs/001-backend-task-crud/data-model.md
 - specs/001-backend-task-crud/contracts/openapi.yaml
 - specs/001-backend-task-crud/quickstart.md
 - CLAUDE.md
tests:
 - None (planning phase)
---

## Prompt

Create:
High-level backend architecture (FastAPI + SQLModel + Neon)

Database schema for User and Task

REST API contract for task operations

Decisions needing documentation:
Task schema fields and relationships

User-task ownership enforcement via user_id

Error-handling strategy and HTTP status usage

Testing & validation:
Verify CRUD operations against database

Confirm user-scoped queries return correct data

Validate persistence across restarts

## Response snapshot

Completed comprehensive implementation plan for Backend Core & Data Layer feature.

**Phase 0: Research (Completed)**
- Launched 3 specialized agents (neon-db-ops, fastapi-backend) to research best practices
- Consolidated findings into research.md covering 10 key technical decisions:
  1. Database connection management (QueuePool with pool_size=5)
  2. Driver selection (psycopg2-binary)
  3. Migration strategy (Alembic)
  4. Project architecture (layered: models → schemas → services → routes)
  5. Schema design (separate Pydantic from SQLModel)
  6. User scoping enforcement (service layer)
  7. Error handling (custom exceptions with global handlers)
  8. Testing strategy (separate PostgreSQL database)
  9. Dependency injection (FastAPI Depends)
  10. Performance optimizations (indexes, pagination, timeouts)

**Phase 1: Design & Contracts (Completed)**
- Created data-model.md with complete database schema:
  - User entity: id (PK), email (unique), name, created_at
  - Task entity: id (PK), user_id (FK), title, description, completed, created_at, updated_at
  - Indexes on user_id, (user_id, completed), created_at
  - Foreign key with CASCADE delete
  - SQLModel implementations provided

- Created contracts/openapi.yaml with REST API specification:
  - 6 endpoints for task CRUD operations
  - Complete request/response schemas
  - HTTP status code mappings (200, 201, 204, 400, 401, 403, 404, 422, 500)
  - Bearer token authentication (JWT)
  - Pagination support for list endpoint

- Created quickstart.md with developer guide:
  - Setup instructions (Python 3.11+, virtual environment, dependencies)
  - Environment configuration (.env with DATABASE_URL)
  - Database migration commands (Alembic)
  - API usage examples with curl commands
  - Testing instructions (pytest with coverage)
  - Troubleshooting guide

- Updated CLAUDE.md agent context with technology stack

**Constitution Check (Post-Design)**
- All 7 constitutional principles pass validation
- Security-first design: User_id scoping enforced at service layer
- Full-stack coherence: OpenAPI contract ready for frontend integration
- Technology stack requirements: FastAPI, SQLModel, Neon PostgreSQL confirmed

**Project Structure Defined**:
```
backend/
├── src/
│   ├── models/          # SQLModel ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── api/routes/      # FastAPI route handlers
│   ├── services/        # Business logic layer
│   ├── database.py      # Connection management
│   ├── config.py        # Configuration
│   └── main.py          # FastAPI app entry
└── tests/
    ├── unit/            # Unit tests
    ├── integration/     # API endpoint tests
    └── conftest.py      # Pytest fixtures
```

## Outcome

- ✅ Impact: Complete implementation plan ready for task breakdown (/sp.tasks)
- 🧪 Tests: Testing strategy defined (pytest, separate test DB, transaction isolation)
- 📁 Files: 5 planning artifacts created (plan.md, research.md, data-model.md, openapi.yaml, quickstart.md)
- 🔁 Next prompts: /sp.tasks (generate task breakdown), /sp.implement (execute implementation)
- 🧠 Reflection: Comprehensive planning with research-backed decisions; layered architecture supports maintainability and testability; user scoping enforced at service layer ensures security

## Evaluation notes (flywheel)

- Failure modes observed: None - all research agents completed successfully
- Graders run and results (PASS/FAIL): Constitution Check - PASS (7/7 principles)
- Prompt variant (if applicable): Standard /sp.plan workflow with Phase 0 research and Phase 1 design
- Next experiment (smallest change to try): Consider adding ADR for significant architectural decisions (layered architecture, user scoping strategy)
