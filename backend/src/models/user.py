"""
User SQLModel entity.
Represents an authenticated user who owns tasks.
"""
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional


class User(SQLModel, table=True):
    """
    User entity with authentication support.
    Includes password hashing, account status, and security features.
    """
    __tablename__ = "users"

    id: str = Field(primary_key=True, max_length=255)
    email: str = Field(unique=True, index=True, max_length=255)
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Authentication fields
    password_hash: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None)
    last_login_at: Optional[datetime] = Field(default=None)
