"""
Tests for User model and related functionality.
"""
import pytest
from pydantic import ValidationError

from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserInDB
from app.utils.security import hash_password, verify_password


class TestUserModel:
    """Tests for the User SQLAlchemy model."""

    def test_user_model_has_required_fields(self):
        """Test that User model has all required fields."""
        assert hasattr(User, 'id')
        assert hasattr(User, 'username')
        assert hasattr(User, 'password_hash')
        assert hasattr(User, 'created_at')
        assert hasattr(User, 'updated_at')

    def test_user_model_tablename(self):
        """Test that User model uses correct table name."""
        assert User.__tablename__ == 'users'

    def test_user_repr(self):
        """Test User model string representation."""
        user = User(id=1, username='testuser', password_hash='hash')
        assert 'testuser' in repr(user)
        assert '1' in repr(user)


class TestUserSchemas:
    """Tests for Pydantic User schemas."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user = UserCreate(username='testuser', password='password123')
        assert user.username == 'testuser'
        assert user.password == 'password123'

    def test_user_create_username_lowercase(self):
        """Test UserCreate converts username to lowercase."""
        user = UserCreate(username='TestUser', password='password123')
        assert user.username == 'testuser'

    def test_user_create_username_too_short(self):
        """Test UserCreate rejects username that is too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username='ab', password='password123')
        assert 'username' in str(exc_info.value).lower()

    def test_user_create_username_too_long(self):
        """Test UserCreate rejects username that is too long."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username='a' * 51, password='password123')
        assert 'username' in str(exc_info.value).lower()

    def test_user_create_username_invalid_characters(self):
        """Test UserCreate rejects username with invalid characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username='test@user', password='password123')
        assert 'alphanumeric' in str(exc_info.value).lower() or 'username' in str(exc_info.value).lower()

    def test_user_create_username_with_underscore(self):
        """Test UserCreate accepts username with underscore."""
        user = UserCreate(username='test_user', password='password123')
        assert user.username == 'test_user'

    def test_user_create_password_too_short(self):
        """Test UserCreate rejects password that is too short."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username='testuser', password='short')
        assert 'password' in str(exc_info.value).lower()

    def test_user_response_excludes_password(self):
        """Test UserResponse does not include password field."""
        # UserResponse should not have password_hash field
        assert 'password' not in UserResponse.model_fields
        assert 'password_hash' not in UserResponse.model_fields

    def test_user_in_db_includes_password_hash(self):
        """Test UserInDB includes password_hash field."""
        assert 'password_hash' in UserInDB.model_fields


class TestPasswordHashing:
    """Tests for password hashing utilities."""

    def test_hash_password_returns_hash(self):
        """Test that hash_password returns a hash."""
        password = 'testpassword123'
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) >= 60  # bcrypt hashes are at least 60 chars

    def test_hash_password_different_hashes(self):
        """Test that same password produces different hashes (salting)."""
        password = 'testpassword123'
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # Different salt each time

    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password."""
        password = 'testpassword123'
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password."""
        password = 'testpassword123'
        hashed = hash_password(password)
        assert verify_password('wrongpassword', hashed) is False

    def test_bcrypt_hash_format(self):
        """Test that hash is in bcrypt format."""
        password = 'testpassword123'
        hashed = hash_password(password)
        # bcrypt hashes start with $2b$ or $2a$
        assert hashed.startswith('$2') 
