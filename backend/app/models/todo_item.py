"""
SQLAlchemy model for to-do items.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class TodoItem(Base):
    """
    To-do item model.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to users table (owner of the item)
        text: The to-do item text (max 500 chars)
        completed: Whether the item is completed (default False)
        created_at: Timestamp when the item was created
        updated_at: Timestamp when the item was last updated
    """
    __tablename__ = "todo_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    text = Column(String(500), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to User model
    owner = relationship("User", back_populates="todo_items")
    
    def __repr__(self):
        return f"<TodoItem(id={self.id}, user_id={self.user_id}, completed={self.completed})>"
