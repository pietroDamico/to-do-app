"""
Tests for JWT authentication middleware/dependency.
"""
import pytest
from datetime import timedelta
from jose import jwt
from app.config import settings
from app.utils.security import create_access_token


class TestAuthMiddleware:
    """Tests for authentication middleware and protected endpoints."""

    def _get_auth_header(self, token: str) -> dict:
        """Helper to create Authorization header."""
        return {"Authorization": f"Bearer {token}"}

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

    def test_valid_token_returns_user(self, client):
        """Test that valid token returns user object in protected endpoint."""
        login_data = self._register_and_login(client)
        token = login_data["access_token"]
        
        response = client.get("/api/auth/me", headers=self._get_auth_header(token))
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert "id" in data

    def test_missing_auth_header_returns_401(self, client):
        """Test that missing Authorization header returns 401."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 403  # HTTPBearer returns 403 for missing token

    def test_invalid_token_format_returns_401(self, client):
        """Test that invalid token format returns 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid-token-format"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    def test_expired_token_returns_401(self, client):
        """Test that expired token returns 401."""
        # Register a user first
        login_data = self._register_and_login(client, username="expireduser")
        user_id = login_data["user"]["id"]
        
        # Create an expired token
        expired_token = create_access_token(
            data={"sub": str(user_id), "username": "expireduser"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        response = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(expired_token)
        )
        
        assert response.status_code == 401

    def test_token_with_invalid_signature_returns_401(self, client):
        """Test that token with invalid signature returns 401."""
        # Create token with wrong secret key
        token = jwt.encode(
            {"sub": "1", "username": "testuser"},
            "wrong-secret-key",
            algorithm="HS256"
        )
        
        response = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 401

    def test_token_with_missing_sub_claim_returns_401(self, client):
        """Test that token without 'sub' claim returns 401."""
        # Create token without sub claim
        token = jwt.encode(
            {"username": "testuser"},  # Missing 'sub'
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        response = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 401

    def test_token_for_nonexistent_user_returns_401(self, client, db_session):
        """Test that token for deleted/non-existent user returns 401."""
        # Create token for user_id that doesn't exist
        token = create_access_token(
            data={"sub": "99999", "username": "deleteduser"}
        )
        
        response = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 401

    def test_protected_endpoint_requires_authentication(self, client):
        """Test that protected endpoint requires valid authentication."""
        # Try to access without any auth
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # HTTPBearer returns 403 for missing

    def test_protected_endpoint_works_with_valid_token(self, client):
        """Test that protected endpoint works with valid token."""
        login_data = self._register_and_login(client, username="validuser")
        token = login_data["access_token"]
        
        response = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 200
        assert response.json()["username"] == "validuser"

    def test_me_endpoint_returns_correct_user_data(self, client):
        """Test that /me endpoint returns correct user data."""
        login_data = self._register_and_login(client, username="meuser")
        token = login_data["access_token"]
        user_id = login_data["user"]["id"]
        
        response = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(token)
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "meuser"
        assert "created_at" in data
        # Password should never be in response
        assert "password" not in data
        assert "password_hash" not in data

    def test_different_users_get_their_own_data(self, client):
        """Test that different users get their own data from /me."""
        # Create two users
        login1 = self._register_and_login(client, username="user1", password="password123")
        login2 = self._register_and_login(client, username="user2", password="password123")
        
        # Each user should get their own data
        response1 = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(login1["access_token"])
        )
        response2 = client.get(
            "/api/auth/me",
            headers=self._get_auth_header(login2["access_token"])
        )
        
        assert response1.json()["username"] == "user1"
        assert response2.json()["username"] == "user2"
        assert response1.json()["id"] != response2.json()["id"]

    def test_malformed_bearer_token_returns_401(self, client):
        """Test that malformed bearer token returns 401."""
        # Test various malformed tokens
        malformed_tokens = [
            "not-a-jwt",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",  # Incomplete JWT
        ]
        
        for token in malformed_tokens:
            response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert response.status_code == 401, f"Token '{token}' should return 401"

    def test_wrong_auth_scheme_returns_error(self, client):
        """Test that wrong authentication scheme returns error."""
        login_data = self._register_and_login(client, username="schemeuser")
        token = login_data["access_token"]
        
        # Use Basic instead of Bearer
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Basic {token}"}
        )
        
        # HTTPBearer rejects non-Bearer schemes
        assert response.status_code in [401, 403]
