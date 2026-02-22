"""Tests for database operations."""

import pytest
from app.db import save_thread, get_user_threads, get_thread_by_id, delete_thread


@pytest.mark.asyncio
async def test_save_and_get_thread(db):
    """Test saving and retrieving a thread."""
    thread_id = "test-thread-123"
    user_id = "test-user-456"
    title = "Test Thread"

    # Save thread
    await save_thread(thread_id, user_id, title)

    # Retrieve thread
    thread = await get_thread_by_id(thread_id)
    assert thread is not None
    assert thread["thread_id"] == thread_id
    assert thread["user_id"] == user_id
    assert thread["title"] == title


@pytest.mark.asyncio
async def test_get_user_threads(db):
    """Test getting all threads for a user."""
    import uuid

    user_id = f"test-user-{uuid.uuid4()}"
    thread1_id = f"thread-1-{uuid.uuid4()}"
    thread2_id = f"thread-2-{uuid.uuid4()}"

    # Create multiple threads
    await save_thread(thread1_id, user_id, "Thread 1")
    await save_thread(thread2_id, user_id, "Thread 2")

    # Get all threads
    threads = await get_user_threads(user_id)
    assert len(threads) >= 2


@pytest.mark.asyncio
async def test_delete_thread(db):
    """Test deleting a thread."""
    thread_id = "delete-test-thread"
    user_id = "delete-test-user"

    # Create thread
    await save_thread(thread_id, user_id, "To Delete")

    # Delete thread
    await delete_thread(thread_id)

    # Verify deletion
    thread = await get_thread_by_id(thread_id)
    assert thread is None


@pytest.mark.asyncio
async def test_thread_not_found(db):
    """Test retrieving non-existent thread."""
    thread = await get_thread_by_id("nonexistent-thread")
    assert thread is None
