"""
Tests for to-do item CRUD endpoints.
"""
import pytest
from app.models.todo_item import TodoItem
from app.models.user import User


class TestTodosEndpoints:
    """Tests for /api/todos endpoints."""

    def _register_and_login(self, client, username="testuser", password="password123"):
        """Helper to register a user and get their token."""
        client.post(
            "/api/auth/register",
            json={"username": username, "password": password}
        )
        response = client.post(
            "/api/auth/login",
            json={"username": username, "password": password}
        )
        return response.json()

    def _get_auth_header(self, token: str) -> dict:
        """Helper to create Authorization header."""
        return {"Authorization": f"Bearer {token}"}


class TestCreateTodo(TestTodosEndpoints):
    """Tests for POST /api/todos endpoint (Issue #18)."""

    def test_authenticated_user_can_create_todo(self, client):
        """Test that authenticated user can create a todo item."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.post(
            "/api/todos/",
            json={"text": "Buy groceries"},
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["text"] == "Buy groceries"
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data

    def test_created_todo_has_correct_user_id(self, client):
        """Test that created todo has correct user_id."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        user_id = login_data["user"]["id"]
        
        response = client.post(
            "/api/todos/",
            json={"text": "Test todo"},
            headers=self._get_auth_header(token)
        )
        
        data = response.json()
        assert data["user_id"] == user_id

    def test_text_is_trimmed(self, client):
        """Test that text is trimmed (leading/trailing whitespace removed)."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.post(
            "/api/todos/",
            json={"text": "  Trimmed text  "},
            headers=self._get_auth_header(token)
        )
        
        data = response.json()
        assert data["text"] == "Trimmed text"

    def test_empty_text_returns_422(self, client):
        """Test that empty text returns validation error."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.post(
            "/api/todos/",
            json={"text": ""},
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 422

    def test_text_over_500_chars_returns_422(self, client):
        """Test that text over 500 chars returns validation error."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.post(
            "/api/todos/",
            json={"text": "x" * 501},
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 422

    def test_unauthenticated_request_returns_403(self, client):
        """Test that unauthenticated request returns 403."""
        response = client.post(
            "/api/todos/",
            json={"text": "Test todo"}
        )
        
        assert response.status_code == 403

    def test_created_todo_defaults_to_not_completed(self, client):
        """Test that created todo defaults to completed=false."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.post(
            "/api/todos/",
            json={"text": "New todo"},
            headers=self._get_auth_header(token)
        )
        
        data = response.json()
        assert data["completed"] is False

    def test_multiple_todos_can_be_created(self, client):
        """Test that multiple todos can be created by same user."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        for i in range(3):
            response = client.post(
                "/api/todos/",
                json={"text": f"Todo {i}"},
                headers=self._get_auth_header(token)
            )
            assert response.status_code == 201


class TestGetAllTodos(TestTodosEndpoints):
    """Tests for GET /api/todos endpoint (Issue #19)."""

    def test_authenticated_user_can_retrieve_todos(self, client):
        """Test that authenticated user can retrieve their todos."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create some todos
        for i in range(3):
            client.post(
                "/api/todos/",
                json={"text": f"Todo {i}"},
                headers=self._get_auth_header(token)
            )
        
        # Get todos
        response = client.get(
            "/api/todos/",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_todos_sorted_newest_first(self, client):
        """Test that todos are sorted newest first."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create todos in order
        texts = ["First", "Second", "Third"]
        for text in texts:
            client.post(
                "/api/todos/",
                json={"text": text},
                headers=self._get_auth_header(token)
            )
        
        # Get todos
        response = client.get(
            "/api/todos/",
            headers=self._get_auth_header(token)
        )
        
        data = response.json()
        # Newest should be first
        assert data[0]["text"] == "Third"
        assert data[2]["text"] == "First"

    def test_user_only_sees_their_own_todos(self, client):
        """Test that user only sees their own todos (data isolation)."""
        # Create user 1 with todos
        login1 = self._register_and_login(client, "user1")
        token1 = login1["access_token"]
        client.post(
            "/api/todos/",
            json={"text": "User 1 todo"},
            headers=self._get_auth_header(token1)
        )
        
        # Create user 2 with todos
        login2 = self._register_and_login(client, "user2")
        token2 = login2["access_token"]
        client.post(
            "/api/todos/",
            json={"text": "User 2 todo"},
            headers=self._get_auth_header(token2)
        )
        
        # User 1 should only see their todo
        response = client.get(
            "/api/todos/",
            headers=self._get_auth_header(token1)
        )
        data = response.json()
        assert len(data) == 1
        assert data[0]["text"] == "User 1 todo"

    def test_returns_empty_array_for_user_with_no_todos(self, client):
        """Test that returns empty array for user with no todos."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.get(
            "/api/todos/",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 200
        assert response.json() == []

    def test_unauthenticated_request_returns_403(self, client):
        """Test that unauthenticated request returns 403."""
        response = client.get("/api/todos/")
        assert response.status_code == 403


class TestUpdateTodoCompletion(TestTodosEndpoints):
    """Tests for PATCH /api/todos/{id} endpoint (Issue #20)."""

    def test_user_can_update_own_todo_completion(self, client):
        """Test that user can update their own todo completion status."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create a todo
        create_response = client.post(
            "/api/todos/",
            json={"text": "Test todo"},
            headers=self._get_auth_header(token)
        )
        todo_id = create_response.json()["id"]
        
        # Update completion status
        response = client.patch(
            f"/api/todos/{todo_id}",
            json={"completed": True},
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    def test_toggle_from_false_to_true(self, client):
        """Test toggle from false to true."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        create_response = client.post(
            "/api/todos/",
            json={"text": "Test todo"},
            headers=self._get_auth_header(token)
        )
        todo_id = create_response.json()["id"]
        
        response = client.patch(
            f"/api/todos/{todo_id}",
            json={"completed": True},
            headers=self._get_auth_header(token)
        )
        
        assert response.json()["completed"] is True

    def test_toggle_from_true_to_false(self, client):
        """Test toggle from true to false."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create and mark complete
        create_response = client.post(
            "/api/todos/",
            json={"text": "Test todo"},
            headers=self._get_auth_header(token)
        )
        todo_id = create_response.json()["id"]
        
        client.patch(
            f"/api/todos/{todo_id}",
            json={"completed": True},
            headers=self._get_auth_header(token)
        )
        
        # Now toggle back to false
        response = client.patch(
            f"/api/todos/{todo_id}",
            json={"completed": False},
            headers=self._get_auth_header(token)
        )
        
        assert response.json()["completed"] is False

    def test_404_for_nonexistent_todo(self, client):
        """Test 404 for non-existent todo ID."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.patch(
            "/api/todos/99999",
            json={"completed": True},
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo item not found"

    def test_403_when_updating_another_users_todo(self, client):
        """Test 403 when trying to update another user's todo."""
        # User 1 creates a todo
        login1 = self._register_and_login(client, "user1")
        token1 = login1["access_token"]
        create_response = client.post(
            "/api/todos/",
            json={"text": "User 1 todo"},
            headers=self._get_auth_header(token1)
        )
        todo_id = create_response.json()["id"]
        
        # User 2 tries to update it
        login2 = self._register_and_login(client, "user2")
        token2 = login2["access_token"]
        
        response = client.patch(
            f"/api/todos/{todo_id}",
            json={"completed": True},
            headers=self._get_auth_header(token2)
        )
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not authorized to update this item"

    def test_401_for_unauthenticated_request(self, client):
        """Test 403 for unauthenticated request."""
        response = client.patch(
            "/api/todos/1",
            json={"completed": True}
        )
        
        assert response.status_code == 403

    def test_text_and_other_fields_remain_unchanged(self, client):
        """Test that text and other fields remain unchanged after update."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        create_response = client.post(
            "/api/todos/",
            json={"text": "Original text"},
            headers=self._get_auth_header(token)
        )
        todo = create_response.json()
        todo_id = todo["id"]
        
        # Update completion
        response = client.patch(
            f"/api/todos/{todo_id}",
            json={"completed": True},
            headers=self._get_auth_header(token)
        )
        
        updated = response.json()
        assert updated["text"] == "Original text"
        assert updated["id"] == todo_id


class TestDeleteTodo(TestTodosEndpoints):
    """Tests for DELETE /api/todos/{id} endpoint (Issue #21)."""

    def test_user_can_delete_own_todo(self, client):
        """Test that user can delete their own todo."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create a todo
        create_response = client.post(
            "/api/todos/",
            json={"text": "To be deleted"},
            headers=self._get_auth_header(token)
        )
        todo_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(
            f"/api/todos/{todo_id}",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 204

    def test_deleted_todo_is_removed_from_database(self, client, db_session):
        """Test that deleted todo is removed from database."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create a todo
        create_response = client.post(
            "/api/todos/",
            json={"text": "To be deleted"},
            headers=self._get_auth_header(token)
        )
        todo_id = create_response.json()["id"]
        
        # Delete it
        client.delete(
            f"/api/todos/{todo_id}",
            headers=self._get_auth_header(token)
        )
        
        # Verify it's gone from database
        todo = db_session.query(TodoItem).filter(TodoItem.id == todo_id).first()
        assert todo is None

    def test_subsequent_get_returns_404(self, client):
        """Test that subsequent GET request for deleted todo returns 404."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create a todo
        create_response = client.post(
            "/api/todos/",
            json={"text": "To be deleted"},
            headers=self._get_auth_header(token)
        )
        todo_id = create_response.json()["id"]
        
        # Delete it
        client.delete(
            f"/api/todos/{todo_id}",
            headers=self._get_auth_header(token)
        )
        
        # Try to update deleted todo
        response = client.patch(
            f"/api/todos/{todo_id}",
            json={"completed": True},
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 404

    def test_404_for_nonexistent_todo(self, client):
        """Test 404 for non-existent todo ID."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.delete(
            "/api/todos/99999",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo item not found"

    def test_403_when_deleting_another_users_todo(self, client):
        """Test 403 when trying to delete another user's todo."""
        # User 1 creates a todo
        login1 = self._register_and_login(client, "user1")
        token1 = login1["access_token"]
        create_response = client.post(
            "/api/todos/",
            json={"text": "User 1 todo"},
            headers=self._get_auth_header(token1)
        )
        todo_id = create_response.json()["id"]
        
        # User 2 tries to delete it
        login2 = self._register_and_login(client, "user2")
        token2 = login2["access_token"]
        
        response = client.delete(
            f"/api/todos/{todo_id}",
            headers=self._get_auth_header(token2)
        )
        
        assert response.status_code == 403
        assert response.json()["detail"] == "Not authorized to delete this item"

    def test_401_for_unauthenticated_request(self, client):
        """Test 403 for unauthenticated request."""
        response = client.delete("/api/todos/1")
        assert response.status_code == 403

    def test_users_other_todos_remain_unaffected(self, client):
        """Test that user's other todos remain unaffected after deletion."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create multiple todos
        todo_ids = []
        for i in range(3):
            response = client.post(
                "/api/todos/",
                json={"text": f"Todo {i}"},
                headers=self._get_auth_header(token)
            )
            todo_ids.append(response.json()["id"])
        
        # Delete the middle one
        client.delete(
            f"/api/todos/{todo_ids[1]}",
            headers=self._get_auth_header(token)
        )
        
        # Get remaining todos
        response = client.get(
            "/api/todos/",
            headers=self._get_auth_header(token)
        )
        
        data = response.json()
        assert len(data) == 2
        remaining_ids = [t["id"] for t in data]
        assert todo_ids[0] in remaining_ids
        assert todo_ids[2] in remaining_ids
        assert todo_ids[1] not in remaining_ids

    def test_idempotency_deleting_already_deleted_returns_404(self, client):
        """Test that deleting already-deleted todo returns 404."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        # Create and delete a todo
        create_response = client.post(
            "/api/todos/",
            json={"text": "To be deleted"},
            headers=self._get_auth_header(token)
        )
        todo_id = create_response.json()["id"]
        
        client.delete(
            f"/api/todos/{todo_id}",
            headers=self._get_auth_header(token)
        )
        
        # Try to delete again
        response = client.delete(
            f"/api/todos/{todo_id}",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 404
