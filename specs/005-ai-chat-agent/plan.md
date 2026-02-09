# Implementation Plan: AI Chat Agent & Conversation System

**Branch**: `005-ai-chat-agent` | **Date**: 2026-02-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-ai-chat-agent/spec.md`

## Summary

Implement a stateless chat endpoint that enables natural language todo management through an AI agent. The agent uses OpenAI Agents SDK to process user messages, invokes MCP tools exclusively for all task operations, and maintains conversation context by persisting and restoring message history from the database. The system demonstrates correct AI agent architecture with no direct database access from the agent and full conversation memory reconstruction per request.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: OpenAI Agents SDK, Official MCP SDK (client), FastAPI, SQLModel 0.0.22, psycopg2-binary 2.9.9
**Storage**: Neon Serverless PostgreSQL (shared with existing backend from Spec-1)
**Testing**: pytest with AI agent integration tests
**Target Platform**: Linux server (runs as FastAPI endpoint alongside existing backend)
**Project Type**: Backend service (chat endpoint)
**Performance Goals**: <3 seconds response time for chat requests, <5 seconds maximum timeout
**Constraints**: Stateless endpoint (zero in-memory conversation state), AI agent must NOT access database directly, all task operations via MCP tools only
**Scale/Scope**: Chat endpoint with 2 database models (Conversation, Message), OpenAI Agents SDK integration, MCP client for 5 tools

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-driven Development
✅ **PASS**: Complete specification exists at `specs/005-ai-chat-agent/spec.md` with all functional requirements, success criteria, and user scenarios defined.

### Agentic Workflow Compliance
✅ **PASS**: Following proper workflow: spec (complete) → plan (in progress) → tasks (next) → implementation.

### Security-first Design
✅ **PASS**: JWT token validation mandatory (FR-007). User isolation enforced by passing user_id to all MCP tool invocations (FR-008). Conversation access restricted to owner.

### Deterministic Behavior
✅ **PASS**: Stateless endpoint design (FR-001, SC-005) ensures consistent behavior. Conversation history reconstruction from database provides deterministic context restoration (FR-002, SC-004).

### Full-stack Coherence
✅ **PASS**: Chat endpoint integrates with existing authentication (Spec-2), MCP tools (Spec-4), and Task schema (Spec-1). Uses same database and authentication system.

### No Manual Coding Constraint
✅ **PASS**: All code will be generated via Claude Code following this plan and task breakdown.

**Constitution Status**: ✅ ALL GATES PASSED - No violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/005-ai-chat-agent/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file (in progress)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── chat-api.md      # Chat endpoint contract
├── checklists/          # Quality validation
│   └── requirements.md  # Spec quality checklist (complete)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/                 # EXISTING: FastAPI backend (Spec-1, Spec-2)
├── src/
│   ├── models/
│   │   ├── task.py      # Task model (existing, used by MCP tools)
│   │   ├── conversation.py  # NEW: Conversation model
│   │   └── message.py   # NEW: Message model
│   ├── services/
│   │   └── chat_service.py  # NEW: Chat service with AI agent integration
│   ├── api/
│   │   └── chat.py      # NEW: Chat endpoint (POST /api/{user_id}/chat)
│   └── ...
└── tests/
    ├── test_chat_endpoint.py  # NEW: Chat endpoint tests
    ├── test_chat_service.py   # NEW: Chat service tests
    └── test_conversation_persistence.py  # NEW: Conversation persistence tests

mcp/                     # EXISTING: MCP server (Spec-4)
├── src/
│   ├── tools/           # 5 MCP tools (add_task, list_tasks, etc.)
│   └── ...
└── ...

frontend/                # EXISTING: Next.js frontend (Spec-3)
└── ...
```

**Structure Decision**: Added new chat functionality to existing FastAPI backend. This keeps the chat endpoint co-located with authentication and allows direct integration with Better Auth JWT validation. The AI agent will invoke MCP tools via MCP client (not direct function calls), maintaining proper separation of concerns.

## Complexity Tracking

> No constitutional violations - this section is not needed.

## Phase 0: Research & Technical Decisions

### Research Topics

1. **OpenAI Agents SDK Usage**
   - How to initialize and configure an AI agent with OpenAI Agents SDK
   - Tool registration and invocation patterns
   - Conversation history management
   - Error handling and retry strategies

2. **MCP Client Integration**
   - How to invoke MCP tools from Python backend (MCP client library)
   - Tool discovery and schema validation
   - Error handling for MCP tool failures
   - Network communication patterns with MCP server

3. **Conversation Persistence Strategy**
   - Database schema for Conversation and Message entities
   - Efficient conversation history loading
   - Message ordering and pagination
   - Conversation lifecycle management

4. **Stateless Endpoint Design**
   - Request/response flow for stateless chat
   - Conversation history reconstruction per request
   - Performance optimization for history loading
   - Caching strategies (if needed)

### Research Deliverable

Create `research.md` documenting:
- OpenAI Agents SDK initialization and tool configuration patterns
- MCP client library usage for tool invocation
- Conversation persistence schema and query patterns
- Stateless endpoint architecture with history reconstruction
- Error handling strategies for AI agent and MCP tool failures

## Phase 1: Design & Contracts

### Data Model

Create `data-model.md` documenting:

**Entities**:
- **Conversation**: id (int), user_id (str), created_at (datetime), updated_at (datetime)
- **Message**: id (int), conversation_id (int), user_id (str), role (str: user/assistant), content (str), created_at (datetime)

**Relationships**:
- One user has many conversations (1:N)
- One conversation has many messages (1:N)
- Messages are ordered chronologically within a conversation

**Indexes**:
- Conversation: user_id (for user-scoped queries)
- Message: conversation_id (for history loading), created_at (for ordering)

### API Contracts

Create `contracts/chat-api.md` documenting:

**Endpoint: POST /api/{user_id}/chat**

**Request**:
```json
{
  "message": "Create a task to buy groceries",
  "conversation_id": 123  // optional, creates new if not provided
}
```

**Response (Success)**:
```json
{
  "conversation_id": 123,
  "message": {
    "role": "assistant",
    "content": "I've created a task: 'Buy groceries'",
    "created_at": "2026-02-09T10:30:00Z"
  }
}
```

**Response (Error)**:
```json
{
  "error": {
    "code": "MCP_TOOL_ERROR",
    "message": "Failed to create task",
    "details": {...}
  }
}
```

**Error Codes**:
- UNAUTHORIZED: Invalid or missing JWT token
- MCP_TOOL_ERROR: MCP tool invocation failed
- OPENAI_API_ERROR: OpenAI API request failed
- CONVERSATION_NOT_FOUND: Invalid conversation_id
- INVALID_INPUT: Malformed request

### Quickstart Guide

Create `quickstart.md` with:
- How to send chat messages to the endpoint
- How to create and continue conversations
- Example natural language commands for task management
- How to handle errors and ambiguous requests
- Integration with frontend chat UI (Spec-3 preview)

### Agent Context Update

Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude` to add:
- OpenAI Agents SDK to technology context
- MCP client library to technology context
- Chat endpoint to project structure
- Conversation persistence pattern

## Phase 2: Implementation Phases

### Phase 1 — Database Models & Migrations

**Objective**: Create Conversation and Message models with database migrations.

**Tasks**:
- Create Conversation SQLModel with user_id, created_at, updated_at
- Create Message SQLModel with conversation_id, user_id, role, content, created_at
- Create database migration for conversations table
- Create database migration for messages table
- Add indexes for user_id (conversations) and conversation_id (messages)
- Verify migrations apply successfully to Neon PostgreSQL

**Exit Conditions**:
- Conversation and Message tables exist in database
- Indexes are created for efficient queries
- Models can be imported and used in backend code
- No schema conflicts with existing tables

### Phase 2 — MCP Client Integration

**Objective**: Implement MCP client for invoking MCP tools from backend.

**Tasks**:
- Install MCP client library for Python
- Create MCP client wrapper service
- Implement tool invocation methods for all 5 MCP tools
- Add error handling for MCP tool failures
- Add retry logic for transient failures
- Test MCP client can successfully invoke tools

**Exit Conditions**:
- MCP client can invoke all 5 tools (add_task, list_tasks, complete_task, update_task, delete_task)
- Tool responses are properly parsed and returned
- Errors are caught and converted to structured responses
- MCP server connectivity is verified

### Phase 3 — OpenAI Agents SDK Integration

**Objective**: Configure OpenAI Agents SDK with MCP tool definitions.

**Tasks**:
- Install OpenAI Agents SDK
- Configure OpenAI API key from environment
- Define tool schemas for all 5 MCP tools
- Register tools with OpenAI agent
- Implement conversation history formatting for OpenAI API
- Test agent can understand natural language and select correct tools

**Exit Conditions**:
- OpenAI agent is initialized with all 5 tool definitions
- Agent can process natural language messages
- Agent correctly selects tools based on user intent
- Tool invocation results are returned to agent
- Agent generates natural language responses

### Phase 4 — Chat Service Implementation

**Objective**: Implement chat service with conversation persistence and AI agent orchestration.

**Tasks**:
- Create ChatService class with conversation management
- Implement get_or_create_conversation method
- Implement load_conversation_history method
- Implement save_message method (user and assistant)
- Implement process_message method with AI agent invocation
- Add error handling for OpenAI API failures
- Add error handling for MCP tool failures
- Implement conversation context reconstruction

**Exit Conditions**:
- ChatService can create and retrieve conversations
- Conversation history is loaded from database
- User messages are persisted before AI processing
- Assistant responses are persisted after AI processing
- AI agent has access to full conversation history
- Errors are handled gracefully with user-friendly messages

### Phase 5 — Chat Endpoint Implementation

**Objective**: Create FastAPI endpoint for chat with JWT authentication.

**Tasks**:
- Create POST /api/{user_id}/chat endpoint
- Add JWT token validation middleware
- Validate user_id matches JWT token
- Parse request body (message, conversation_id)
- Invoke ChatService.process_message
- Return structured response with conversation_id and assistant message
- Add request/response validation with Pydantic
- Add error handling with proper HTTP status codes

**Exit Conditions**:
- Chat endpoint is accessible at POST /api/{user_id}/chat
- JWT tokens are validated on every request
- User isolation is enforced (user_id from JWT)
- Requests are processed within 5 seconds
- Responses include conversation_id and assistant message
- Errors return appropriate HTTP status codes

### Phase 6 — Testing & Validation

**Objective**: Comprehensive testing of chat functionality.

**Tasks**:
- Create unit tests for Conversation and Message models
- Create unit tests for MCP client wrapper
- Create unit tests for ChatService
- Create integration tests for chat endpoint
- Create tests for conversation persistence and restoration
- Create tests for AI agent tool selection
- Create tests for error handling (MCP failures, OpenAI failures)
- Create tests for user isolation
- Create tests for conversation resumption after server restart

**Exit Conditions**:
- All unit tests pass
- All integration tests pass
- Conversation persistence works correctly
- AI agent selects correct tools for natural language commands
- Errors are handled gracefully
- User isolation is enforced
- Conversations can be resumed after restart

## Dependencies & Integration Points

### External Dependencies
- OpenAI Agents SDK for AI processing (new dependency)
- OpenAI API for language model access (new dependency)
- MCP client library for tool invocation (new dependency)
- FastAPI (existing, reused)
- SQLModel 0.0.22 (existing, reused)
- psycopg2-binary 2.9.9 (existing, reused)
- Neon Serverless PostgreSQL (existing, shared)

### Internal Dependencies
- **Spec-1 (Backend Task CRUD)**: MCP tools operate on Task schema
- **Spec-2 (Better Auth JWT)**: Chat endpoint validates JWT tokens
- **Spec-4 (MCP Server & Task Tools)**: Chat agent invokes all 5 MCP tools

### Integration Points
- Database: Chat endpoint connects to same Neon PostgreSQL database as existing backend
- Authentication: Chat endpoint uses Better Auth JWT validation from Spec-2
- MCP Tools: Chat agent invokes MCP tools via MCP client (network calls to MCP server)
- Task Operations: All task CRUD operations go through MCP tools (no direct database access)

## Risk Assessment

### Technical Risks

1. **OpenAI API Latency**
   - Mitigation: Set reasonable timeout (5 seconds), implement retry logic
   - Fallback: Return error message to user, suggest retry

2. **MCP Tool Invocation Failures**
   - Mitigation: Implement error handling, retry transient failures
   - Fallback: Communicate failure to user in natural language

3. **Conversation History Size**
   - Mitigation: Limit history to recent N messages (e.g., last 50)
   - Fallback: Implement pagination or summarization if needed

4. **AI Agent Tool Selection Accuracy**
   - Mitigation: Clear tool descriptions, test with common phrasings
   - Fallback: Agent asks clarifying questions when uncertain

### Operational Risks

1. **OpenAI API Costs**
   - Mitigation: Monitor usage, implement rate limiting if needed
   - Fallback: Set budget alerts, optimize prompt length

2. **Stateless Performance**
   - Mitigation: Optimize conversation history queries, add indexes
   - Fallback: Implement caching layer if database queries become bottleneck

## Success Validation

### Acceptance Criteria (from Spec)

- ✅ SC-001: 90%+ accuracy for natural language task creation
- ✅ SC-002: 95%+ correct MCP tool invocation
- ✅ SC-003: <3 second response time
- ✅ SC-004: 100% conversation history restoration accuracy
- ✅ SC-005: Zero in-memory conversation state (stateless)
- ✅ SC-006: 100% task operations via MCP tools
- ✅ SC-007: Clear confirmation messages
- ✅ SC-008: Graceful MCP tool error handling
- ✅ SC-009: Full task management workflow demonstrable
- ✅ SC-010: Correct conversation resumption after restart

### Testing Strategy

1. **Unit Tests**: Test models, services, and MCP client in isolation
2. **Integration Tests**: Test chat endpoint with real database and MCP server
3. **AI Agent Tests**: Test tool selection accuracy with various natural language inputs
4. **Persistence Tests**: Test conversation history restoration across requests
5. **Error Handling Tests**: Test graceful handling of OpenAI and MCP failures
6. **Performance Tests**: Measure response times under normal load
7. **Security Tests**: Verify JWT validation and user isolation

## Next Steps

1. ✅ Complete this plan (Phase 0-1 of /sp.plan) - COMPLETE
2. ✅ Phase 0: Research completed (research.md)
3. ✅ Phase 1: Design artifacts completed (data-model.md, contracts/chat-api.md, quickstart.md)
4. ✅ Agent context updated with new technologies
5. ⬜ Run `/sp.tasks` to generate task breakdown
6. ⬜ Run `/sp.implement` to execute implementation
7. ⬜ Test chat endpoint with sample natural language commands
8. ⬜ Integrate with frontend chat UI (Spec-3 extension)
