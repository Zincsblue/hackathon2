"""
PasswordResetToken SQLModel entity.
Manages password reset tokens with expiration.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class PasswordResetToken(SQLModel, table=True):
    """
    Password reset token entity.
    One-time use tokens with expiration for secure password resets.
    """
    __tablename__ = "password_reset_tokens"

    id: int = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id", max_length=255, index=True)
    token_hash: str = Field(unique=True, index=True, max_length=255)
    expires_at: datetime = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = Field(default=None)
