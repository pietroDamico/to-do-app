"""
To-do items router for CRUD operations.
All endpoints require authentication and enforce user ownership.
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.todo_item import TodoItem
from app.schemas.todo_item import TodoItemCreate, TodoItemUpdateCompletion, TodoItemResponse
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/todos", tags=["todos"])


@router.post("/", response_model=TodoItemResponse, status_code=status.HTTP_201_CREATED)
async def create_todo_item(
    todo_data: TodoItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new to-do item for the authenticated user.
    
    - **text**: 1-500 characters, the to-do item content
    
    Returns the created to-do item.
    """
    logger.info(f"Creating todo for user_id: {current_user.id}")
    
    # Create new todo item
    new_todo = TodoItem(
        user_id=current_user.id,
        text=todo_data.text.strip(),  # Remove leading/trailing whitespace
        completed=False
    )
    
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    
    logger.info(f"Todo created: id={new_todo.id} for user_id={current_user.id}")
    return new_todo


@router.get("/", response_model=List[TodoItemResponse])
async def get_all_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all to-do items for the authenticated user.
    
    Returns items in reverse chronological order (newest first).
    """
    logger.info(f"Fetching todos for user_id: {current_user.id}")
    
    todos = db.query(TodoItem)\
              .filter(TodoItem.user_id == current_user.id)\
              .order_by(TodoItem.id.desc())\
              .all()
    
    logger.info(f"Returning {len(todos)} todos for user_id={current_user.id}")
    return todos


@router.patch("/{todo_id}", response_model=TodoItemResponse)
async def update_todo_completion(
    todo_id: int,
    update_data: TodoItemUpdateCompletion,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the completion status of a to-do item.
    
    Users can only update their own items.
    
    - **completed**: Boolean indicating completion status
    
    Returns the updated to-do item.
    """
    logger.info(f"Updating todo_id={todo_id} for user_id={current_user.id}")
    
    # Get the todo item
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    
    # Check if todo exists
    if not todo:
        logger.warning(f"Todo not found: id={todo_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo item not found"
        )
    
    # Check authorization (user owns this todo)
    if todo.user_id != current_user.id:
        logger.warning(f"Authorization failed: user_id={current_user.id} tried to update todo_id={todo_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this item"
        )
    
    # Update completion status
    todo.completed = update_data.completed
    db.commit()
    db.refresh(todo)
    
    logger.info(f"Todo updated: id={todo_id}, completed={update_data.completed}")
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_item(
    todo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a to-do item permanently.
    
    Users can only delete their own items.
    
    Returns 204 No Content on success.
    """
    logger.info(f"Deleting todo_id={todo_id} for user_id={current_user.id}")
    
    # Get the todo item
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    
    # Check if todo exists
    if not todo:
        logger.warning(f"Todo not found: id={todo_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo item not found"
        )
    
    # Check authorization (user owns this todo)
    if todo.user_id != current_user.id:
        logger.warning(f"Authorization failed: user_id={current_user.id} tried to delete todo_id={todo_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this item"
        )
    
    # Delete the todo
    db.delete(todo)
    db.commit()
    
    logger.info(f"Todo deleted: id={todo_id}")
    return None
