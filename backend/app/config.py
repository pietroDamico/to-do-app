"""
Application configuration management.
Loads settings from environment variables with validation.
"""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/todo_app"
    
    # JWT configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # CORS configuration
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Application configuration
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings instance.
    Use lru_cache to avoid reading .env file on every request.
    """
    return Settings()


settings = get_settings()
