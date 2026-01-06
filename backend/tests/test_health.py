"""
Tests for health check endpoints.
"""
import pytest


def test_root_endpoint(client):
    """Test the root endpoint returns API status."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "message" in data
    assert "version" in data


def test_health_endpoint_returns_200(client):
    """Test the health endpoint returns 200 status code."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_structure(client):
    """Test the health endpoint returns expected structure."""
    response = client.get("/health")
    data = response.json()
    
    # Check overall status exists
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]
    
    # Check components structure
    assert "components" in data
    assert "api" in data["components"]
    assert "database" in data["components"]
    
    # Check API component
    assert "status" in data["components"]["api"]
    assert data["components"]["api"]["status"] == "healthy"
    
    # Check database component has required fields
    assert "status" in data["components"]["database"]
    assert "message" in data["components"]["database"]


def test_health_endpoint_api_always_healthy(client):
    """Test that the API component is always healthy if endpoint responds."""
    response = client.get("/health")
    data = response.json()
    
    # If we get a response, API component should be healthy
    assert data["components"]["api"]["status"] == "healthy"
