# Tasks: AI Chat Agent & Conversation System

**Input**: Design documents from `/specs/005-ai-chat-agent/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chat-api.md, quickstart.md

**Tests**: Tests are not explicitly requested in the specification, so this task list focuses on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- Backend: `backend/src/` (Python FastAPI)
- Frontend: `frontend/src/` (Next.js - future integration)
- MCP Server: `mcp/src/` (existing from Spec-4)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for chat functionality

- [ ] T001 Install OpenAI Python SDK in backend/requirements.txt
- [ ] T002 Install Official MCP SDK client library in backend/requirements.txt
- [ ] T003 [P] Create backend/src/models/conversation.py file structure
- [ ] T004 [P] Create backend/src/models/message.py file structure
- [ ] T005 [P] Create backend/src/services/chat_service.py file structure
- [ ] T006 [P] Create backend/src/services/mcp_client.py file structure
- [ ] T007 [P] Create backend/src/api/chat.py file structure
- [ ] T008 Configure OpenAI API key in backend/.env.example
- [ ] T009 Configure MCP server URL in backend/.env.example

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 Create Conversation SQLModel in backend/src/models/conversation.py with fields: id, user_id, created_at, updated_at
- [ ] T011 Create Message SQLModel in backend/src/models/message.py with fields: id, conversation_id, user_id, role, content, created_at
- [ ] T012 Create Alembic migration for conversations table in alembic/versions/
- [ ] T013 Create Alembic migration for messages table in alembic/versions/
- [ ] T014 Add indexes for conversations.user_id in migration
- [ ] T015 Add indexes for messages.conversation_id and messages.created_at in migration
- [ ] T016 Run migrations against Neon PostgreSQL database
- [ ] T017 Implement MCPClient class in backend/src/services/mcp_client.py with __init__ method
- [ ] T018 [P] Implement MCPClient.add_task method in backend/src/services/mcp_client.py
- [ ] T019 [P] Implement MCPClient.list_tasks method in backend/src/services/mcp_client.py
- [ ] T020 [P] Implement MCPClient.complete_task method in backend/src/services/mcp_client.py
- [ ] T021 [P] Implement MCPClient.update_task method in backend/src/services/mcp_client.py
- [ ] T022 [P] Implement MCPClient.delete_task method in backend/src/services/mcp_client.py
- [ ] T023 Add error handling and retry logic to MCPClient in backend/src/services/mcp_client.py
- [ ] T024 Initialize OpenAI client in backend/src/services/chat_service.py
- [ ] T025 Define tool schemas for all 5 MCP tools in backend/src/services/chat_service.py
- [ ] T026 Register tools with OpenAI agent in backend/src/services/chat_service.py
- [ ] T027 Implement conversation history formatting for OpenAI API in backend/src/services/chat_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 & 2 - Natural Language Task Creation + Conversation Persistence (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks via natural language and persist all conversation history to database with full context restoration

**Independent Test**: Send "Create a task to buy groceries" → verify task created via MCP tool → send follow-up "Make it high priority" → verify agent understands context from previous message → restart server → send new message → verify full conversation history restored

**Why Combined**: These two stories are interdependent - you cannot have natural language task creation without conversation persistence, and persistence is meaningless without the chat functionality. Both are P1 and form the core MVP.

### Implementation for User Stories 1 & 2

- [ ] T028 [US1+2] Implement get_or_create_conversation method in backend/src/services/chat_service.py
- [ ] T029 [US1+2] Implement load_conversation_history method in backend/src/services/chat_service.py
- [ ] T030 [US1+2] Implement save_message method in backend/src/services/chat_service.py
- [ ] T031 [US1+2] Implement process_message method with OpenAI agent invocation in backend/src/services/chat_service.py
- [ ] T032 [US1+2] Add tool invocation orchestration in process_message method in backend/src/services/chat_service.py
- [ ] T033 [US1+2] Implement tool result handling and response generation in backend/src/services/chat_service.py
- [ ] T034 [US1+2] Add error handling for OpenAI API failures in backend/src/services/chat_service.py
- [ ] T035 [US1+2] Add error handling for MCP tool failures in backend/src/services/chat_service.py
- [ ] T036 [US1+2] Create ChatRequest Pydantic schema in backend/src/api/chat.py
- [ ] T037 [US1+2] Create ChatResponse Pydantic schema in backend/src/api/chat.py
- [ ] T038 [US1+2] Create ErrorResponse Pydantic schema in backend/src/api/chat.py
- [ ] T039 [US1+2] Implement POST /api/{user_id}/chat endpoint in backend/src/api/chat.py
- [ ] T040 [US1+2] Add JWT token validation to chat endpoint in backend/src/api/chat.py
- [ ] T041 [US1+2] Add user_id validation (JWT matches path parameter) in backend/src/api/chat.py
- [ ] T042 [US1+2] Add request body validation in backend/src/api/chat.py
- [ ] T043 [US1+2] Invoke ChatService.process_message from endpoint in backend/src/api/chat.py
- [ ] T044 [US1+2] Add response serialization in backend/src/api/chat.py
- [ ] T045 [US1+2] Add error handling with proper HTTP status codes in backend/src/api/chat.py
- [ ] T046 [US1+2] Add conversation_id validation (belongs to user) in backend/src/api/chat.py
- [ ] T047 [US1+2] Update conversation.updated_at timestamp on new messages in backend/src/services/chat_service.py
- [ ] T048 [US1+2] Add message content sanitization to prevent XSS in backend/src/services/chat_service.py
- [ ] T049 [US1+2] Add conversation history size limit (50 messages) in backend/src/services/chat_service.py
- [ ] T050 [US1+2] Add request timeout handling (5 seconds) in backend/src/api/chat.py

**Checkpoint**: At this point, users can create tasks via natural language, all messages are persisted, conversation history is restored on each request, and conversations resume correctly after server restart. This is the complete MVP.

---

## Phase 4: User Story 3 - Natural Language Task Listing (Priority: P2)

**Goal**: Enable users to view their tasks by asking the AI agent in natural language

**Independent Test**: Send "What are my tasks?" → verify agent invokes list_tasks MCP tool → verify agent presents tasks in conversational format → verify empty task list handled gracefully

### Implementation for User Story 3

- [ ] T051 [US3] Add list_tasks tool invocation logic to OpenAI agent in backend/src/services/chat_service.py
- [ ] T052 [US3] Implement task list formatting for conversational response in backend/src/services/chat_service.py
- [ ] T053 [US3] Add empty task list handling with helpful prompt in backend/src/services/chat_service.py
- [ ] T054 [US3] Add error handling for list_tasks MCP tool failures in backend/src/services/chat_service.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can create tasks and view their task list conversationally.

---

## Phase 5: User Story 4 - Natural Language Task Completion (Priority: P2)

**Goal**: Enable users to mark tasks as completed by telling the AI agent in natural language

**Independent Test**: Create task "Buy groceries" → send "I finished buying groceries" → verify agent invokes complete_task with correct task_id → verify task marked complete in database → verify confirmation message

### Implementation for User Story 4

- [ ] T055 [US4] Add complete_task tool invocation logic to OpenAI agent in backend/src/services/chat_service.py
- [ ] T056 [US4] Implement task identification from natural language in backend/src/services/chat_service.py
- [ ] T057 [US4] Add ambiguous task reference handling (ask for clarification) in backend/src/services/chat_service.py
- [ ] T058 [US4] Add non-existent task error handling in backend/src/services/chat_service.py
- [ ] T059 [US4] Add completion confirmation message generation in backend/src/services/chat_service.py

**Checkpoint**: At this point, User Stories 1-4 should all work independently. Users can create, view, and complete tasks conversationally.

---

## Phase 6: User Story 5 - Natural Language Task Updates (Priority: P3)

**Goal**: Enable users to modify task details (title, description) by instructing the AI agent in natural language

**Independent Test**: Create task "Buy groceries" → send "Change the groceries task to 'Buy groceries and cook dinner'" → verify agent invokes update_task with new title → verify task updated in database → verify confirmation message

### Implementation for User Story 5

- [ ] T060 [US5] Add update_task tool invocation logic to OpenAI agent in backend/src/services/chat_service.py
- [ ] T061 [US5] Implement task field update detection from natural language in backend/src/services/chat_service.py
- [ ] T062 [US5] Add partial update support (title only, description only, or both) in backend/src/services/chat_service.py
- [ ] T063 [US5] Add ambiguous update reference handling in backend/src/services/chat_service.py
- [ ] T064 [US5] Add update confirmation message generation in backend/src/services/chat_service.py

**Checkpoint**: At this point, User Stories 1-5 should all work independently. Users can create, view, complete, and update tasks conversationally.

---

## Phase 7: User Story 6 - Natural Language Task Deletion (Priority: P3)

**Goal**: Enable users to permanently remove tasks by instructing the AI agent

**Independent Test**: Create task "Buy groceries" → send "Delete the groceries task" → verify agent invokes delete_task → verify task removed from database → verify confirmation message

### Implementation for User Story 6

- [ ] T065 [US6] Add delete_task tool invocation logic to OpenAI agent in backend/src/services/chat_service.py
- [ ] T066 [US6] Implement task identification for deletion from natural language in backend/src/services/chat_service.py
- [ ] T067 [US6] Add deletion confirmation request (for safety) in backend/src/services/chat_service.py
- [ ] T068 [US6] Add non-existent task deletion error handling in backend/src/services/chat_service.py
- [ ] T069 [US6] Add deletion confirmation message generation in backend/src/services/chat_service.py

**Checkpoint**: All user stories should now be independently functional. Full task management workflow available via natural language.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T070 [P] Add structured logging for all chat operations in backend/src/services/chat_service.py
- [ ] T071 [P] Add rate limiting per user (60 requests/minute) in backend/src/api/chat.py
- [ ] T072 [P] Add global rate limiting (1000 requests/minute) in backend/src/api/chat.py
- [ ] T073 [P] Add performance monitoring and metrics in backend/src/api/chat.py
- [ ] T074 [P] Add conversation history pagination support in backend/src/services/chat_service.py
- [ ] T075 [P] Optimize database queries with connection pooling in backend/src/database.py
- [ ] T076 [P] Add API documentation with OpenAPI schema in backend/src/api/chat.py
- [ ] T077 [P] Create README.md for chat service in backend/
- [ ] T078 [P] Add deployment guide in backend/DEPLOYMENT.md
- [ ] T079 Validate all quickstart.md examples work correctly
- [ ] T080 Security audit: verify JWT validation, user isolation, input sanitization
- [ ] T081 Performance test: verify response times meet targets (p95 < 3s)
- [ ] T082 End-to-end test: complete task management workflow via natural language

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories 1+2 (Phase 3)**: Depends on Foundational phase completion - MVP core
- **User Story 3 (Phase 4)**: Depends on Foundational phase completion - Can run in parallel with US1+2 if staffed
- **User Story 4 (Phase 5)**: Depends on Foundational phase completion - Can run in parallel with other stories if staffed
- **User Story 5 (Phase 6)**: Depends on Foundational phase completion - Can run in parallel with other stories if staffed
- **User Story 6 (Phase 7)**: Depends on Foundational phase completion - Can run in parallel with other stories if staffed
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Stories 1+2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories - CORE MVP
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 4 (P2)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories

### Within Each User Story

- Models before services
- Services before endpoints
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005, T006, T007 can run in parallel (different files)
- **Phase 2 (Foundational)**: T018-T022 (MCP client methods) can run in parallel (different methods)
- **Phase 3 (US1+2)**: T036, T037, T038 (Pydantic schemas) can run in parallel (different schemas)
- **Phase 8 (Polish)**: T070-T078 can run in parallel (different concerns)
- **User Stories**: After Foundational phase completes, US3, US4, US5, US6 can all be worked on in parallel by different team members

---

## Parallel Example: Foundational Phase

```bash
# Launch all MCP client methods together:
Task: "Implement MCPClient.add_task method in backend/src/services/mcp_client.py"
Task: "Implement MCPClient.list_tasks method in backend/src/services/mcp_client.py"
Task: "Implement MCPClient.complete_task method in backend/src/services/mcp_client.py"
Task: "Implement MCPClient.update_task method in backend/src/services/mcp_client.py"
Task: "Implement MCPClient.delete_task method in backend/src/services/mcp_client.py"
```

## Parallel Example: User Stories 1+2

```bash
# Launch all Pydantic schemas together:
Task: "Create ChatRequest Pydantic schema in backend/src/api/chat.py"
Task: "Create ChatResponse Pydantic schema in backend/src/api/chat.py"
Task: "Create ErrorResponse Pydantic schema in backend/src/api/chat.py"
```

## Parallel Example: After Foundational Complete

```bash
# Different team members can work on different user stories:
Developer A: Phase 3 (User Stories 1+2 - MVP core)
Developer B: Phase 4 (User Story 3 - Task listing)
Developer C: Phase 5 (User Story 4 - Task completion)
Developer D: Phase 6 (User Story 5 - Task updates)
```

---

## Implementation Strategy

### MVP First (User Stories 1+2 Only)

1. Complete Phase 1: Setup (9 tasks)
2. Complete Phase 2: Foundational (18 tasks) - CRITICAL - blocks all stories
3. Complete Phase 3: User Stories 1+2 (23 tasks)
4. **STOP and VALIDATE**: Test natural language task creation and conversation persistence independently
5. Deploy/demo if ready - this is a complete, usable chat agent

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready (27 tasks)
2. Add User Stories 1+2 → Test independently → Deploy/Demo (MVP! - 50 tasks total)
3. Add User Story 3 → Test independently → Deploy/Demo (54 tasks total)
4. Add User Story 4 → Test independently → Deploy/Demo (59 tasks total)
5. Add User Story 5 → Test independently → Deploy/Demo (64 tasks total)
6. Add User Story 6 → Test independently → Deploy/Demo (69 tasks total)
7. Add Polish → Final production-ready version (82 tasks total)
8. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (27 tasks)
2. Once Foundational is done:
   - Developer A: User Stories 1+2 (MVP core - 23 tasks)
   - Developer B: User Story 3 (4 tasks)
   - Developer C: User Story 4 (5 tasks)
   - Developer D: User Story 5 (5 tasks)
   - Developer E: User Story 6 (5 tasks)
3. Stories complete and integrate independently
4. Team completes Polish together (13 tasks)

---

## Task Summary

**Total Tasks**: 82

**Tasks by Phase**:
- Phase 1 (Setup): 9 tasks
- Phase 2 (Foundational): 18 tasks
- Phase 3 (User Stories 1+2 - P1): 23 tasks
- Phase 4 (User Story 3 - P2): 4 tasks
- Phase 5 (User Story 4 - P2): 5 tasks
- Phase 6 (User Story 5 - P3): 5 tasks
- Phase 7 (User Story 6 - P3): 5 tasks
- Phase 8 (Polish): 13 tasks

**MVP Scope** (Recommended): Phases 1-3 = 50 tasks
- Delivers core chat functionality with natural language task creation
- Full conversation persistence and history restoration
- Demonstrates AI agent correctness and MCP tool integration
- Showcases stateless architecture principles

**Parallel Opportunities**: 20 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**: Each user story phase includes clear test criteria for independent validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Stories 1+2 are combined as they're interdependent and both P1
- User Stories 3-6 are independent and can be implemented in any order after Foundational phase
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
