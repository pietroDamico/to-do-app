"""
Pydantic schemas for User API requests and responses.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class UserCreate(BaseModel):
    """
    Schema for user registration input.
    
    Attributes:
        username: 3-50 characters, alphanumeric and underscore only
        password: Minimum 8 characters
    """
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username contains only alphanumeric characters and underscores."""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v.lower()  # Store username in lowercase


class UserResponse(BaseModel):
    """
    Schema for user API responses.
    Excludes password hash for security.
    """
    id: int
    username: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserInDB(BaseModel):
    """
    Schema for internal user representation.
    Includes password hash for authentication operations.
    """
    id: int
    username: str
    password_hash: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
