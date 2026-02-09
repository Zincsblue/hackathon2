"""
Message model for AI Chat Agent.

This module defines the Message entity which represents a single message
in a conversation (user or assistant).
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Message(SQLModel, table=True):
    """
    Represents a single message in a conversation.

    Attributes:
        id: Unique identifier for the message
        conversation_id: Parent conversation
        user_id: User who owns this conversation
        role: Message role - "user" or "assistant"
        content: Message text content
        created_at: Timestamp when message was created
    """
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True, nullable=False)
    user_id: str = Field(nullable=False)
    role: str = Field(nullable=False)  # "user" or "assistant"
    content: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
