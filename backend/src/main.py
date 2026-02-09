"""
FastAPI application entry point.
Initializes the API with CORS middleware, exception handlers, and routes.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from .config import get_settings
from .api.routes import tasks, auth
from .middleware.rate_limit import limiter, rate_limit_exceeded_handler

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure security logger
security_logger = logging.getLogger("security")
security_handler = logging.FileHandler("security.log")
security_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
security_logger.addHandler(security_handler)
security_logger.setLevel(logging.INFO)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Enforce HTTPS (only in production)
        if not settings.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'"
        )

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response

# Initialize FastAPI app
app = FastAPI(
    title="Task Management API",
    description="RESTful API for user-scoped task management with CRUD operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    debug=settings.debug
)

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns service status and basic information.
    """
    return {
        "status": "healthy",
        "service": "Task Management API",
        "version": "1.0.0"
    }


# Register task routes
app.include_router(tasks.router, prefix="/api/v1")

# Register authentication routes
app.include_router(auth.router, prefix="/api/v1")

logger.info(f"Task Management API started on {settings.api_host}:{settings.api_port}")
