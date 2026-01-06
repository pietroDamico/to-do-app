"""
Tests for user login endpoint.
"""
import pytest
from jose import jwt
from app.config import settings


class TestLoginEndpoint:
    """Tests for POST /api/auth/login endpoint."""

    def test_successful_login_returns_token(self, client):
        """Test successful login returns 200 and JWT token."""
        # First register a user
        client.post(
            "/api/auth/register",
            json={"username": "loginuser", "password": "password123"}
        )
        
        # Then login
        response = client.post(
            "/api/auth/login",
            json={"username": "loginuser", "password": "password123"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "loginuser"

    def test_token_payload_contains_user_info(self, client):
        """Test that JWT token payload contains correct user_id and username."""
        # Register user
        reg_response = client.post(
            "/api/auth/register",
            json={"username": "payloaduser", "password": "password123"}
        )
        user_id = reg_response.json()["id"]
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={"username": "payloaduser", "password": "password123"}
        )
        
        token = response.json()["access_token"]
        
        # Decode token without verification to check payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["sub"] == str(user_id)
        assert payload["username"] == "payloaduser"

    def test_token_can_be_decoded_with_secret_key(self, client):
        """Test that token can be decoded with SECRET_KEY."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "decodeuser", "password": "password123"}
        )
        
        response = client.post(
            "/api/auth/login",
            json={"username": "decodeuser", "password": "password123"}
        )
        
        token = response.json()["access_token"]
        
        # This should not raise an exception
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "sub" in payload
        assert "username" in payload

    def test_token_has_expiration_time(self, client):
        """Test that JWT token has expiration time set."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "expireuser", "password": "password123"}
        )
        
        response = client.post(
            "/api/auth/login",
            json={"username": "expireuser", "password": "password123"}
        )
        
        token = response.json()["access_token"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert "exp" in payload
        assert payload["exp"] is not None

    def test_invalid_username_returns_401(self, client):
        """Test that non-existent username returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_invalid_password_returns_401(self, client):
        """Test that wrong password returns 401."""
        # Register user
        client.post(
            "/api/auth/register",
            json={"username": "wrongpass", "password": "password123"}
        )
        
        # Login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"username": "wrongpass", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_error_message_generic_for_username_and_password(self, client):
        """Test that error message doesn't reveal if username exists."""
        # Register a user
        client.post(
            "/api/auth/register",
            json={"username": "realuser", "password": "password123"}
        )
        
        # Try login with non-existent username
        response1 = client.post(
            "/api/auth/login",
            json={"username": "fakeuser", "password": "password123"}
        )
        
        # Try login with wrong password
        response2 = client.post(
            "/api/auth/login",
            json={"username": "realuser", "password": "wrongpassword"}
        )
        
        # Both should have same generic error message
        assert response1.json()["detail"] == response2.json()["detail"]
        assert response1.json()["detail"] == "Invalid credentials"

    def test_login_is_case_insensitive(self, client):
        """Test that login works regardless of username case."""
        # Register with lowercase
        client.post(
            "/api/auth/register",
            json={"username": "caseuser", "password": "password123"}
        )
        
        # Login with different cases
        response1 = client.post(
            "/api/auth/login",
            json={"username": "CASEUSER", "password": "password123"}
        )
        
        response2 = client.post(
            "/api/auth/login",
            json={"username": "CaseUser", "password": "password123"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200

    def test_multiple_logins_generate_different_tokens(self, client):
        """Test that multiple logins generate different tokens."""
        # Register
        client.post(
            "/api/auth/register",
            json={"username": "multilogin", "password": "password123"}
        )
        
        # Login twice
        response1 = client.post(
            "/api/auth/login",
            json={"username": "multilogin", "password": "password123"}
        )
        
        response2 = client.post(
            "/api/auth/login",
            json={"username": "multilogin", "password": "password123"}
        )
        
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        
        # Tokens should be different (different exp times)
        assert token1 != token2

    def test_login_response_contains_user_info(self, client):
        """Test that login response contains user id and username."""
        # Register
        reg_response = client.post(
            "/api/auth/register",
            json={"username": "infouser", "password": "password123"}
        )
        user_id = reg_response.json()["id"]
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={"username": "infouser", "password": "password123"}
        )
        
        data = response.json()
        assert data["user"]["id"] == user_id
        assert data["user"]["username"] == "infouser"

    def test_missing_username_returns_422(self, client):
        """Test that missing username returns validation error."""
        response = client.post(
            "/api/auth/login",
            json={"password": "password123"}
        )
        
        assert response.status_code == 422

    def test_missing_password_returns_422(self, client):
        """Test that missing password returns validation error."""
        response = client.post(
            "/api/auth/login",
            json={"username": "testuser"}
        )
        
        assert response.status_code == 422

    def test_empty_body_returns_422(self, client):
        """Test that empty request body returns validation error."""
        response = client.post("/api/auth/login", json={})
        
        assert response.status_code == 422

    def test_response_does_not_include_password(self, client):
        """Test that login response never includes password."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "nopassresp", "password": "password123"}
        )
        
        response = client.post(
            "/api/auth/login",
            json={"username": "nopassresp", "password": "password123"}
        )
        
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
        assert "password" not in data.get("user", {})
