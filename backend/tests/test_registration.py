"""
Tests for user registration endpoint.
"""
import pytest
from app.models.user import User
from app.utils.security import verify_password


class TestRegistrationEndpoint:
    """Tests for POST /api/auth/register endpoint."""

    def test_successful_registration(self, client):
        """Test successful user registration returns 201 and user data."""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "password123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data
        assert "created_at" in data
        # Password should never be in response
        assert "password" not in data
        assert "password_hash" not in data

    def test_registration_creates_user_in_database(self, client, db_session):
        """Test that registration actually creates a user in the database."""
        response = client.post(
            "/api/auth/register",
            json={"username": "dbuser", "password": "password123"}
        )
        
        assert response.status_code == 201
        
        # Verify user exists in database
        user = db_session.query(User).filter(User.username == "dbuser").first()
        assert user is not None
        assert user.username == "dbuser"

    def test_password_is_hashed(self, client, db_session):
        """Test that password is stored as bcrypt hash, not plaintext."""
        password = "mySecurePassword123"
        response = client.post(
            "/api/auth/register",
            json={"username": "hashtest", "password": password}
        )
        
        assert response.status_code == 201
        
        # Get user from database
        user = db_session.query(User).filter(User.username == "hashtest").first()
        
        # Password should not be stored in plaintext
        assert user.password_hash != password
        
        # Password hash should be verifiable
        assert verify_password(password, user.password_hash) is True
        
        # Hash should be bcrypt format (starts with $2)
        assert user.password_hash.startswith("$2")

    def test_username_stored_lowercase(self, client, db_session):
        """Test that username is stored in lowercase."""
        response = client.post(
            "/api/auth/register",
            json={"username": "TestUser", "password": "password123"}
        )
        
        assert response.status_code == 201
        assert response.json()["username"] == "testuser"
        
        # Verify in database
        user = db_session.query(User).filter(User.username == "testuser").first()
        assert user is not None

    def test_duplicate_username_returns_409(self, client):
        """Test that registering with existing username returns 409."""
        # First registration
        client.post(
            "/api/auth/register",
            json={"username": "duplicate", "password": "password123"}
        )
        
        # Second registration with same username
        response = client.post(
            "/api/auth/register",
            json={"username": "duplicate", "password": "differentpassword"}
        )
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_username_case_insensitive_duplicate(self, client):
        """Test that username check is case-insensitive (John vs john)."""
        # First registration
        client.post(
            "/api/auth/register",
            json={"username": "john", "password": "password123"}
        )
        
        # Second registration with different case
        response = client.post(
            "/api/auth/register",
            json={"username": "JOHN", "password": "password123"}
        )
        
        assert response.status_code == 409

    def test_username_too_short_returns_422(self, client):
        """Test that username less than 3 characters returns validation error."""
        response = client.post(
            "/api/auth/register",
            json={"username": "ab", "password": "password123"}
        )
        
        assert response.status_code == 422

    def test_username_too_long_returns_422(self, client):
        """Test that username more than 50 characters returns validation error."""
        response = client.post(
            "/api/auth/register",
            json={"username": "a" * 51, "password": "password123"}
        )
        
        assert response.status_code == 422

    def test_username_invalid_characters_returns_422(self, client):
        """Test that username with invalid characters returns validation error."""
        response = client.post(
            "/api/auth/register",
            json={"username": "test@user", "password": "password123"}
        )
        
        assert response.status_code == 422

    def test_username_with_underscore_allowed(self, client):
        """Test that username with underscore is allowed."""
        response = client.post(
            "/api/auth/register",
            json={"username": "test_user", "password": "password123"}
        )
        
        assert response.status_code == 201
        assert response.json()["username"] == "test_user"

    def test_password_too_short_returns_422(self, client):
        """Test that password less than 8 characters returns validation error."""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser", "password": "short"}
        )
        
        assert response.status_code == 422

    def test_missing_username_returns_422(self, client):
        """Test that missing username returns validation error."""
        response = client.post(
            "/api/auth/register",
            json={"password": "password123"}
        )
        
        assert response.status_code == 422

    def test_missing_password_returns_422(self, client):
        """Test that missing password returns validation error."""
        response = client.post(
            "/api/auth/register",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client):
        """Test that empty request body returns validation error."""
        response = client.post("/api/auth/register", json={})
        
        assert response.status_code == 422

    def test_response_does_not_include_password(self, client):
        """Test that response never includes password or password_hash."""
        response = client.post(
            "/api/auth/register",
            json={"username": "nopassword", "password": "password123"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        # Check that no password-related fields are in response
        assert "password" not in data
        assert "password_hash" not in data
        assert "hashed_password" not in data

    def test_sql_injection_handled_safely(self, client):
        """Test that SQL injection attempts are handled safely."""
        # Try various SQL injection patterns
        injection_attempts = [
            "'; DROP TABLE users; --",
            "1; DELETE FROM users",
            "admin'--",
            "1 OR 1=1",
        ]
        
        for injection in injection_attempts:
            response = client.post(
                "/api/auth/register",
                json={"username": injection, "password": "password123"}
            )
            # Should either reject with 422 (invalid chars) or succeed without harm
            assert response.status_code in [201, 422]

    def test_multiple_users_can_register(self, client):
        """Test that multiple different users can register."""
        users = ["user1", "user2", "user3"]
        
        for username in users:
            response = client.post(
                "/api/auth/register",
                json={"username": username, "password": "password123"}
            )
            assert response.status_code == 201
            assert response.json()["username"] == username
