# Research: Backend Core & Data Layer

**Feature**: 001-backend-task-crud
**Date**: 2026-02-08
**Phase**: 0 - Research & Discovery

## Overview

This document consolidates research findings for implementing a task management backend using FastAPI, SQLModel, and Neon Serverless PostgreSQL. Research focused on connection management, architecture patterns, error handling, and testing strategies.

## Key Technical Decisions

### 1. Database Connection Management

**Decision**: Use SQLAlchemy QueuePool with conservative pool settings for long-running FastAPI server

**Rationale**:
- Neon Serverless PostgreSQL has connection limits (100 connections on free tier)
- QueuePool provides efficient connection reuse while preventing exhaustion
- pool_pre_ping ensures connection health before use
- Connection recycling (1800s) aligns with Neon's idle timeout

**Configuration**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Conservative for Neon
    max_overflow=10,       # Total max: 15 connections
    pool_timeout=30,       # Wait for available connection
    pool_recycle=1800,     # Recycle every 30 minutes
    pool_pre_ping=True,    # Verify connection health
)
```

**Alternatives Considered**:
- NullPool: Rejected for long-running servers (creates/closes per request, inefficient)
- Larger pool sizes: Rejected to avoid exhausting Neon connection limits
- Neon's connection pooler: Recommended for serverless functions, not needed for our use case

### 2. Database Driver Selection

**Decision**: Use psycopg2-binary (synchronous driver)

**Rationale**:
- SQLModel is built on SQLAlchemy with mature psycopg2 support
- Simpler reasoning about synchronous CRUD operations
- Battle-tested with SQLAlchemy's connection pooling
- Neon fully supports both psycopg2 and asyncpg

**Alternatives Considered**:
- asyncpg: Rejected for initial implementation (adds complexity, requires async/await throughout)
- Can migrate to asyncpg later if high-concurrency requirements emerge

### 3. Migration Strategy

**Decision**: Use Alembic for database migrations

**Rationale**:
- Provides version control for schema changes
- Supports rollback capabilities
- Industry standard for SQLAlchemy-based projects
- Better for production deployments than SQLModel.metadata.create_all()

**Implementation**:
- Alembic configured to read SQLModel.metadata
- Migrations stored in alembic/versions/
- Development can use create_all() for rapid iteration

**Alternatives Considered**:
- SQLModel.metadata.create_all(): Rejected for production (no version control, no rollback)
- Manual SQL migrations: Rejected (error-prone, no automation)

### 4. Project Architecture

**Decision**: Layered architecture with separation of concerns

**Structure**:
```
backend/
├── src/
│   ├── models/          # SQLModel ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── api/routes/      # FastAPI route handlers
│   ├── services/        # Business logic layer
│   ├── database.py      # Database connection management
│   ├── config.py        # Configuration (env vars)
│   └── main.py          # FastAPI application entry
└── tests/
    ├── unit/            # Unit tests for services
    ├── integration/     # API endpoint tests
    └── conftest.py      # Pytest fixtures
```

**Rationale**:
- Clear separation: Models (data) → Schemas (API) → Services (logic) → Routes (HTTP)
- Testable: Each layer can be tested independently
- Maintainable: Changes isolated to specific layers
- Scalable: Easy to add new features without affecting existing code

**Alternatives Considered**:
- Flat structure: Rejected (becomes unmaintainable as project grows)
- Domain-driven design: Rejected (overkill for CRUD API)

### 5. Request/Response Schema Design

**Decision**: Separate Pydantic schemas from SQLModel models

**Rationale**:
- API contracts independent of database schema
- Allows different validation rules for create/update/read operations
- Prevents exposing internal fields (e.g., password hashes)
- Supports partial updates with optional fields

**Pattern**:
- TaskBase: Shared properties
- Task: SQLModel ORM model (table=True)
- TaskCreate: Request schema for creation
- TaskUpdate: Request schema for updates (all fields optional)
- TaskRead: Response schema with computed fields

**Alternatives Considered**:
- Combined SQLModel models: Rejected (couples API to database schema)
- Single schema for all operations: Rejected (inflexible, security risk)

### 6. User-Scoped Query Enforcement

**Decision**: Enforce user_id filtering at the service layer

**Rationale**:
- Security-critical: Prevents unauthorized data access
- Centralized: All queries go through service layer
- Testable: Service methods can be unit tested
- Consistent: Same pattern across all operations

**Implementation Pattern**:
```python
async def get_task(task_id: int, user_id: str) -> Task:
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id  # Always filter by user
    )
    task = session.exec(statement).first()
    if not task:
        raise TaskNotFoundException(task_id)
    return task
```

**Alternatives Considered**:
- Route-level filtering: Rejected (easy to forget, inconsistent)
- Database-level RLS: Rejected (Neon doesn't support PostgreSQL RLS in free tier)

### 7. Error Handling Strategy

**Decision**: Custom exception classes with global exception handlers

**Rationale**:
- Consistent error responses across all endpoints
- Proper HTTP status codes (404, 403, 400, 500)
- Detailed error messages for debugging
- Separates business logic from HTTP concerns

**HTTP Status Code Mapping**:
- 200 OK: Successful GET/PUT
- 201 Created: Successful POST
- 204 No Content: Successful DELETE
- 400 Bad Request: Invalid input data
- 401 Unauthorized: Missing/invalid authentication
- 403 Forbidden: Valid auth but insufficient permissions
- 404 Not Found: Resource doesn't exist
- 422 Unprocessable Entity: Validation errors
- 500 Internal Server Error: Unexpected errors

**Alternatives Considered**:
- HTTP exceptions in routes: Rejected (duplicates error handling logic)
- Generic error responses: Rejected (poor developer experience)

### 8. Testing Strategy

**Decision**: Separate test PostgreSQL database with transaction-based isolation

**Rationale**:
- Accurate testing: Same database engine as production
- Fast: Transactions rollback after each test
- Isolated: Tests don't interfere with each other
- Reliable: No SQLite dialect differences

**Test Structure**:
- pytest with pytest-asyncio for async support
- Fixtures for database sessions, test users, test data
- Integration tests for full request/response cycles
- Unit tests for service layer business logic
- 80%+ code coverage target

**Alternatives Considered**:
- In-memory SQLite: Rejected (different SQL dialect, unreliable)
- Shared test database: Rejected (tests interfere with each other)
- Mocking database: Rejected (doesn't test actual queries)

### 9. Dependency Injection Pattern

**Decision**: FastAPI Depends() with type annotations

**Rationale**:
- Clean endpoint signatures
- Automatic dependency resolution
- Easy to override for testing
- Type-safe with IDE support

**Pattern**:
```python
SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[str, Depends(get_current_user_id)]

@router.post("/tasks")
async def create_task(
    task_data: TaskCreate,
    current_user_id: CurrentUserDep,
    session: SessionDep
) -> TaskRead:
    # Implementation
```

**Alternatives Considered**:
- Manual dependency passing: Rejected (verbose, error-prone)
- Global session: Rejected (not thread-safe, hard to test)

### 10. Performance Optimizations

**Decisions**:
1. **Indexes**: Add index on Task.user_id for fast user-scoped queries
2. **Pagination**: Implement offset/limit for list endpoints
3. **Query timeouts**: Set statement_timeout=30000 (30 seconds)
4. **Connection timeouts**: Set connect_timeout=10 seconds
5. **Selective loading**: Use select() with specific columns when needed

**Rationale**:
- Prevents slow queries from blocking connections
- Handles large datasets efficiently
- Protects against connection exhaustion
- Meets <2 second response time requirement

## Environment Configuration

**Required Environment Variables**:
```bash
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ENVIRONMENT=development|production
```

**Configuration Management**:
- Use Pydantic BaseSettings for type-safe config
- Load from .env file in development
- Use environment variables in production
- Validate required settings on startup

## Dependencies

**Core Dependencies**:
```
fastapi>=0.104.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
alembic>=1.13.0
```

**Development Dependencies**:
```
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.25.0
pytest-cov>=4.1.0
```

## Security Considerations

1. **User Isolation**: All queries filtered by user_id at service layer
2. **Input Validation**: Pydantic schemas validate all request data
3. **SQL Injection**: SQLModel/SQLAlchemy parameterizes all queries
4. **Connection Security**: SSL required for Neon connections (sslmode=require)
5. **Error Messages**: Don't leak sensitive information in error responses

## Next Steps

Phase 1 artifacts to be created:
1. **data-model.md**: Detailed database schema with relationships
2. **contracts/**: OpenAPI specification for REST endpoints
3. **quickstart.md**: Setup and development guide
4. **Agent context update**: Add technology stack to agent memory

## References

- FastAPI Documentation: https://fastapi.tiangolo.com/
- SQLModel Documentation: https://sqlmodel.tiangolo.com/
- Neon Documentation: https://neon.tech/docs/
- Alembic Documentation: https://alembic.sqlalchemy.org/
