# Implementation Plan: MCP Server & Task Tools

**Branch**: `004-mcp-task-tools` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-mcp-task-tools/spec.md`

## Summary

Implement a stateless MCP server that exposes five task management operations (add_task, list_tasks, complete_task, update_task, delete_task) as MCP protocol tools. The server will use the Official MCP SDK, connect directly to the existing Neon PostgreSQL database using SQLModel, and enforce user isolation for all operations. All tools are stateless and database-backed, with no in-memory state maintained between invocations.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Official MCP SDK (mcp package), SQLModel 0.0.22, psycopg2-binary 2.9.9
**Storage**: Neon Serverless PostgreSQL (shared with existing backend from Spec-1)
**Testing**: pytest with MCP tool invocation tests
**Target Platform**: Linux server (runs as independent process alongside FastAPI backend)
**Project Type**: Backend service (MCP server)
**Performance Goals**: <2 seconds response time for tool invocations, support 100+ concurrent invocations
**Constraints**: <5 seconds timeout per tool, zero in-memory state, no Task schema modifications
**Scale/Scope**: 5 MCP tools, integrates with existing Task schema (Spec-1), user isolation enforced

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-driven Development
✅ **PASS**: Complete specification exists at `specs/004-mcp-task-tools/spec.md` with all functional requirements, success criteria, and user scenarios defined.

### Agentic Workflow Compliance
✅ **PASS**: Following proper workflow: spec (complete) → plan (in progress) → tasks (next) → implementation.

### Security-first Design
✅ **PASS**: User isolation is mandatory (FR-006). All MCP tools enforce user_id validation and prevent cross-user data access. Audit logging required (FR-009).

### Deterministic Behavior
✅ **PASS**: MCP tools are stateless (FR-003) and return structured, predictable responses (FR-004). No in-memory state maintained (SC-008).

### Full-stack Coherence
✅ **PASS**: MCP server integrates with existing Task schema from Spec-1 without modifications (FR-008). Uses same database and authentication system (Spec-2).

### No Manual Coding Constraint
✅ **PASS**: All code will be generated via Claude Code following this plan and task breakdown.

**Constitution Status**: ✅ ALL GATES PASSED - No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/004-mcp-task-tools/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── mcp-tools.md     # MCP tool schemas and contracts
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
mcp/                     # NEW: MCP server component
├── src/
│   ├── server.py        # MCP server initialization and lifecycle
│   ├── tools/           # MCP tool implementations
│   │   ├── __init__.py
│   │   ├── add_task.py
│   │   ├── list_tasks.py
│   │   ├── complete_task.py
│   │   ├── update_task.py
│   │   └── delete_task.py
│   ├── database.py      # Database connection and session management
│   ├── models.py        # SQLModel models (reuse from backend)
│   └── schemas.py       # Tool input/output schemas
├── tests/
│   ├── test_tools.py    # Tool invocation tests
│   ├── test_database.py # Database integration tests
│   └── conftest.py      # pytest fixtures
├── requirements.txt     # MCP server dependencies
└── README.md            # MCP server documentation

backend/                 # EXISTING: FastAPI backend (Spec-1, Spec-2)
├── src/
│   ├── models/
│   │   └── task.py      # Task model (reused by MCP server)
│   └── ...
└── ...

frontend/                # EXISTING: Next.js frontend (Spec-3)
└── ...
```

**Structure Decision**: Added new `mcp/` directory at repository root to house the MCP server component. This keeps the MCP server separate from the FastAPI backend while allowing it to reuse the Task model definition. The MCP server runs as an independent process and connects directly to the same Neon PostgreSQL database.

## Complexity Tracking

> No constitutional violations - this section is not needed.

## Phase 0: Research & Technical Decisions

### Research Topics

1. **Official MCP SDK Usage**
   - How to initialize and configure an MCP server using the Official MCP SDK
   - Tool registration and lifecycle management
   - Best practices for stateless tool implementation
   - Error handling patterns in MCP tools

2. **Database Connection Strategy**
   - How to share database connection with existing FastAPI backend
   - Connection pooling for MCP server
   - Transaction management for tool invocations
   - Handling database connection failures gracefully

3. **SQLModel Integration**
   - Reusing existing Task model from backend
   - Query patterns for user-scoped operations
   - Concurrent access handling

4. **Tool Schema Design**
   - MCP tool input/output schema format
   - Structured error response format
   - Tool parameter validation patterns

### Research Deliverable

Create `research.md` documenting:
- MCP SDK initialization and tool registration patterns
- Database connection strategy for independent MCP server process
- Tool schema design decisions
- Error handling and validation approach

## Phase 1: Design & Contracts

### Data Model

Create `data-model.md` documenting:

**Entities** (reused from Spec-1):
- **Task**: id (int), user_id (int), title (str), description (str), completed (bool), created_at (datetime), updated_at (datetime)

**MCP-Specific Concepts**:
- **Tool Request**: user_id, tool_name, parameters, timestamp
- **Tool Response**: success (bool), data (dict), error (dict)

**Relationships**:
- MCP tools operate on Task entities
- Each tool invocation is scoped to a single user_id
- No new database tables required

### API Contracts

Create `contracts/mcp-tools.md` documenting:

**Tool: add_task**
- Input: user_id (int), title (str), description (str, optional)
- Output: task_id (int), title (str), description (str), completed (bool), created_at (str)
- Errors: USER_NOT_FOUND, TITLE_REQUIRED, TITLE_TOO_LONG

**Tool: list_tasks**
- Input: user_id (int)
- Output: tasks (list of task objects)
- Errors: USER_NOT_FOUND

**Tool: complete_task**
- Input: user_id (int), task_id (int)
- Output: task object with completed=true
- Errors: USER_NOT_FOUND, TASK_NOT_FOUND, UNAUTHORIZED

**Tool: update_task**
- Input: user_id (int), task_id (int), title (str, optional), description (str, optional), completed (bool, optional)
- Output: updated task object
- Errors: USER_NOT_FOUND, TASK_NOT_FOUND, UNAUTHORIZED

**Tool: delete_task**
- Input: user_id (int), task_id (int)
- Output: success (bool), message (str)
- Errors: USER_NOT_FOUND, TASK_NOT_FOUND, UNAUTHORIZED

### Quickstart Guide

Create `quickstart.md` with:
- How to start the MCP server
- How to invoke MCP tools (example commands)
- How to verify tool functionality
- Integration with AI agents (Spec-5 preview)

### Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to add:
- MCP SDK to technology context
- MCP server component to project structure
- Tool-based architecture pattern

## Phase 2: Implementation Phases (User-Provided)

### Phase 1 — MCP Server Foundation

**Objective**: Initialize MCP server using Official MCP SDK and establish database connectivity.

**Tasks**:
- Install Official MCP SDK and dependencies
- Create MCP server initialization script (mcp/src/server.py)
- Configure database connection using existing Neon credentials
- Implement database session management
- Verify MCP server starts successfully
- Verify database connectivity from MCP server

**Exit Conditions**:
- MCP server starts without errors
- Database connection pool established
- No in-memory state stored in server
- Server can be stopped and restarted cleanly

### Phase 2 — Tool Interface Definition

**Objective**: Define MCP tool schemas and register tools with the MCP server.

**Tasks**:
- Define tool schemas for all 5 tools (add_task, list_tasks, complete_task, update_task, delete_task)
- Specify required and optional parameters for each tool
- Define structured return payload format
- Define structured error response format
- Register all tools with MCP server
- Implement tool discovery endpoint (if applicable)

**Exit Conditions**:
- All 5 tools registered with MCP server
- Tool interfaces match specification exactly
- Tool schemas are reviewable and deterministic
- Tools can be discovered by AI agents

### Phase 3 — Tool Implementation (Database-Backed)

**Objective**: Implement all 5 MCP tools with database operations and user isolation.

**Tasks**:
- Implement add_task tool with database insert
- Implement list_tasks tool with user-scoped query
- Implement complete_task tool with database update
- Implement delete_task tool with database delete
- Implement update_task tool with database update
- Enforce user_id scoping in all database queries
- Implement transaction management for each tool
- Add audit logging for all tool invocations

**Exit Conditions**:
- All tools perform correct database operations
- Tasks persist correctly in Neon PostgreSQL
- No cross-user data access possible
- All operations are atomic (transaction-wrapped)
- Audit logs capture user_id, tool_name, and outcome

### Phase 4 — Error Handling & Validation

**Objective**: Implement comprehensive input validation and error handling.

**Tasks**:
- Validate tool input parameters (required fields, types, lengths)
- Handle task not found scenarios
- Handle invalid user_id or task_id
- Handle database connection errors
- Handle concurrent modification conflicts
- Return structured error responses with error codes
- Implement timeout handling (5 second limit)
- Sanitize input to prevent injection attacks

**Exit Conditions**:
- MCP tools fail gracefully with structured errors
- Errors are predictable and non-leaky (no stack traces exposed)
- No unhandled exceptions
- All error scenarios from spec are covered
- Input validation prevents malformed data

### Phase 5 — Statelessness & Compatibility Review

**Objective**: Verify stateless operation and compatibility with existing system.

**Tasks**:
- Verify MCP tools hold no server-side state
- Confirm all state is persisted in database
- Validate compatibility with Spec-1 Task schema
- Test concurrent tool invocations
- Verify performance meets <2 second target
- Validate user isolation enforcement
- Prepare for AI agent integration (Spec-5)
- Document MCP server deployment and operation

**Exit Conditions**:
- MCP server is fully stateless (can restart without data loss)
- All Spec-4 success criteria satisfied (SC-001 through SC-008)
- MCP tools ready for AI agent integration
- Performance benchmarks met
- Documentation complete

## Dependencies & Integration Points

### External Dependencies
- Official MCP SDK for Python (new dependency)
- SQLModel 0.0.22 (existing, reused)
- psycopg2-binary 2.9.9 (existing, reused)
- Neon Serverless PostgreSQL (existing, shared)

### Internal Dependencies
- **Spec-1 (Backend Task CRUD)**: Reuse Task model and database schema
- **Spec-2 (Better Auth JWT)**: Rely on existing user authentication for user_id validation
- **Spec-3 (Frontend)**: No direct dependency, but MCP tools will be consumed by AI agents in future

### Integration Points
- Database: MCP server connects to same Neon PostgreSQL database as FastAPI backend
- Task Model: MCP server imports Task model from backend/src/models/task.py
- User Validation: MCP tools validate user_id exists in users table (from Spec-2)

## Risk Assessment

### Technical Risks

1. **MCP SDK Learning Curve**
   - Mitigation: Phase 0 research will document SDK usage patterns
   - Fallback: Consult MCP SDK documentation and examples

2. **Database Connection Conflicts**
   - Mitigation: Use separate connection pool for MCP server
   - Fallback: Implement connection retry logic and timeouts

3. **Concurrent Access Issues**
   - Mitigation: Use database transactions and proper locking
   - Fallback: Implement optimistic locking with version fields

4. **Performance Under Load**
   - Mitigation: Connection pooling and query optimization
   - Fallback: Add caching layer if needed (violates stateless principle, avoid if possible)

### Operational Risks

1. **MCP Server Deployment**
   - Mitigation: Document deployment process in quickstart.md
   - Fallback: Provide Docker container for easy deployment

2. **Monitoring and Debugging**
   - Mitigation: Comprehensive audit logging (FR-009)
   - Fallback: Add structured logging with log levels

## Success Validation

### Acceptance Criteria (from Spec)

- ✅ SC-001: All five MCP tools functional and accessible via MCP protocol
- ✅ SC-002: 100% user isolation enforcement
- ✅ SC-003: <2 second response time
- ✅ SC-004: 100+ concurrent invocations supported
- ✅ SC-005: Structured error responses
- ✅ SC-006: No Task schema modifications required
- ✅ SC-007: Hackathon reviewers can invoke tools and observe database changes
- ✅ SC-008: Zero in-memory state maintained

### Testing Strategy

1. **Unit Tests**: Test each tool in isolation with mocked database
2. **Integration Tests**: Test tools with real database connection
3. **Concurrency Tests**: Test 100+ simultaneous tool invocations
4. **Performance Tests**: Measure response times under load
5. **Security Tests**: Verify user isolation and input validation
6. **Statelessness Tests**: Restart server and verify no data loss

## Next Steps

1. ✅ Complete this plan (Phase 0-1 of /sp.plan)
2. ⬜ Run `/sp.tasks` to generate task breakdown
3. ⬜ Run `/sp.implement` to execute implementation
4. ⬜ Test MCP tools with sample invocations
5. ⬜ Prepare for AI agent integration (Spec-5)
