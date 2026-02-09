# Data Model: AI Chat Agent & Conversation System

**Feature**: 005-ai-chat-agent
**Date**: 2026-02-09
**Status**: Complete

## Overview

This document defines the database schema for the AI Chat Agent & Conversation System. The data model supports stateless conversation management with full history persistence and user isolation.

## Entities

### Conversation

Represents a chat session between a user and the AI agent.

**Fields**:
- `id` (int, primary key): Unique identifier for the conversation
- `user_id` (str, not null): Owner of the conversation (from JWT token)
- `created_at` (datetime, not null): Timestamp when conversation was created
- `updated_at` (datetime, not null): Timestamp when conversation was last updated

**Constraints**:
- `user_id` must be a valid user identifier from Better Auth
- `created_at` defaults to current timestamp
- `updated_at` defaults to current timestamp, updated on message addition

**Indexes**:
- Primary key on `id`
- Index on `user_id` for efficient user-scoped queries

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Conversation(SQLModel, table=True):
    __tablename__ = "conversations"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Message

Represents a single message in a conversation (user or assistant).

**Fields**:
- `id` (int, primary key): Unique identifier for the message
- `conversation_id` (int, foreign key, not null): Parent conversation
- `user_id` (str, not null): User who owns this conversation
- `role` (str, not null): Message role - "user" or "assistant"
- `content` (str, not null): Message text content
- `created_at` (datetime, not null): Timestamp when message was created

**Constraints**:
- `conversation_id` references `conversations.id` (foreign key)
- `role` must be either "user" or "assistant"
- `content` cannot be empty
- `created_at` defaults to current timestamp

**Indexes**:
- Primary key on `id`
- Index on `conversation_id` for efficient history loading
- Index on `created_at` for chronological ordering

**SQLModel Definition**:
```python
from sqlmodel import SQLModel, Field
from datetime import datetime

class Message(SQLModel, table=True):
    __tablename__ = "messages"

    id: int | None = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    user_id: str = Field(nullable=False)
    role: str = Field(nullable=False)  # "user" or "assistant"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

## Relationships

### One-to-Many: User → Conversations
- One user can have multiple conversations
- Each conversation belongs to exactly one user
- User isolation enforced by `user_id` field

### One-to-Many: Conversation → Messages
- One conversation contains multiple messages
- Each message belongs to exactly one conversation
- Messages are ordered chronologically by `created_at`

### Relationship Diagram

```
User (from Better Auth)
  |
  | 1:N
  |
Conversation
  |
  | 1:N
  |
Message
```

## Query Patterns

### Get or Create Conversation

```python
from sqlmodel import Session, select

def get_or_create_conversation(session: Session, user_id: str) -> Conversation:
    """Get existing conversation or create new one for user."""
    statement = select(Conversation).where(Conversation.user_id == user_id)
    conversation = session.exec(statement).first()

    if not conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    return conversation
```

### Load Conversation History

```python
from sqlmodel import Session, select

def load_conversation_history(session: Session, conversation_id: int) -> list[Message]:
    """Load all messages for a conversation in chronological order."""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = session.exec(statement).all()
    return list(messages)
```

### Save Message

```python
from sqlmodel import Session

def save_message(
    session: Session,
    conversation_id: int,
    user_id: str,
    role: str,
    content: str
) -> Message:
    """Save a new message to the conversation."""
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

    return message
```

### List User Conversations

```python
from sqlmodel import Session, select

def list_user_conversations(session: Session, user_id: str) -> list[Conversation]:
    """List all conversations for a user, ordered by most recent."""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    conversations = session.exec(statement).all()
    return list(conversations)
```

## Database Migrations

### Migration: Create Conversations Table

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
```

### Migration: Create Messages Table

```sql
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

## Performance Considerations

### Indexing Strategy
- **conversations.user_id**: Enables fast lookup of user's conversations
- **messages.conversation_id**: Enables fast loading of conversation history
- **messages.created_at**: Enables efficient chronological ordering

### History Size Management
- Limit conversation history to recent N messages (e.g., 50) when loading for AI agent
- Implement pagination for very long conversations (100+ messages)
- Consider archiving old conversations after inactivity period

### Query Optimization
- Use `select()` with explicit column selection for large result sets
- Batch message inserts when possible
- Use connection pooling for concurrent requests

## Data Validation

### Conversation Validation
- `user_id` must not be empty
- `user_id` must match authenticated user from JWT token
- Timestamps must be valid datetime objects

### Message Validation
- `conversation_id` must reference existing conversation
- `user_id` must match conversation owner
- `role` must be exactly "user" or "assistant"
- `content` must not be empty or whitespace-only
- `content` length should be reasonable (e.g., max 10,000 characters)

## Security Considerations

### User Isolation
- All queries must filter by `user_id` from JWT token
- Never expose conversation_id without user_id validation
- Prevent cross-user conversation access

### Data Sanitization
- Sanitize message content to prevent XSS attacks
- Validate role field to prevent injection
- Escape special characters in database queries

## Testing Strategy

### Unit Tests
- Test conversation creation and retrieval
- Test message persistence and ordering
- Test user isolation enforcement
- Test timestamp handling

### Integration Tests
- Test full conversation flow (create → add messages → load history)
- Test concurrent message additions
- Test conversation resumption after server restart
- Test history size limits

## Future Enhancements

### Potential Additions (Out of Scope for Current Implementation)
- Conversation titles/summaries
- Message editing and deletion
- Conversation branching
- Message reactions or feedback
- Conversation search and filtering
- Message attachments or metadata
- Conversation sharing between users
