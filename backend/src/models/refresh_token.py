"""
RefreshToken SQLModel entity.
Manages refresh tokens for session management with token rotation.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class RefreshToken(SQLModel, table=True):
    """
    Refresh token entity for session management.
    Supports token rotation and device tracking.
    """
    __tablename__ = "refresh_tokens"

    id: int = Field(primary_key=True)
    user_id: str = Field(foreign_key="users.id", max_length=255, index=True)
    token_hash: str = Field(unique=True, index=True, max_length=255)
    expires_at: datetime = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = Field(default=None)
    replaced_by: Optional[int] = Field(default=None, foreign_key="refresh_tokens.id")
    device_info: Optional[str] = Field(default=None, max_length=500)
    ip_address: Optional[str] = Field(default=None, max_length=45)
