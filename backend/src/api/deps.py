"""
API dependencies.
Shared dependencies for FastAPI routes.
"""
from typing import Annotated
from fastapi import Depends, Path, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select

from ..database import get_session
from ..services.token_service import token_service
from ..models.user import User

security = HTTPBearer()


def get_current_user_id(
    user_id: Annotated[str, Path(description="User ID from path parameter")]
) -> str:
    """
    Extract user_id from path parameter.

    Mock implementation for Spec-1 (Backend Core & Data Layer).
    In Spec-2 (Authentication), this will validate JWT token and extract user_id.

    For now, we trust the user_id from the path parameter to enable
    testing of user-scoped data isolation.

    Args:
        user_id: User ID from path parameter

    Returns:
        User ID string
    """
    return user_id


def get_current_user_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[Session, Depends(get_session)]
) -> User:
    """
    Extract and validate user from JWT access token.

    Args:
        credentials: HTTP Bearer token from Authorization header
        session: Database session

    Returns:
        User object if token is valid

    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    token = credentials.credentials

    # Verify token
    payload = token_service.verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Get user from database
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


# Type alias for cleaner endpoint signatures
CurrentUserDep = Annotated[str, Depends(get_current_user_id)]
CurrentUserFromToken = Annotated[User, Depends(get_current_user_from_token)]
