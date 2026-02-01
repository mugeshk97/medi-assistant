"""Test configuration and fixtures."""

import pytest
import asyncio
from app.db import init_db, db_pool


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db():
    """Initialize test database."""
    await init_db()
    await db_pool.connect()
    yield db_pool
    await db_pool.close()
