# Quickstart Guide: AI Chat Agent

**Feature**: 005-ai-chat-agent
**Date**: 2026-02-09
**Status**: Complete

## Overview

This guide shows you how to interact with the AI Chat Agent to manage your tasks using natural language. The AI agent understands conversational commands and invokes the appropriate task management tools on your behalf.

## Prerequisites

- Valid user account with Better Auth
- JWT authentication token
- Access to the chat endpoint: `POST /api/{user_id}/chat`

## Getting Started

### 1. Obtain Authentication Token

First, authenticate with Better Auth to get your JWT token:

```bash
# Example: Login to get JWT token
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'

# Response includes JWT token
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user123",
    "email": "user@example.com"
  }
}
```

### 2. Send Your First Message

Use the JWT token to send a message to the AI agent:

```bash
curl -X POST https://api.example.com/api/user123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a task to buy groceries"
  }'
```

**Response**:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I've created a task: 'Buy groceries'. Would you like me to add any additional details?",
    "created_at": "2026-02-09T10:30:00Z"
  }
}
```

### 3. Continue the Conversation

Include the `conversation_id` to maintain context:

```bash
curl -X POST https://api.example.com/api/user123/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Yes, add milk and eggs to the description",
    "conversation_id": 1
  }'
```

## Common Use Cases

### Creating Tasks

The AI agent understands various ways to create tasks:

**Direct command**:
```json
{
  "message": "Create a task to call the dentist"
}
```

**Natural phrasing**:
```json
{
  "message": "Remind me to submit the report by Friday"
}
```

**Casual request**:
```json
{
  "message": "I need to buy milk"
}
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I've created a task: 'Buy milk'. Anything else?",
    "created_at": "2026-02-09T10:30:00Z"
  }
}
```

### Viewing Tasks

Ask the agent to show your tasks:

**List all tasks**:
```json
{
  "message": "What are my tasks?",
  "conversation_id": 1
}
```

**Alternative phrasings**:
```json
{
  "message": "Show me my todo list"
}
```

```json
{
  "message": "What do I need to do today?"
}
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "You have 3 tasks:\n1. Buy groceries (not completed)\n2. Call the dentist (not completed)\n3. Submit report (not completed)\n\nWould you like to mark any as complete?",
    "created_at": "2026-02-09T10:31:00Z"
  }
}
```

### Completing Tasks

Tell the agent when you've finished a task:

**Direct completion**:
```json
{
  "message": "I finished buying groceries",
  "conversation_id": 1
}
```

**Mark as done**:
```json
{
  "message": "Mark 'call the dentist' as complete",
  "conversation_id": 1
}
```

**Casual update**:
```json
{
  "message": "Done with the report",
  "conversation_id": 1
}
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "Great! I've marked 'Buy groceries' as completed. You have 2 remaining tasks.",
    "created_at": "2026-02-09T10:32:00Z"
  }
}
```

### Updating Tasks

Modify task details conversationally:

**Change title**:
```json
{
  "message": "Change the groceries task to 'Buy groceries and cook dinner'",
  "conversation_id": 1
}
```

**Add description**:
```json
{
  "message": "Add a note to the dentist task: bring insurance card",
  "conversation_id": 1
}
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I've updated the task title to 'Buy groceries and cook dinner'.",
    "created_at": "2026-02-09T10:33:00Z"
  }
}
```

### Deleting Tasks

Remove tasks you no longer need:

**Delete specific task**:
```json
{
  "message": "Delete the groceries task",
  "conversation_id": 1
}
```

**Remove task**:
```json
{
  "message": "I don't need the dentist task anymore",
  "conversation_id": 1
}
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I've deleted the task 'Buy groceries'.",
    "created_at": "2026-02-09T10:34:00Z"
  }
}
```

## Handling Ambiguity

The AI agent will ask for clarification when your request is unclear:

**Ambiguous request**:
```json
{
  "message": "groceries",
  "conversation_id": 1
}
```

**Agent's clarifying response**:
```json
{
  "conversation_id": 1,
  "message": {
    "role": "assistant",
    "content": "I'm not sure what you'd like me to do with 'groceries'. Would you like me to:\n1. Create a new task for groceries\n2. Show you existing grocery-related tasks\n3. Something else?",
    "created_at": "2026-02-09T10:35:00Z"
  }
}
```

**Your clarification**:
```json
{
  "message": "Create a new task",
  "conversation_id": 1
}
```

## Error Handling

### Authentication Errors

If your token is invalid or missing:

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing authentication token"
  }
}
```

**Solution**: Obtain a new JWT token by logging in again.

### Task Not Found

If you reference a non-existent task:

```json
{
  "error": {
    "code": "MCP_TOOL_ERROR",
    "message": "I couldn't find a task matching that description. Would you like to see your current tasks?",
    "details": {
      "tool": "complete_task",
      "mcp_error": "TASK_NOT_FOUND"
    }
  }
}
```

**Solution**: Ask the agent to list your tasks first, then reference them correctly.

### Service Unavailable

If the MCP server or OpenAI API is temporarily unavailable:

```json
{
  "error": {
    "code": "MCP_UNAVAILABLE",
    "message": "Task management service is temporarily unavailable",
    "details": {
      "retry_after": 30
    }
  }
}
```

**Solution**: Wait a few seconds and retry your request.

## Best Practices

### 1. Be Specific

**Good**: "Create a task to buy milk and eggs from the grocery store"
**Less Good**: "groceries"

### 2. Use Context

The agent remembers your conversation, so you can reference previous messages:

```json
// First message
{"message": "Create a task to buy groceries"}

// Follow-up (agent understands "it" refers to the groceries task)
{"message": "Make it high priority"}
```

### 3. Ask for Help

If you're unsure what the agent can do:

```json
{
  "message": "What can you help me with?",
  "conversation_id": 1
}
```

### 4. Provide Feedback

If the agent misunderstands, clarify:

```json
{
  "message": "No, I meant the other task",
  "conversation_id": 1
}
```

## Integration Examples

### JavaScript/TypeScript (Frontend)

```typescript
// Chat service for Next.js frontend
class ChatService {
  private baseUrl = 'https://api.example.com';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  async sendMessage(userId: string, message: string, conversationId?: number) {
    const response = await fetch(`${this.baseUrl}/api/${userId}/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }

    return await response.json();
  }
}

// Usage
const chatService = new ChatService(userToken);
const response = await chatService.sendMessage(
  'user123',
  'Create a task to buy groceries'
);
console.log(response.message.content);
```

### Python (Backend/Testing)

```python
import requests

class ChatClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def send_message(self, user_id: str, message: str, conversation_id: int = None):
        url = f'{self.base_url}/api/{user_id}/chat'
        payload = {'message': message}
        if conversation_id:
            payload['conversation_id'] = conversation_id

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Usage
client = ChatClient('https://api.example.com', user_token)
response = client.send_message('user123', 'What are my tasks?')
print(response['message']['content'])
```

### cURL (Command Line)

```bash
#!/bin/bash

# Set your credentials
TOKEN="your_jwt_token_here"
USER_ID="user123"
API_URL="https://api.example.com"

# Function to send chat message
send_message() {
  local message="$1"
  local conversation_id="$2"

  if [ -z "$conversation_id" ]; then
    curl -X POST "$API_URL/api/$USER_ID/chat" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"$message\"}"
  else
    curl -X POST "$API_URL/api/$USER_ID/chat" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"message\": \"$message\", \"conversation_id\": $conversation_id}"
  fi
}

# Create a task
send_message "Create a task to buy groceries"

# Continue conversation (use conversation_id from previous response)
send_message "What are my tasks?" 1
```

## Conversation Management

### Starting a New Conversation

Omit `conversation_id` to start fresh:

```json
{
  "message": "Create a task to buy groceries"
}
```

### Continuing a Conversation

Include `conversation_id` to maintain context:

```json
{
  "message": "Add another task",
  "conversation_id": 1
}
```

### Conversation Persistence

Conversations are automatically saved and can be resumed even after:
- Server restarts
- User logout/login
- Browser refresh (frontend)

The agent will remember your full conversation history.

## Performance Tips

### Response Times

- **Typical response**: 1-2 seconds
- **Complex requests**: 2-3 seconds
- **Maximum timeout**: 5 seconds

### Rate Limits

- **Per user**: 60 requests per minute
- **Global**: 1000 requests per minute

If you hit rate limits, wait 60 seconds before retrying.

## Troubleshooting

### "Conversation not found" error

**Cause**: Invalid conversation_id or conversation belongs to another user

**Solution**: Omit conversation_id to start a new conversation

### Agent doesn't understand my request

**Cause**: Ambiguous or unclear phrasing

**Solution**: Be more specific or ask the agent for help

### Slow responses

**Cause**: High server load or complex AI processing

**Solution**: Wait for response (up to 5 seconds) or retry if timeout occurs

## Next Steps

- **Frontend Integration**: See Spec-3 for Next.js chat UI implementation
- **API Reference**: See `contracts/chat-api.md` for complete API documentation
- **Data Model**: See `data-model.md` for conversation and message schemas
- **Architecture**: See `plan.md` for technical implementation details

## Support

For issues or questions:
- Check error codes in `contracts/chat-api.md`
- Review conversation history for context
- Contact support with conversation_id for debugging
