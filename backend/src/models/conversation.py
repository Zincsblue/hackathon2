"""
Conversation model for AI Chat Agent.

This module defines the Conversation entity which represents a chat session
between a user and the AI agent.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class Conversation(SQLModel, table=True):
    """
    Represents a chat session between a user and the AI agent.

    Attributes:
        id: Unique identifier for the conversation
        user_id: Owner of the conversation (from JWT token)
        created_at: Timestamp when conversation was created
        updated_at: Timestamp when conversation was last updated
    """
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
