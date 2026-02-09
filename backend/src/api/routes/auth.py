"""
Authentication API routes.
Handles user registration, login, token refresh, and session management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlmodel import Session

from ...database import get_session
from ...schemas.auth import (
    UserRegister,
    UserLogin,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm
)
from ...schemas.user import UserProfile
from ...services.auth_service import auth_service
from ...middleware.rate_limit import limiter
from ...config import get_settings
from ..deps import get_current_user_from_token
from ...models.user import User

router = APIRouter(tags=["Authentication"])
settings = get_settings()


@router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with email and password. Returns access token and sets refresh token cookie."
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    response: Response,
    user_data: UserRegister,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Register a new user account.

    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **name**: User full name

    Returns JWT access token and sets httpOnly refresh token cookie.
    """
    try:
        user, access_token, refresh_token = auth_service.register_user(
            session=session,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )

        # Set refresh token in httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # HTTPS only in production
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    summary="User login",
    description="Authenticate user with email and password. Returns access token and sets refresh token cookie."
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    credentials: UserLogin,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Authenticate user and create session.

    - **email**: User email address
    - **password**: User password

    Returns JWT access token and sets httpOnly refresh token cookie.
    Account will be locked for 15 minutes after 10 failed login attempts.
    """
    try:
        # Extract client info
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent", "")

        user, access_token, refresh_token = auth_service.login_user(
            session=session,
            email=credentials.email,
            password=credentials.password,
            ip_address=ip_address,
            device_info=user_agent[:500]  # Truncate to max length
        )

        # Set refresh token in httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post(
    "/auth/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange refresh token for new access token with token rotation."
)
@limiter.limit("20/minute")
async def refresh_token(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
) -> TokenResponse:
    """
    Refresh access token using refresh token cookie.

    Token rotation: Old refresh token is invalidated and new one is issued.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    try:
        new_access_token, new_refresh_token = auth_service.refresh_access_token(
            session=session,
            refresh_token=refresh_token
        )

        # Set new refresh token in httpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.refresh_token_expire_days * 24 * 60 * 60
        )

        return TokenResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Revoke refresh token and end session."
)
@limiter.limit("10/minute")
async def logout(
    request: Request,
    response: Response,
    session: Session = Depends(get_session)
):
    """
    Logout user by revoking refresh token.

    Clears refresh token cookie and marks token as revoked in database.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        # Already logged out, return success
        response.delete_cookie("refresh_token")
        return

    try:
        auth_service.logout_user(
            session=session,
            refresh_token=refresh_token
        )
    except ValueError:
        # Token not found or already revoked, continue to clear cookie
        pass
    except Exception:
        # Log error but still clear cookie
        pass

    # Clear refresh token cookie
    response.delete_cookie("refresh_token")


@router.get(
    "/auth/me",
    response_model=UserProfile,
    summary="Get current user profile",
    description="Returns profile information for the authenticated user."
)
@limiter.limit("100/minute")
async def get_current_user(
    request: Request,
    current_user: User = Depends(get_current_user_from_token)
) -> UserProfile:
    """
    Get current user profile from JWT token.

    Requires valid access token in Authorization header.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at
    )
