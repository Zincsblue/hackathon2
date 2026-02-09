"""
User profile schemas.
Defines data structures for user information responses.
"""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserProfile(BaseModel):
    """
    User profile response schema.
    Returns user information without sensitive data.
    """
    id: str = Field(..., description="User unique identifier")
    email: EmailStr = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    is_active: bool = Field(..., description="Account active status")
    is_verified: bool = Field(..., description="Email verification status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "user_123abc",
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
                "is_verified": False,
                "created_at": "2024-01-15T10:30:00Z",
                "last_login_at": "2024-01-20T14:45:00Z"
            }
        }
