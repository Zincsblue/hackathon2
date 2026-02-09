"""
Authentication service.
Handles user registration, login, token refresh, and session management.
"""
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlmodel import Session, select

from ..models.user import User
from ..models.refresh_token import RefreshToken
from .password_service import password_service
from .token_service import token_service
from ..config import get_settings

# Configure logger for security events
logger = logging.getLogger(__name__)
security_logger = logging.getLogger("security")


class AuthService:
    """
    Authentication service for user management and token handling.
    """

    def __init__(self):
        """Initialize auth service with settings."""
        self.settings = get_settings()

    def register_user(
        self,
        session: Session,
        email: str,
        password: str,
        name: str
    ) -> Tuple[User, str, str]:
        """
        Register a new user account.

        Args:
            session: Database session
            email: User email address
            password: Plain text password
            name: User full name

        Returns:
            Tuple of (User, access_token, refresh_token)

        Raises:
            ValueError: If email already exists or validation fails
        """
        # Check if user already exists
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if existing_user:
            raise ValueError("Email already registered")

        # Generate user ID
        user_id = f"user_{secrets.token_urlsafe(16)}"

        # Hash password
        password_hash = password_service.hash_password(password)

        # Create user
        user = User(
            id=user_id,
            email=email,
            name=name,
            password_hash=password_hash,
            is_active=True,
            is_verified=False,
            failed_login_attempts=0
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        # Generate tokens
        access_token = token_service.create_access_token(
            user_id=user.id,
            email=user.email
        )

        refresh_token = token_service.create_refresh_token(user_id=user.id)

        # Store refresh token in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=self.settings.refresh_token_expire_days)

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        session.add(refresh_token_record)
        session.commit()

        # Log successful registration
        security_logger.info(
            f"User registered successfully: user_id={user.id}, email={user.email}"
        )

        return user, access_token, refresh_token

    def login_user(
        self,
        session: Session,
        email: str,
        password: str,
        ip_address: Optional[str] = None,
        device_info: Optional[str] = None
    ) -> Tuple[User, str, str]:
        """
        Authenticate user and create session.

        Args:
            session: Database session
            email: User email address
            password: Plain text password
            ip_address: Optional client IP address
            device_info: Optional device information

        Returns:
            Tuple of (User, access_token, refresh_token)

        Raises:
            ValueError: If credentials are invalid or account is locked
        """
        # Find user by email
        user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if not user:
            raise ValueError("Invalid email or password")

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise ValueError("Account is locked. Please try again later.")

        # Check if account is active
        if not user.is_active:
            raise ValueError("Account is inactive")

        # Verify password
        if not password_service.verify_password(password, user.password_hash):
            # Increment failed login attempts
            user.failed_login_attempts += 1

            # Lock account after 10 failed attempts
            if user.failed_login_attempts >= 10:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
                security_logger.warning(
                    f"Account locked due to failed login attempts: user_id={user.id}, email={user.email}"
                )

            session.add(user)
            session.commit()

            # Log failed login attempt
            security_logger.warning(
                f"Failed login attempt: email={email}, attempts={user.failed_login_attempts}, ip={ip_address}"
            )

            raise ValueError("Invalid email or password")

        # Reset failed login attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()

        session.add(user)
        session.commit()
        session.refresh(user)

        # Generate tokens
        access_token = token_service.create_access_token(
            user_id=user.id,
            email=user.email
        )

        refresh_token = token_service.create_refresh_token(user_id=user.id)

        # Store refresh token in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=self.settings.refresh_token_expire_days)

        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            device_info=device_info
        )

        session.add(refresh_token_record)
        session.commit()

        # Log successful login
        security_logger.info(
            f"User logged in successfully: user_id={user.id}, email={user.email}, ip={ip_address}"
        )

        return user, access_token, refresh_token

    def refresh_access_token(
        self,
        session: Session,
        refresh_token: str
    ) -> Tuple[str, str]:
        """
        Refresh access token using refresh token with rotation.

        Args:
            session: Database session
            refresh_token: Current refresh token

        Returns:
            Tuple of (new_access_token, new_refresh_token)

        Raises:
            ValueError: If refresh token is invalid, expired, or revoked
        """
        # Verify refresh token
        payload = token_service.verify_token(refresh_token, token_type="refresh")
        if not payload:
            raise ValueError("Invalid or expired refresh token")

        user_id = payload.get("sub")

        # Hash token and lookup in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        token_record = session.exec(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == user_id
            )
        ).first()

        if not token_record:
            raise ValueError("Refresh token not found")

        # Check if token is revoked
        if token_record.revoked_at:
            raise ValueError("Refresh token has been revoked")

        # Check if token is expired
        if token_record.expires_at < datetime.utcnow():
            raise ValueError("Refresh token has expired")

        # Get user
        user = session.exec(select(User).where(User.id == user_id)).first()
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        # Generate new tokens
        new_access_token = token_service.create_access_token(
            user_id=user.id,
            email=user.email
        )

        new_refresh_token = token_service.create_refresh_token(user_id=user.id)

        # Store new refresh token
        new_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
        expires_at = datetime.utcnow() + timedelta(days=self.settings.refresh_token_expire_days)

        new_token_record = RefreshToken(
            user_id=user.id,
            token_hash=new_token_hash,
            expires_at=expires_at
        )

        session.add(new_token_record)

        # Mark old token as replaced
        token_record.replaced_by = new_token_record.id
        session.add(token_record)

        session.commit()
        session.refresh(new_token_record)

        # Update replaced_by reference
        token_record.replaced_by = new_token_record.id
        session.add(token_record)
        session.commit()

        # Log token refresh
        security_logger.info(
            f"Token refreshed successfully: user_id={user.id}"
        )

        return new_access_token, new_refresh_token

    def logout_user(
        self,
        session: Session,
        refresh_token: str
    ) -> None:
        """
        Logout user by revoking refresh token.

        Args:
            session: Database session
            refresh_token: Refresh token to revoke

        Raises:
            ValueError: If refresh token is invalid
        """
        # Hash token and lookup in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        token_record = session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        ).first()

        if not token_record:
            raise ValueError("Refresh token not found")

        # Mark token as revoked
        token_record.revoked_at = datetime.utcnow()
        session.add(token_record)
        session.commit()

        # Log logout
        security_logger.info(
            f"User logged out successfully: user_id={token_record.user_id}"
        )


# Singleton instance
auth_service = AuthService()
