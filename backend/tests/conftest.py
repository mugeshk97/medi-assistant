"""Test configuration and fixtures."""

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.db import init_db, db


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def setup_db():
    """Connect to DB and initialise connection once for the whole test session."""
    await db.connect()
    await init_db()
    yield
    await db.close()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def db_instance(setup_db):
    """Yield the shared db for a single test."""
    yield db


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def client(setup_db):
    """Async HTTP client wrapping the full FastAPI app lifespan.

    Uses httpx.AsyncClient with ASGITransport so the app lifespan (including
    the Cloud SQL + LangGraph checkpointer setup) runs on the same asyncio
    session loop as the Cloud SQL Connector — avoiding ConnectorLoopError.
    """
    from main import app

    async with app.router.lifespan_context(app):
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            yield ac
