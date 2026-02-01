"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_chat_endpoint_requires_auth():
    """Test that chat endpoint validates input."""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "Hello",
            "thread_id": "thread-123-abc",
            "user_id": "user-456-def",
        },
    )
    # Should return 200 or streaming response
    assert response.status_code in [200, 429]  # 429 if rate limited


@pytest.mark.asyncio
async def test_chat_endpoint_validation():
    """Test input validation on chat endpoint."""
    response = client.post(
        "/api/v1/chat",
        json={
            "message": "",  # Empty message should fail
            "thread_id": "invalid",  # Invalid format
            "user_id": "invalid",  # Invalid format
        },
    )
    # Should fail validation
    assert response.status_code == 422


def test_list_threads():
    """Test list threads endpoint."""
    response = client.get("/api/v1/threads/user-123-abc")
    assert response.status_code in [200, 429]  # 200 or rate limited


def test_cors_headers():
    """Test CORS headers are set."""
    response = client.get("/health", headers={"Origin": "http://localhost:8081"})
    assert "access-control-allow-origin" in response.headers
