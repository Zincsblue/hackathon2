"""
JWT token generation and verification service.
Handles access tokens and refresh tokens with configurable expiration.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from ..config import get_settings


class TokenService:
    """
    JWT token service for authentication.
    Uses HS256 algorithm with configurable secret key and expiration.
    """

    def __init__(self):
        """Initialize token service with settings."""
        self.settings = get_settings()

    def create_access_token(
        self,
        user_id: str,
        email: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.

        Args:
            user_id: User ID to encode in token
            email: User email to encode in token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.settings.access_token_expire_minutes)

        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }

        return jwt.encode(
            payload,
            self.settings.secret_key,
            algorithm=self.settings.algorithm
        )

    def create_refresh_token(
        self,
        user_id: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT refresh token.

        Args:
            user_id: User ID to encode in token
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token string
        """
        if expires_delta is None:
            expires_delta = timedelta(days=self.settings.refresh_token_expire_days)

        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }

        return jwt.encode(
            payload,
            self.settings.secret_key,
            algorithm=self.settings.algorithm
        )

    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.

        Args:
            token: JWT token string to verify
            token_type: Expected token type ("access" or "refresh")

        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.algorithm]
            )

            # Verify token type matches expected type
            if payload.get("type") != token_type:
                return None

            return payload

        except JWTError:
            return None

    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from a valid token.

        Args:
            token: JWT token string

        Returns:
            User ID if token is valid, None otherwise
        """
        payload = self.verify_token(token)
        if payload:
            return payload.get("sub")
        return None


# Singleton instance
token_service = TokenService()
