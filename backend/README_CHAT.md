# AI Chat Agent Service

## Overview

The AI Chat Agent service provides natural language task management through conversational interactions with an OpenAI-powered AI agent. Users can create, view, update, complete, and delete tasks using natural language commands.

## Features

- **Natural Language Task Management**: Create and manage tasks through conversational chat
- **Conversation Persistence**: Full conversation history saved and restored from database
- **Stateless Architecture**: Zero in-memory state, survives server restarts
- **OpenAI GPT-4 Integration**: AI agent with function calling capabilities
- **MCP Tool Integration**: All task operations via MCP tools (no direct database access)
- **JWT Authentication**: Secure user isolation and validation
- **Comprehensive Error Handling**: 9 error codes with proper HTTP status codes
- **Rate Limiting**: 60 requests per minute per user
- **Security Features**: XSS prevention, input sanitization, timeout protection

## Architecture

### Components

1. **Chat Endpoint** (`backend/src/api/chat.py`)
   - POST /api/{user_id}/chat
   - JWT authentication and validation
   - Request/response validation
   - Rate limiting and timeout handling

2. **Chat Service** (`backend/src/services/chat_service.py`)
   - Conversation management
   - OpenAI agent orchestration
   - MCP tool invocation
   - Message persistence

3. **MCP Client** (`backend/src/services/mcp_client.py`)
   - HTTP wrapper for MCP server
   - Retry logic with exponential backoff
   - Error handling for all 5 tools

4. **Database Models** (`backend/src/models/`)
   - Conversation: Chat session entity
   - Message: Individual message entity

## API Usage

### Send Chat Message

```bash
POST /api/{user_id}/chat
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "message": "Create a task to buy groceries",
  "conversation_id": 123  // optional
}
```

### Response

```json
{
  "conversation_id": 123,
  "message": {
    "role": "assistant",
    "content": "I've created a task: 'Buy groceries'. Is there anything else you'd like me to help with?",
    "created_at": "2026-02-09T10:30:00Z"
  }
}
```

## Natural Language Commands

### Create Tasks
- "Create a task to buy groceries"
- "Remind me to call the dentist tomorrow"
- "Add a task for submitting the report"

### View Tasks
- "What are my tasks?"
- "Show me my todo list"
- "What do I need to do today?"

### Complete Tasks
- "I finished buying groceries"
- "Mark 'call the dentist' as complete"
- "Done with the report"

### Update Tasks
- "Change the groceries task to 'Buy groceries and cook dinner'"
- "Add a note to the dentist task: bring insurance card"

### Delete Tasks
- "Delete the groceries task"
- "Remove the dentist task"

## Configuration

### Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# MCP Server Configuration
MCP_SERVER_URL=http://localhost:8001

# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/database

# Authentication
JWT_SECRET_KEY=your-secret-key-here
```

## Error Handling

The service returns structured error responses with the following codes:

- **UNAUTHORIZED**: Invalid or missing JWT token
- **USER_MISMATCH**: user_id doesn't match JWT token
- **INVALID_INPUT**: Malformed request
- **MESSAGE_TOO_LONG**: Message exceeds 10,000 characters
- **CONVERSATION_NOT_FOUND**: Invalid conversation_id
- **MCP_TOOL_ERROR**: MCP tool invocation failed
- **MCP_UNAVAILABLE**: MCP server unreachable
- **OPENAI_API_ERROR**: OpenAI API request failed
- **AGENT_TIMEOUT**: Request exceeded 5-second timeout
- **INTERNAL_ERROR**: Unexpected server error

## Performance

- **Response Time**: p95 < 3 seconds
- **Timeout**: 5 seconds (hard limit)
- **Rate Limit**: 60 requests/minute per user
- **History Limit**: 50 messages per conversation
- **Retry Logic**: 3 retries with exponential backoff for MCP tools

## Security

- JWT token validation on every request
- User isolation enforced (all queries filtered by user_id)
- Conversation ownership validation
- XSS prevention via content sanitization
- Input validation (message length, conversation_id)
- Timeout protection (5 seconds)

## Database Schema

### Conversations Table
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

### Messages Table
```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

## Testing

See `specs/005-ai-chat-agent/quickstart.md` for detailed testing examples.

## Deployment

See `DEPLOYMENT.md` for production deployment instructions.

## Troubleshooting

### "Conversation not found" error
- Ensure conversation_id belongs to the authenticated user
- Omit conversation_id to start a new conversation

### Slow responses
- Check OpenAI API status
- Verify MCP server is running and responsive
- Review database query performance

### Agent doesn't understand request
- Be more specific in your phrasing
- Ask the agent for help: "What can you help me with?"

## Support

For issues or questions, refer to:
- API Contract: `specs/005-ai-chat-agent/contracts/chat-api.md`
- Data Model: `specs/005-ai-chat-agent/data-model.md`
- Quickstart Guide: `specs/005-ai-chat-agent/quickstart.md`
