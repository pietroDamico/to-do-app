"""
Pydantic schemas for request/response validation.
Schemas define the structure of API inputs and outputs.
"""
from app.schemas.user import UserCreate, UserResponse, UserInDB
from app.schemas.auth import LoginRequest, LoginResponse, LoginUserInfo
from app.schemas.todo_item import TodoItemCreate, TodoItemUpdateCompletion, TodoItemResponse

__all__ = [
    "UserCreate", 
    "UserResponse", 
    "UserInDB",
    "LoginRequest",
    "LoginResponse",
    "LoginUserInfo",
    "TodoItemCreate",
    "TodoItemUpdateCompletion",
    "TodoItemResponse",
]
