"""
SQLAlchemy model for users.
"""
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    User model for authentication and authorization.
    
    Attributes:
        id: Primary key
        username: Unique username (max 50 chars, stored lowercase)
        password_hash: Bcrypt hashed password
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to TodoItem model (one-to-many)
    todo_items = relationship(
        "TodoItem", 
        back_populates="owner", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
