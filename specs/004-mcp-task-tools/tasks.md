# Task Breakdown: MCP Server & Task Tools

**Feature**: 004-mcp-task-tools
**Branch**: `004-mcp-task-tools`
**Date**: 2026-02-09
**Status**: Ready for Implementation

## Task Organization

Tasks are organized by implementation phase and user story priority. Each task includes:
- **Task ID**: Unique identifier (T001, T002, etc.)
- **[P]**: Parallel execution marker (can run concurrently with other [P] tasks)
- **[US#]**: User story reference (US1-US5 from spec.md)
- **Description**: Clear, actionable task description with file paths

## Execution Order

1. **Setup Phase**: Initialize project structure and dependencies (T001-T005)
2. **Foundational Phase**: MCP server foundation and tool registration (T006-T015)
3. **User Story Implementation**: Implement tools by priority (T016-T035)
   - US1 (P1): Task Creation - add_task tool (T016-T020)
   - US2 (P1): Task Listing - list_tasks tool (T021-T025)
   - US3 (P2): Task Completion - complete_task tool (T026-T030)
   - US4 (P2): Task Update - update_task tool (T031-T035)
   - US5 (P3): Task Deletion - delete_task tool (T036-T040)
4. **Polish Phase**: Error handling, validation, testing, documentation (T041-T055)

---

## Setup Phase

- [X] [T001] Create mcp/ directory structure at repository root with src/, tests/, and config subdirectories
- [X] [T002] Create requirements.txt in mcp/ with dependencies: mcp>=1.0.0, sqlmodel==0.0.22, psycopg2-binary==2.9.9, pydantic>=2.0.0, python-dotenv>=1.0.0, pytest>=7.0.0
- [X] [T003] Create .env.example in mcp/ with DATABASE_URL, MCP_SERVER_PORT, LOG_LEVEL placeholders
- [X] [T004] Create mcp/README.md with MCP server overview, installation instructions, and quickstart guide
- [X] [T005] Create mcp/src/__init__.py and mcp/tests/__init__.py to mark as Python packages

---

## Foundational Phase

### MCP Server Foundation (Phase 1)

- [X] [T006] Create mcp/src/database.py with database connection pool using SQLModel and Neon PostgreSQL connection string from environment
- [X] [T007] Create mcp/src/models.py that imports Task model from backend/src/models/task.py for reuse
- [X] [T008] Create mcp/src/server.py with MCP server initialization using Official MCP SDK
- [X] [T009] Implement database session management in mcp/src/database.py with connection pooling (pool_size=10) and transaction support
- [X] [T010] Add server lifecycle management (start/stop) in mcp/src/server.py with graceful shutdown and connection cleanup

### Tool Interface Definition (Phase 2)

- [X] [T011] Create mcp/src/schemas.py with Pydantic models for tool input schemas (AddTaskInput, ListTasksInput, CompleteTaskInput, UpdateTaskInput, DeleteTaskInput)
- [X] [T012] Create mcp/src/schemas.py with Pydantic models for tool output schemas (TaskOutput, TaskListOutput, DeleteTaskOutput, ErrorResponse)
- [X] [T013] Create mcp/src/tools/__init__.py with tool registry and registration helper functions
- [X] [T014] Define structured error response format in mcp/src/schemas.py with error_code, message, and details fields
- [X] [T015] Register tool discovery mechanism in mcp/src/server.py to expose available tools to AI agents

---

## User Story Implementation

### US1 (P1): Task Creation via MCP Tool

- [X] [T016] [US1] Create mcp/src/tools/add_task.py with @mcp.tool() decorator and function signature accepting user_id, title, description
- [X] [T017] [US1] Implement database insert logic in add_task tool using SQLModel session and Task model
- [X] [T018] [US1] Add input validation in add_task tool: verify title is 1-200 characters, description ≤1000 characters if provided
- [X] [T019] [US1] Implement user_id validation in add_task tool: verify user exists in users table before creating task
- [X] [T020] [US1] Return structured success response from add_task tool with created task object including id, user_id, title, description, completed, created_at, updated_at

### US2 (P1): Task Listing via MCP Tool

- [X] [T021] [US2] Create mcp/src/tools/list_tasks.py with @mcp.tool() decorator and function signature accepting user_id
- [X] [T022] [US2] Implement user-scoped database query in list_tasks tool: SELECT * FROM tasks WHERE user_id = ? using SQLModel
- [X] [T023] [US2] Add user_id validation in list_tasks tool: verify user exists in users table
- [X] [T024] [US2] Handle empty task list scenario in list_tasks tool: return empty array with count=0 without errors
- [X] [T025] [US2] Return structured success response from list_tasks tool with tasks array and count field

### US3 (P2): Task Completion via MCP Tool

- [X] [T026] [US3] Create mcp/src/tools/complete_task.py with @mcp.tool() decorator and function signature accepting user_id, task_id
- [X] [T027] [US3] Implement task lookup with user validation in complete_task tool: SELECT * FROM tasks WHERE id = ? AND user_id = ?
- [X] [T028] [US3] Implement database update logic in complete_task tool: UPDATE tasks SET completed = true, updated_at = NOW() WHERE id = ? AND user_id = ?
- [X] [T029] [US3] Add authorization check in complete_task tool: return UNAUTHORIZED error if task belongs to different user
- [X] [T030] [US3] Return structured success response from complete_task tool with updated task object showing completed=true

### US4 (P2): Task Update via MCP Tool

- [X] [T031] [US4] Create mcp/src/tools/update_task.py with @mcp.tool() decorator and function signature accepting user_id, task_id, title (optional), description (optional), completed (optional)
- [X] [T032] [US4] Implement task lookup with user validation in update_task tool: SELECT * FROM tasks WHERE id = ? AND user_id = ?
- [X] [T033] [US4] Implement partial update logic in update_task tool: only update provided fields (title, description, completed) and always update updated_at
- [X] [T034] [US4] Add input validation in update_task tool: verify title is 1-200 characters if provided, description ≤1000 characters if provided
- [X] [T035] [US4] Return structured success response from update_task tool with updated task object reflecting all changes

### US5 (P3): Task Deletion via MCP Tool

- [X] [T036] [US5] Create mcp/src/tools/delete_task.py with @mcp.tool() decorator and function signature accepting user_id, task_id
- [X] [T037] [US5] Implement task lookup with user validation in delete_task tool: SELECT * FROM tasks WHERE id = ? AND user_id = ?
- [X] [T038] [US5] Implement database delete logic in delete_task tool: DELETE FROM tasks WHERE id = ? AND user_id = ?
- [X] [T039] [US5] Add authorization check in delete_task tool: return UNAUTHORIZED error if task belongs to different user
- [X] [T040] [US5] Return structured success response from delete_task tool with deleted=true, task_id, and confirmation message

---

## Polish Phase

### Error Handling & Validation (Phase 4)

- [ ] [T041] [P] Implement USER_NOT_FOUND error handling across all tools: check user exists in users table before operations
- [ ] [T042] [P] Implement TASK_NOT_FOUND error handling in complete_task, update_task, delete_task tools: return structured error if task doesn't exist
- [ ] [T043] [P] Implement UNAUTHORIZED error handling in complete_task, update_task, delete_task tools: verify user_id matches task owner
- [ ] [T044] [P] Implement TITLE_REQUIRED error handling in add_task tool: return structured error if title is empty or null
- [ ] [T045] [P] Implement TITLE_TOO_LONG error handling in add_task and update_task tools: return structured error if title exceeds 200 characters
- [ ] [T046] [P] Implement DESCRIPTION_TOO_LONG error handling in add_task and update_task tools: return structured error if description exceeds 1000 characters
- [ ] [T047] [P] Implement DATABASE_ERROR handling across all tools: catch database exceptions and return structured error response
- [ ] [T048] [P] Implement TIMEOUT handling across all tools: enforce 5 second timeout and return structured error if exceeded
- [ ] [T049] [P] Add input sanitization across all tools: prevent SQL injection by using parameterized queries (SQLModel handles this)
- [ ] [T050] [P] Implement transaction management across all tools: wrap database operations in transactions with rollback on error

### Audit Logging & Monitoring

- [ ] [T051] Create mcp/src/logging.py with structured logging configuration using Python logging module
- [ ] [T052] Add audit logging to all tools in mcp/src/tools/*.py: log user_id, tool_name, parameters, outcome (success/error), timestamp
- [ ] [T053] Configure log output to mcp/logs/server.log with rotation and retention policy

### Testing & Validation (Phase 5)

- [ ] [T054] [P] Create mcp/tests/conftest.py with pytest fixtures for database session, test user, and test tasks
- [ ] [T055] [P] Create mcp/tests/test_add_task.py with tests for: successful task creation, missing title error, invalid user error, title too long error
- [ ] [T056] [P] Create mcp/tests/test_list_tasks.py with tests for: successful task listing, empty list scenario, invalid user error
- [ ] [T057] [P] Create mcp/tests/test_complete_task.py with tests for: successful task completion, task not found error, unauthorized access error
- [ ] [T058] [P] Create mcp/tests/test_update_task.py with tests for: successful task update, partial update, task not found error, unauthorized access error
- [ ] [T059] [P] Create mcp/tests/test_delete_task.py with tests for: successful task deletion, task not found error, unauthorized access error
- [ ] [T060] [P] Create mcp/tests/test_database.py with tests for: connection pool initialization, session management, transaction rollback
- [ ] [T061] [P] Create mcp/tests/test_user_isolation.py with tests verifying users cannot access other users' tasks across all tools
- [ ] [T062] [P] Create mcp/tests/test_concurrency.py with tests for 100+ concurrent tool invocations without data corruption

### Statelessness & Compatibility Review (Phase 5)

- [ ] [T063] Verify MCP server holds no in-memory state: review all tool implementations to ensure no class variables or global state
- [ ] [T064] Verify all state persists in database: restart MCP server and confirm all tasks remain accessible
- [ ] [T065] Validate compatibility with Spec-1 Task schema: verify Task model import works and no schema modifications required
- [ ] [T066] Run performance benchmarks: measure tool response times under normal load and verify <2 second target met
- [ ] [T067] Validate user isolation enforcement: run security tests to confirm no cross-user data access possible

### Documentation & Deployment

- [ ] [T068] Update mcp/README.md with complete installation instructions, environment configuration, and usage examples
- [ ] [T069] Create mcp/DEPLOYMENT.md with deployment instructions for production environment
- [ ] [T070] Update specs/004-mcp-task-tools/quickstart.md with verified tool invocation examples and troubleshooting guide
- [ ] [T071] Add health check endpoint to mcp/src/server.py for monitoring server status and database connectivity
- [ ] [T072] Create mcp/docker-compose.yml for containerized deployment (optional, for easier hackathon demo)

---

## Dependency Graph

```
Setup Phase (T001-T005)
    ↓
Foundational Phase (T006-T015)
    ↓
    ├─→ US1 (T016-T020) [P1] ──┐
    ├─→ US2 (T021-T025) [P1] ──┤
    ├─→ US3 (T026-T030) [P2] ──┼─→ Polish Phase (T041-T072)
    ├─→ US4 (T031-T035) [P2] ──┤
    └─→ US5 (T036-T040) [P3] ──┘
```

**Sequential Dependencies**:
- Setup Phase must complete before Foundational Phase
- Foundational Phase must complete before User Story Implementation
- User Story Implementation must complete before Polish Phase

**Parallel Execution**:
- All User Story phases (US1-US5) can run in parallel after Foundational Phase completes
- All error handling tasks (T041-T050) can run in parallel
- All testing tasks (T054-T062) can run in parallel

---

## Parallel Execution Examples

### Example 1: User Story Implementation (After T015 completes)
```bash
# All 5 user stories can be implemented concurrently
Task T016-T020 (US1: add_task)     [Agent 1]
Task T021-T025 (US2: list_tasks)   [Agent 2]
Task T026-T030 (US3: complete_task) [Agent 3]
Task T031-T035 (US4: update_task)  [Agent 4]
Task T036-T040 (US5: delete_task)  [Agent 5]
```

### Example 2: Error Handling (After T040 completes)
```bash
# All error handling tasks can run concurrently
Task T041 (USER_NOT_FOUND)         [Agent 1]
Task T042 (TASK_NOT_FOUND)         [Agent 2]
Task T043 (UNAUTHORIZED)           [Agent 3]
Task T044 (TITLE_REQUIRED)         [Agent 4]
Task T045 (TITLE_TOO_LONG)         [Agent 5]
Task T046 (DESCRIPTION_TOO_LONG)   [Agent 6]
Task T047 (DATABASE_ERROR)         [Agent 7]
Task T048 (TIMEOUT)                [Agent 8]
Task T049 (Input sanitization)     [Agent 9]
Task T050 (Transaction management) [Agent 10]
```

### Example 3: Testing (After T053 completes)
```bash
# All test suites can run concurrently
Task T054 (conftest.py)            [Agent 1]
Task T055 (test_add_task.py)       [Agent 2]
Task T056 (test_list_tasks.py)     [Agent 3]
Task T057 (test_complete_task.py)  [Agent 4]
Task T058 (test_update_task.py)    [Agent 5]
Task T059 (test_delete_task.py)    [Agent 6]
Task T060 (test_database.py)       [Agent 7]
Task T061 (test_user_isolation.py) [Agent 8]
Task T062 (test_concurrency.py)    [Agent 9]
```

---

## Task Summary

- **Total Tasks**: 72
- **Setup Phase**: 5 tasks (T001-T005)
- **Foundational Phase**: 10 tasks (T006-T015)
- **User Story Implementation**: 25 tasks (T016-T040)
  - US1 (P1): 5 tasks
  - US2 (P1): 5 tasks
  - US3 (P2): 5 tasks
  - US4 (P2): 5 tasks
  - US5 (P3): 5 tasks
- **Polish Phase**: 32 tasks (T041-T072)
  - Error Handling: 10 tasks
  - Audit Logging: 3 tasks
  - Testing: 9 tasks
  - Statelessness Review: 5 tasks
  - Documentation: 5 tasks

---

## Success Criteria Mapping

| Success Criterion | Related Tasks |
|-------------------|---------------|
| SC-001: All 5 tools functional | T016-T040 (User Story Implementation) |
| SC-002: 100% user isolation | T019, T023, T027, T029, T032, T037, T039, T061 |
| SC-003: <2 second response time | T066 (Performance benchmarks) |
| SC-004: 100+ concurrent invocations | T062 (Concurrency tests) |
| SC-005: Structured error responses | T041-T048 (Error handling) |
| SC-006: No Task schema modifications | T007, T065 (Task model reuse) |
| SC-007: Hackathon demo ready | T068-T072 (Documentation) |
| SC-008: Zero in-memory state | T063-T064 (Statelessness verification) |

---

## Implementation Notes

1. **Task Model Reuse**: Import Task model from `backend/src/models/task.py` - do not duplicate or modify
2. **Database Connection**: Use existing Neon PostgreSQL connection string from environment variables
3. **MCP SDK**: Follow Official MCP SDK patterns with `@mcp.tool()` decorator for tool registration
4. **User Isolation**: Always include `WHERE user_id = ?` in database queries for task operations
5. **Error Responses**: Use structured format with `success`, `data`, and `error` fields as defined in contracts/mcp-tools.md
6. **Stateless Architecture**: No class variables, no global state, no session storage - all state in database
7. **Transaction Management**: Wrap all database operations in transactions with rollback on error
8. **Audit Logging**: Log every tool invocation with user_id, tool_name, parameters, and outcome
9. **Testing Strategy**: Unit tests with mocked database, integration tests with real database, concurrency tests with 100+ invocations
10. **Performance Target**: All tools must respond within 2 seconds under normal load, 5 seconds maximum timeout

---

## Next Steps

1. Review this task breakdown for completeness and accuracy
2. Run `/sp.implement` to begin implementation following this task plan
3. Execute tasks in order: Setup → Foundational → User Stories → Polish
4. Mark tasks as complete with `[X]` as implementation progresses
5. Run tests after each phase to validate functionality
6. Prepare for hackathon demonstration after all tasks complete
