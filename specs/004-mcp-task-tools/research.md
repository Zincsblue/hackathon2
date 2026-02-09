# Research: MCP Server & Task Tools

**Feature**: 004-mcp-task-tools
**Date**: 2026-02-09
**Status**: Complete

## Research Topics

### 1. Official MCP SDK Usage

**Decision**: Use the Official MCP SDK Python package (`mcp`) for server implementation

**Rationale**:
- Official SDK provides standardized MCP protocol implementation
- Handles tool registration, discovery, and invocation automatically
- Provides built-in error handling and validation patterns
- Ensures compatibility with MCP-compliant AI agents

**Key Patterns**:
- Server initialization: Create MCP server instance with tool registry
- Tool registration: Decorate functions with `@mcp.tool()` decorator
- Tool schemas: Define using Pydantic models for input/output validation
- Lifecycle management: Start/stop server with proper cleanup

**Alternatives Considered**:
- Custom MCP protocol implementation: Rejected due to complexity and maintenance burden
- REST API wrapper: Rejected as it doesn't follow MCP protocol standards

### 2. Database Connection Strategy

**Decision**: Create independent database connection pool for MCP server, separate from FastAPI backend

**Rationale**:
- MCP server runs as independent process
- Separate connection pool prevents resource contention with FastAPI backend
- Allows independent scaling and restart without affecting backend
- Maintains stateless architecture (no shared in-memory state)

**Implementation Approach**:
- Use SQLModel's `create_engine()` with connection pooling
- Configure pool size based on expected concurrent tool invocations (default: 10 connections)
- Reuse existing Neon PostgreSQL connection string from environment variables
- Implement connection retry logic with exponential backoff

**Alternatives Considered**:
- Shared connection pool with FastAPI: Rejected due to process isolation requirements
- Connection per request: Rejected due to performance overhead

### 3. SQLModel Integration

**Decision**: Import and reuse Task model from existing backend codebase

**Rationale**:
- Maintains single source of truth for Task schema
- Ensures compatibility with Spec-1 backend
- Avoids schema drift between MCP server and backend
- Simplifies maintenance (schema changes in one place)

**Implementation Approach**:
- Import Task model from `backend.src.models.task`
- Use SQLModel's session management for database operations
- Implement user-scoped queries with `WHERE user_id = ?` filters
- Use transactions for atomic operations

**Query Patterns**:
```python
# List tasks for user
tasks = session.exec(select(Task).where(Task.user_id == user_id)).all()

# Get task with user validation
task = session.exec(
    select(Task).where(Task.id == task_id, Task.user_id == user_id)
).first()
```

**Alternatives Considered**:
- Duplicate Task model in MCP server: Rejected due to maintenance burden
- Raw SQL queries: Rejected in favor of SQLModel ORM for type safety

### 4. Tool Schema Design

**Decision**: Use Pydantic models for tool input/output schemas with structured error responses

**Rationale**:
- Pydantic provides automatic validation and serialization
- Type-safe schemas prevent runtime errors
- Clear contract definition for AI agents
- Consistent error format across all tools

**Schema Structure**:

**Input Schema Example**:
```python
class AddTaskInput(BaseModel):
    user_id: int
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
```

**Output Schema Example**:
```python
class TaskOutput(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime
```

**Error Response Format**:
```python
class ErrorResponse(BaseModel):
    error_code: str  # e.g., "USER_NOT_FOUND", "TASK_NOT_FOUND"
    message: str     # Human-readable error message
    details: Optional[dict] = None  # Additional context
```

**Alternatives Considered**:
- Plain dictionaries: Rejected due to lack of validation
- JSON Schema: Rejected in favor of Pydantic for Python integration

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| MCP SDK | Official MCP Python SDK | Latest | MCP protocol implementation |
| ORM | SQLModel | 0.0.22 | Database operations |
| Database Driver | psycopg2-binary | 2.9.9 | PostgreSQL connectivity |
| Database | Neon Serverless PostgreSQL | N/A | Data persistence |
| Validation | Pydantic | 2.x | Schema validation |
| Testing | pytest | Latest | Unit and integration tests |

## Implementation Recommendations

1. **Stateless Design**: Store zero state in MCP server memory. All state persists in database.
2. **User Isolation**: Always include `user_id` in WHERE clauses for task queries.
3. **Error Handling**: Return structured errors with error codes, never expose stack traces.
4. **Logging**: Log all tool invocations with user_id, tool_name, parameters, and outcome.
5. **Performance**: Use connection pooling and prepared statements for optimal performance.
6. **Security**: Validate and sanitize all input parameters to prevent injection attacks.

## Open Questions

None - all technical decisions resolved.
