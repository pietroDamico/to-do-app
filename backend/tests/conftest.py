"""
Pytest configuration and fixtures for testing.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """
    Test client fixture for making requests to the FastAPI app.
    """
    return TestClient(app)
