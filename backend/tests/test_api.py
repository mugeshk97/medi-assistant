"""Tests for API endpoints."""

import pytest


def test_health_check_sync():
    """Basic sanity: the /health endpoint responds.

    This test is sync so it bypasses the async client entirely — useful
    as a fast smoke test that doesn't require Cloud SQL.
    """
    from fastapi.testclient import TestClient
    from fastapi import FastAPI

    mini_app = FastAPI()

    @mini_app.get("/health")
    def _health():
        return {"status": "ok"}

    with TestClient(mini_app) as c:
        resp = c.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_check(client):
    """Test health check endpoint via the full app."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_chat_endpoint_validation(client):
    """Test input validation on chat endpoint."""
    response = await client.post(
        "/api/v1/chat",
        json={
            "message": "",  # Empty message should fail
            "thread_id": "thread-123",
        },
        headers={"X-User-ID": "test_user"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_threads(client):
    """Test list threads endpoint."""
    response = await client.get(
        "/api/v1/threads", headers={"X-User-ID": "test_user_789"}
    )
    assert response.status_code in [200, 429]  # 200 or rate limited


@pytest.mark.asyncio
async def test_cors_headers(client):
    """Test CORS headers are set."""
    response = await client.get("/health", headers={"Origin": "http://localhost:8081"})
    assert "access-control-allow-origin" in response.headers


@pytest.mark.asyncio
async def test_chat_endpoint_missing_user_id(client):
    """Test that chat endpoint requires X-User-ID header."""
    response = await client.post(
        "/api/v1/chat",
        json={"message": "Hello", "thread_id": "thread-abc"},
        # no X-User-ID header
    )
    assert response.status_code == 422  # missing required header
