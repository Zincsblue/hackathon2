"""
Authentication request and response schemas.
Defines data structures for registration, login, and token responses.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    """
    User registration request schema.
    Validates email format and password requirements.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        description="Password (minimum 8 characters)"
    )
    name: str = Field(..., min_length=1, max_length=255, description="User full name")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "name": "John Doe"
            }
        }


class UserLogin(BaseModel):
    """
    User login request schema.
    Requires email and password for authentication.
    """
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class TokenResponse(BaseModel):
    """
    Authentication token response schema.
    Returns access token and token metadata.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 900
            }
        }


class RefreshTokenRequest(BaseModel):
    """
    Token refresh request schema.
    Used when refresh token is sent in request body instead of cookie.
    """
    refresh_token: Optional[str] = Field(None, description="Refresh token (optional if using cookie)")


class PasswordResetRequest(BaseModel):
    """
    Password reset request schema.
    Initiates password reset flow by email.
    """
    email: EmailStr = Field(..., description="User email address")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetConfirm(BaseModel):
    """
    Password reset confirmation schema.
    Completes password reset with token and new password.
    """
    token: str = Field(..., description="Password reset token from email")
    new_password: str = Field(
        ...,
        min_length=8,
        description="New password (minimum 8 characters)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456",
                "new_password": "NewSecurePass123!"
            }
        }
