"""
Tests for TodoItem model and schemas.
"""
import pytest
from pydantic import ValidationError

from app.models.todo_item import TodoItem
from app.models.user import User
from app.schemas.todo_item import TodoItemCreate, TodoItemUpdateCompletion, TodoItemResponse


class TestTodoItemModel:
    """Tests for TodoItem SQLAlchemy model."""

    def test_todo_item_model_has_required_fields(self):
        """Test that TodoItem model has all required fields."""
        assert hasattr(TodoItem, 'id')
        assert hasattr(TodoItem, 'user_id')
        assert hasattr(TodoItem, 'text')
        assert hasattr(TodoItem, 'completed')
        assert hasattr(TodoItem, 'created_at')
        assert hasattr(TodoItem, 'updated_at')

    def test_todo_item_model_tablename(self):
        """Test that TodoItem model has correct table name."""
        assert TodoItem.__tablename__ == "todo_items"

    def test_todo_item_repr(self, db_session):
        """Test TodoItem string representation."""
        # Create a user first
        user = User(username="testuser", password_hash="hashedpassword")
        db_session.add(user)
        db_session.commit()
        
        todo = TodoItem(user_id=user.id, text="Test todo", completed=False)
        db_session.add(todo)
        db_session.commit()
        
        repr_str = repr(todo)
        assert "TodoItem" in repr_str
        assert str(todo.id) in repr_str
        assert str(user.id) in repr_str

    def test_todo_item_can_be_created(self, db_session):
        """Test that TodoItem can be created and saved."""
        user = User(username="todouser", password_hash="hashedpassword")
        db_session.add(user)
        db_session.commit()
        
        todo = TodoItem(user_id=user.id, text="Buy groceries", completed=False)
        db_session.add(todo)
        db_session.commit()
        
        assert todo.id is not None
        assert todo.user_id == user.id
        assert todo.text == "Buy groceries"
        assert todo.completed is False
        assert todo.created_at is not None

    def test_todo_item_completed_defaults_to_false(self, db_session):
        """Test that completed defaults to False."""
        user = User(username="defaultuser", password_hash="hashedpassword")
        db_session.add(user)
        db_session.commit()
        
        todo = TodoItem(user_id=user.id, text="Test default")
        db_session.add(todo)
        db_session.commit()
        
        assert todo.completed is False

    def test_todo_item_relationship_to_user(self, db_session):
        """Test foreign key relationship to User works."""
        user = User(username="reluser", password_hash="hashedpassword")
        db_session.add(user)
        db_session.commit()
        
        todo = TodoItem(user_id=user.id, text="Related todo")
        db_session.add(todo)
        db_session.commit()
        
        # Test relationship from todo to user
        assert todo.owner.id == user.id
        assert todo.owner.username == "reluser"
        
        # Test relationship from user to todos
        assert len(user.todo_items) == 1
        assert user.todo_items[0].text == "Related todo"

    def test_cascade_delete_removes_todos(self, db_session):
        """Test that deleting user deletes their todos."""
        user = User(username="cascadeuser", password_hash="hashedpassword")
        db_session.add(user)
        db_session.commit()
        
        todo1 = TodoItem(user_id=user.id, text="Todo 1")
        todo2 = TodoItem(user_id=user.id, text="Todo 2")
        db_session.add_all([todo1, todo2])
        db_session.commit()
        
        # Get todo ids before deletion
        todo_ids = [todo1.id, todo2.id]
        
        # Delete the user
        db_session.delete(user)
        db_session.commit()
        
        # Verify todos are deleted
        remaining_todos = db_session.query(TodoItem).filter(
            TodoItem.id.in_(todo_ids)
        ).all()
        assert len(remaining_todos) == 0

    def test_user_can_have_multiple_todos(self, db_session):
        """Test that a user can have multiple to-do items."""
        user = User(username="multiuser", password_hash="hashedpassword")
        db_session.add(user)
        db_session.commit()
        
        todos = [
            TodoItem(user_id=user.id, text=f"Todo {i}")
            for i in range(5)
        ]
        db_session.add_all(todos)
        db_session.commit()
        
        assert len(user.todo_items) == 5


class TestTodoItemSchemas:
    """Tests for TodoItem Pydantic schemas."""

    def test_todo_item_create_valid(self):
        """Test valid TodoItemCreate schema."""
        data = TodoItemCreate(text="Buy milk")
        assert data.text == "Buy milk"

    def test_todo_item_create_text_required(self):
        """Test that text is required."""
        with pytest.raises(ValidationError):
            TodoItemCreate()

    def test_todo_item_create_text_min_length(self):
        """Test minimum text length (1 character)."""
        with pytest.raises(ValidationError):
            TodoItemCreate(text="")

    def test_todo_item_create_text_max_length(self):
        """Test maximum text length (500 characters)."""
        with pytest.raises(ValidationError):
            TodoItemCreate(text="x" * 501)

    def test_todo_item_create_text_at_max_length(self):
        """Test text at exactly max length is valid."""
        data = TodoItemCreate(text="x" * 500)
        assert len(data.text) == 500

    def test_todo_item_update_completion_valid(self):
        """Test valid TodoItemUpdateCompletion schema."""
        data = TodoItemUpdateCompletion(completed=True)
        assert data.completed is True
        
        data = TodoItemUpdateCompletion(completed=False)
        assert data.completed is False

    def test_todo_item_update_completion_required(self):
        """Test that completed is required."""
        with pytest.raises(ValidationError):
            TodoItemUpdateCompletion()

    def test_todo_item_response_from_model(self, db_session):
        """Test TodoItemResponse can be created from model."""
        user = User(username="respuser", password_hash="hashedpassword")
        db_session.add(user)
        db_session.commit()
        
        todo = TodoItem(user_id=user.id, text="Response test", completed=True)
        db_session.add(todo)
        db_session.commit()
        
        response = TodoItemResponse.model_validate(todo)
        assert response.id == todo.id
        assert response.user_id == user.id
        assert response.text == "Response test"
        assert response.completed is True
        assert response.created_at is not None
