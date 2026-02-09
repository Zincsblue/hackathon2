"""
Rate limiting middleware using slowapi.
Protects authentication endpoints from brute force attacks.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors.

    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception

    Returns:
        JSON response with 429 status code
    """
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": str(exc.detail)
        }
    )


# Initialize limiter with in-memory backend (for testing without Redis)
# For production, use Redis: storage_uri="redis://localhost:6379"
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri="memory://",
    strategy="fixed-window"
)
