# Research: AI Chat Agent & Conversation System

**Feature**: 005-ai-chat-agent
**Date**: 2026-02-09
**Status**: Complete

## Research Topics

### 1. OpenAI Agents SDK Usage

**Decision**: Use OpenAI Agents SDK (or OpenAI Python SDK with function calling) for AI agent implementation

**Rationale**:
- Official SDK provides standardized patterns for tool calling
- Built-in conversation history management
- Automatic tool schema generation from function definitions
- Handles tool invocation orchestration
- Provides retry logic and error handling

**Key Patterns**:
- Agent initialization: Create OpenAI client with API key
- Tool registration: Define tools as Python functions with type hints and docstrings
- Conversation history: Format messages as list of dicts with role and content
- Tool invocation: SDK automatically calls functions when agent selects them
- Response generation: Agent generates natural language responses after tool execution

**Implementation Approach**:
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define tools as functions
def add_task(user_id: str, title: str, description: str = None):
    """Create a new task for the user."""
    # Invoke MCP tool via MCP client
    return mcp_client.add_task(user_id, title, description)

# Register tools with agent
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {...}
        }
    }
]

# Process message with conversation history
response = client.chat.completions.create(
    model="gpt-4",
    messages=conversation_history,
    tools=tools,
    tool_choice="auto"
)
```

**Alternatives Considered**:
- Custom tool orchestration: Rejected due to complexity and maintenance burden
- LangChain: Rejected to minimize dependencies and maintain direct control

### 2. MCP Client Integration

**Decision**: Use MCP client library (if available) or HTTP client to invoke MCP tools from Python backend

**Rationale**:
- MCP server from Spec-4 exposes tools via MCP protocol
- Backend needs to invoke tools on behalf of AI agent
- Network calls maintain separation between chat endpoint and MCP server
- Allows independent scaling and deployment

**Implementation Approach**:
- If MCP Python client exists: Use official client library
- If no client: Use HTTP client (requests library) to call MCP server
- Wrap MCP calls in service layer for error handling
- Convert MCP responses to Python dicts for OpenAI agent

**MCP Client Wrapper Pattern**:
```python
class MCPClient:
    def __init__(self, mcp_server_url: str):
        self.base_url = mcp_server_url

    def add_task(self, user_id: str, title: str, description: str = None):
        response = requests.post(
            f"{self.base_url}/tools/add_task",
            json={"user_id": user_id, "title": title, "description": description}
        )
        return response.json()

    # Similar methods for other tools
```

**Error Handling**:
- Network errors: Retry with exponential backoff
- MCP tool errors: Parse error response and return to agent
- Timeout errors: Return timeout message to user

**Alternatives Considered**:
- Direct function calls to MCP tools: Rejected to maintain separation
- gRPC: Rejected as MCP protocol may not use gRPC

### 3. Conversation Persistence Strategy

**Decision**: Store conversations and messages in separate tables with user_id scoping

**Rationale**:
- Separate tables allow efficient querying and indexing
- Conversation entity tracks metadata (created_at, updated_at)
- Message entity stores individual messages with role and content
- User_id on both tables enables user isolation
- Chronological ordering via created_at timestamp

**Database Schema**:
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

**Query Patterns**:
```python
# Get or create conversation
conversation = session.exec(
    select(Conversation).where(Conversation.user_id == user_id)
).first()

if not conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()

# Load conversation history
messages = session.exec(
    select(Message)
    .where(Message.conversation_id == conversation.id)
    .order_by(Message.created_at)
).all()

# Save message
message = Message(
    conversation_id=conversation.id,
    user_id=user_id,
    role="user",
    content="Create a task to buy groceries"
)
session.add(message)
session.commit()
```

**Performance Optimization**:
- Index on conversation_id for fast message loading
- Index on created_at for chronological ordering
- Limit history to recent N messages (e.g., 50) to reduce load
- Consider pagination for very long conversations

**Alternatives Considered**:
- Single table with JSON: Rejected due to query complexity
- NoSQL: Rejected to maintain consistency with existing PostgreSQL

### 4. Stateless Endpoint Design

**Decision**: Load full conversation history from database on each request, no in-memory state

**Rationale**:
- Stateless design enables horizontal scaling
- No session affinity required for load balancing
- Server restarts don't lose conversation context
- Consistent with constitution principles

**Request/Response Flow**:
1. Client sends POST /api/{user_id}/chat with message and optional conversation_id
2. Endpoint validates JWT token and user_id
3. Get or create conversation for user
4. Load conversation history from database
5. Append user message to history
6. Save user message to database
7. Format history for OpenAI API
8. Invoke OpenAI agent with history and tools
9. Agent processes message and may invoke MCP tools
10. Agent generates response
11. Save assistant message to database
12. Return response with conversation_id

**Performance Considerations**:
- Database query per request (acceptable for <3 second target)
- Optimize with indexes on conversation_id and created_at
- Consider caching if database becomes bottleneck
- Limit history size to prevent large payloads

**Caching Strategy** (if needed):
- Cache conversation history in Redis with TTL
- Invalidate cache on new messages
- Fall back to database if cache miss

**Alternatives Considered**:
- In-memory conversation state: Rejected due to stateless requirement
- WebSocket with persistent connection: Rejected as out of scope

## Technology Stack Summary

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| AI Framework | OpenAI Python SDK | Latest | AI agent with function calling |
| MCP Client | HTTP client (requests) | Latest | MCP tool invocation |
| ORM | SQLModel | 0.0.22 | Database operations |
| Database Driver | psycopg2-binary | 2.9.9 | PostgreSQL connectivity |
| Database | Neon Serverless PostgreSQL | N/A | Data persistence |
| Web Framework | FastAPI | Latest | Chat endpoint |
| Validation | Pydantic | 2.x | Request/response validation |
| Testing | pytest | Latest | Unit and integration tests |

## Implementation Recommendations

1. **Stateless Design**: Store zero state in memory. All conversation context from database.
2. **User Isolation**: Always include user_id in WHERE clauses for conversation and message queries.
3. **Error Handling**: Catch OpenAI API errors and MCP tool errors, return user-friendly messages.
4. **Tool Invocation**: Wrap MCP client calls in try/except, handle network failures gracefully.
5. **Performance**: Limit conversation history to recent 50 messages, add database indexes.
6. **Security**: Validate JWT tokens, ensure user_id from token matches path parameter.

## Open Questions

None - all technical decisions resolved.
