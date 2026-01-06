"""
Integration tests for the complete authentication flow.
Tests the end-to-end authentication journey from registration to protected resource access.
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.config import get_settings

settings = get_settings()


class TestAuthenticationFlow:
    """Integration tests for the complete authentication flow."""

    def test_register_login_access_protected_resource(self, client):
        """
        Test complete flow: register → login → access protected resource.
        This is the happy path for the entire authentication system.
        """
        # Step 1: Register a new user
        register_response = client.post(
            "/api/auth/register",
            json={"username": "flowuser", "password": "password123"}
        )
        assert register_response.status_code == 201
        registered_user = register_response.json()
        assert registered_user["username"] == "flowuser"
        
        # Step 2: Login with the registered credentials
        login_response = client.post(
            "/api/auth/login",
            json={"username": "flowuser", "password": "password123"}
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert "access_token" in login_data
        assert login_data["token_type"] == "bearer"
        assert login_data["user"]["username"] == "flowuser"
        
        token = login_data["access_token"]
        
        # Step 3: Access protected resource with the token
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["username"] == "flowuser"
        assert user_data["id"] == registered_user["id"]

    def test_register_then_login_immediately(self, client):
        """Test that a user can login immediately after registration."""
        # Register
        client.post(
            "/api/auth/register",
            json={"username": "quicklogin", "password": "password123"}
        )
        
        # Login immediately
        response = client.post(
            "/api/auth/login",
            json={"username": "quicklogin", "password": "password123"}
        )
        
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_multiple_users_isolation(self, client):
        """Test that multiple users have properly isolated sessions."""
        # Register two users
        client.post(
            "/api/auth/register",
            json={"username": "user_a", "password": "password123"}
        )
        client.post(
            "/api/auth/register",
            json={"username": "user_b", "password": "password456"}
        )
        
        # Login as user_a
        login_a = client.post(
            "/api/auth/login",
            json={"username": "user_a", "password": "password123"}
        )
        token_a = login_a.json()["access_token"]
        
        # Login as user_b
        login_b = client.post(
            "/api/auth/login",
            json={"username": "user_b", "password": "password456"}
        )
        token_b = login_b.json()["access_token"]
        
        # Each token should return the correct user
        me_a = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_a}"})
        me_b = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token_b}"})
        
        assert me_a.json()["username"] == "user_a"
        assert me_b.json()["username"] == "user_b"


class TestDuplicateRegistration:
    """Tests for duplicate username handling."""

    def test_duplicate_username_fails(self, client):
        """Test that registering with an existing username returns 409."""
        # First registration
        client.post(
            "/api/auth/register",
            json={"username": "duplicate", "password": "password123"}
        )
        
        # Attempt duplicate registration
        response = client.post(
            "/api/auth/register",
            json={"username": "duplicate", "password": "differentpassword"}
        )
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    def test_duplicate_username_case_insensitive(self, client):
        """Test that username uniqueness is case-insensitive."""
        # Register with lowercase
        client.post(
            "/api/auth/register",
            json={"username": "casetest", "password": "password123"}
        )
        
        # Attempt with different case
        response = client.post(
            "/api/auth/register",
            json={"username": "CaseTest", "password": "password456"}
        )
        
        assert response.status_code == 409


class TestInvalidCredentials:
    """Tests for invalid login credentials handling."""

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent username returns 401."""
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_wrong_password(self, client):
        """Test login with wrong password returns 401."""
        # Register user
        client.post(
            "/api/auth/register",
            json={"username": "wrongpass", "password": "correctpassword"}
        )
        
        # Login with wrong password
        response = client.post(
            "/api/auth/login",
            json={"username": "wrongpass", "password": "incorrectpassword"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_error_message_is_generic(self, client):
        """
        Test that error messages don't reveal whether username exists.
        Both invalid username and invalid password should return the same message.
        """
        # Register a user
        client.post(
            "/api/auth/register",
            json={"username": "generictest", "password": "password123"}
        )
        
        # Invalid username error
        invalid_user_response = client.post(
            "/api/auth/login",
            json={"username": "invalid_user", "password": "password123"}
        )
        
        # Invalid password error
        invalid_pass_response = client.post(
            "/api/auth/login",
            json={"username": "generictest", "password": "wrongpassword"}
        )
        
        # Both should have identical error messages
        assert invalid_user_response.json()["detail"] == invalid_pass_response.json()["detail"]


class TestProtectedEndpoints:
    """Tests for protected endpoint access control."""

    def test_protected_endpoint_without_token(self, client):
        """Test that protected endpoints require authentication."""
        response = client.get("/api/auth/me")
        
        # Should return 403 (Forbidden) when no auth header is present
        assert response.status_code == 403

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test that invalid tokens are rejected."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        
        assert response.status_code == 401

    def test_protected_endpoint_with_malformed_auth_header(self, client):
        """Test that malformed authorization headers are rejected."""
        # Missing "Bearer" prefix
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "invalid_token"}
        )
        
        assert response.status_code in [401, 403]

    def test_protected_endpoint_with_valid_token(self, client):
        """Test that valid tokens allow access to protected endpoints."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "validtoken", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "validtoken", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200


class TestTokenValidation:
    """Tests for JWT token validation."""

    def test_token_contains_correct_payload(self, client):
        """Test that JWT token contains user_id and username."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "payloadtest", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "payloadtest", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Decode and verify payload
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        assert "sub" in payload  # user_id
        assert "username" in payload
        assert payload["username"] == "payloadtest"
        assert "exp" in payload  # expiration

    def test_token_has_expiration(self, client):
        """Test that token has a valid expiration time set."""
        # Register and login
        client.post(
            "/api/auth/register",
            json={"username": "exptest", "password": "password123"}
        )
        login_response = client.post(
            "/api/auth/login",
            json={"username": "exptest", "password": "password123"}
        )
        token = login_response.json()["access_token"]
        
        # Decode and check expiration
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        
        # Expiration should be in the future
        assert exp_datetime > datetime.utcnow()

    def test_expired_token_rejected(self, client):
        """Test that expired tokens are rejected."""
        # Create an expired token manually
        expired_payload = {
            "sub": "1",
            "username": "expireduser",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(
            expired_payload, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401

    def test_token_with_wrong_signature_rejected(self, client):
        """Test that tokens signed with wrong key are rejected."""
        # Create a token with a different secret key
        fake_payload = {
            "sub": "1",
            "username": "fakeuser",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        fake_token = jwt.encode(
            fake_payload, 
            "wrong_secret_key", 
            algorithm=settings.ALGORITHM
        )
        
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {fake_token}"}
        )
        
        assert response.status_code == 401

    def test_multiple_logins_return_valid_tokens(self, client):
        """Test that each login returns a valid, usable token."""
        # Register
        client.post(
            "/api/auth/register",
            json={"username": "multilogin", "password": "password123"}
        )
        
        # Login multiple times
        token1 = client.post(
            "/api/auth/login",
            json={"username": "multilogin", "password": "password123"}
        ).json()["access_token"]
        
        token2 = client.post(
            "/api/auth/login",
            json={"username": "multilogin", "password": "password123"}
        ).json()["access_token"]
        
        # Both tokens should be valid and usable
        response1 = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token1}"}
        )
        response2 = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token2}"}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["username"] == "multilogin"
        assert response2.json()["username"] == "multilogin"


class TestUsernameHandling:
    """Tests for username validation and handling."""

    def test_login_is_case_insensitive(self, client):
        """Test that login username matching is case-insensitive."""
        # Register with lowercase
        client.post(
            "/api/auth/register",
            json={"username": "caseuser", "password": "password123"}
        )
        
        # Login with different cases
        response_upper = client.post(
            "/api/auth/login",
            json={"username": "CASEUSER", "password": "password123"}
        )
        response_mixed = client.post(
            "/api/auth/login",
            json={"username": "CaseUser", "password": "password123"}
        )
        
        assert response_upper.status_code == 200
        assert response_mixed.status_code == 200


class TestInputValidation:
    """Tests for input validation."""

    def test_username_too_short(self, client):
        """Test that username shorter than 3 characters is rejected."""
        response = client.post(
            "/api/auth/register",
            json={"username": "ab", "password": "password123"}
        )
        
        assert response.status_code == 422

    def test_username_too_long(self, client):
        """Test that username longer than 50 characters is rejected."""
        long_username = "a" * 51
        response = client.post(
            "/api/auth/register",
            json={"username": long_username, "password": "password123"}
        )
        
        assert response.status_code == 422

    def test_password_too_short(self, client):
        """Test that password shorter than 8 characters is rejected."""
        response = client.post(
            "/api/auth/register",
            json={"username": "shortpass", "password": "short"}
        )
        
        assert response.status_code == 422

    def test_username_with_invalid_characters(self, client):
        """Test that username with special characters is rejected."""
        response = client.post(
            "/api/auth/register",
            json={"username": "user@name!", "password": "password123"}
        )
        
        assert response.status_code == 422

    def test_missing_username(self, client):
        """Test that missing username is rejected."""
        response = client.post(
            "/api/auth/register",
            json={"password": "password123"}
        )
        
        assert response.status_code == 422

    def test_missing_password(self, client):
        """Test that missing password is rejected."""
        response = client.post(
            "/api/auth/register",
            json={"username": "missingpass"}
        )
        
        assert response.status_code == 422


class TestPasswordSecurity:
    """Tests for password security."""

    def test_password_not_stored_plaintext(self, client, db_session):
        """Test that password is hashed, not stored as plaintext."""
        from app.models.user import User
        
        password = "mySecretPassword123"
        client.post(
            "/api/auth/register",
            json={"username": "hashcheck", "password": password}
        )
        
        # Query the database directly
        user = db_session.query(User).filter(User.username == "hashcheck").first()
        
        # Password hash should not equal the plaintext password
        assert user.password_hash != password
        # Password hash should start with bcrypt identifier
        assert user.password_hash.startswith("$2")

    def test_password_never_returned_in_response(self, client):
        """Test that password/hash is never included in API responses."""
        # Registration response
        reg_response = client.post(
            "/api/auth/register",
            json={"username": "nopwdresp", "password": "password123"}
        )
        reg_data = reg_response.json()
        assert "password" not in reg_data
        assert "password_hash" not in reg_data
        
        # Login response
        login_response = client.post(
            "/api/auth/login",
            json={"username": "nopwdresp", "password": "password123"}
        )
        login_data = login_response.json()
        assert "password" not in login_data
        assert "password" not in login_data.get("user", {})
        
        # /me response
        token = login_data["access_token"]
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        me_data = me_response.json()
        assert "password" not in me_data
        assert "password_hash" not in me_data
