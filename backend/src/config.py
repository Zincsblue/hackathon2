"""
Configuration management using Pydantic Settings.
Loads environment variables for database connection and API settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration (Neon Serverless PostgreSQL)
    database_url: str

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Debug Mode
    debug: bool = False

    # Logging Level
    log_level: str = "info"

    # CORS Configuration
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Authentication Configuration
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Rate Limiting
    redis_url: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file multiple times.
    """
    return Settings()

