"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from main import app


# Create a test client using the with block to trigger the lifespan manager
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_chat_endpoint_works_without_auth(client):
    """Test that chat endpoint works without auth."""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "thread_id": "thread-123-abc",
        },
        headers={"X-User-ID": "test_user_789"},
    )
    # Should return 200 or streaming response
    assert response.status_code in [200, 429]  # 429 if rate limited


@pytest.mark.asyncio
async def test_chat_endpoint_validation(client):
    """Test input validation on chat endpoint."""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "",  # Empty message should fail
            "thread_id": "invalid",  # Invalid format
        },
        headers={"X-User-ID": "test_user"},
    )
    # Should fail validation
    assert response.status_code == 422


def test_list_threads(client):
    """Test list threads endpoint."""
    response = client.get("/api/v1/threads", headers={"X-User-ID": "test_user_789"})
    assert response.status_code in [200, 429]  # 200 or rate limited


def test_cors_headers(client):
    """Test CORS headers are set."""
    response = client.get("/health", headers={"Origin": "http://localhost:8081"})
    assert "access-control-allow-origin" in response.headers
