"""
Pydantic schemas for authentication requests and responses.
"""
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    Schema for login request.
    """
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class LoginUserInfo(BaseModel):
    """
    Schema for user info included in login response.
    """
    id: int
    username: str


class LoginResponse(BaseModel):
    """
    Schema for successful login response.
    """
    access_token: str
    token_type: str = "bearer"
    user: LoginUserInfo
