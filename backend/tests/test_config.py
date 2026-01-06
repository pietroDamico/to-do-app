"""
Tests for configuration module.
"""
import pytest
from app.config import Settings, get_settings, settings


def test_settings_has_required_fields():
    """Test that settings has all required configuration fields."""
    assert hasattr(settings, 'DATABASE_URL')
    assert hasattr(settings, 'SECRET_KEY')
    assert hasattr(settings, 'ALGORITHM')
    assert hasattr(settings, 'ACCESS_TOKEN_EXPIRE_HOURS')
    assert hasattr(settings, 'CORS_ORIGINS')


def test_settings_default_values():
    """Test that settings has sensible default values."""
    # Create a new settings instance with defaults
    test_settings = Settings()
    
    assert test_settings.ALGORITHM == "HS256"
    assert test_settings.ACCESS_TOKEN_EXPIRE_HOURS == 24
    assert isinstance(test_settings.CORS_ORIGINS, list)


def test_get_settings_returns_settings_instance():
    """Test that get_settings returns a Settings instance."""
    result = get_settings()
    assert isinstance(result, Settings)


def test_get_settings_is_cached():
    """Test that get_settings returns the same cached instance."""
    result1 = get_settings()
    result2 = get_settings()
    assert result1 is result2
