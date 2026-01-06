"""
Pydantic schemas for to-do item requests and responses.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TodoItemCreate(BaseModel):
    """
    Schema for creating a new to-do item.
    """
    text: str = Field(..., min_length=1, max_length=500, description="To-do item text")


class TodoItemUpdateCompletion(BaseModel):
    """
    Schema for updating to-do item completion status.
    """
    completed: bool = Field(..., description="Completion status")


class TodoItemResponse(BaseModel):
    """
    Schema for to-do item response.
    """
    id: int
    user_id: int
    text: str
    completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
