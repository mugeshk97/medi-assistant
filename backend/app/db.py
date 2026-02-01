"""Database operations with connection pooling."""

import aiosqlite
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

DB_NAME = "chat_history.db"


class DatabasePool:
    """Database connection pool manager."""

    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self._pool: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Initialize database connection."""
        if not self._pool:
            self._pool = await aiosqlite.connect(self.db_name, check_same_thread=False)
            logger.info(f"Database connection pool initialized: {self.db_name}")

    async def close(self):
        """Close database connection."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            logger.info("Database connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        if not self._pool:
            await self.connect()
        try:
            yield self._pool
        except Exception as e:
            logger.error(f"Database operation error: {e}", exc_info=True)
            raise


# Global database pool instance
db_pool = DatabasePool()


async def init_db():
    """Initialize database schema with connection pool."""
    try:
        async with db_pool.get_connection() as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_threads (
                    thread_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create indexes for better query performance
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id ON user_threads(user_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_updated_at ON user_threads(updated_at DESC)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_updated ON user_threads(user_id, updated_at DESC)
            """)
            await db.commit()
            logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise


async def save_thread(thread_id: str, user_id: str, title: str = "New Chat"):
    """Save or update a thread in the database."""
    try:
        async with db_pool.get_connection() as db:
            # Check if exists to avoid overwriting creation time (or upsert)
            async with db.execute(
                "SELECT 1 FROM user_threads WHERE thread_id = ?", (thread_id,)
            ) as cursor:
                if await cursor.fetchone():
                    # Update timestamp
                    await db.execute(
                        "UPDATE user_threads SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?",
                        (thread_id,),
                    )
                else:
                    await db.execute(
                        "INSERT INTO user_threads (thread_id, user_id, title) VALUES (?, ?, ?)",
                        (thread_id, user_id, title),
                    )
            await db.commit()
    except Exception as e:
        logger.error(f"Error saving thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def update_thread_title(thread_id: str, title: str):
    """
    Update the title of an existing thread.
    """
    try:
        async with db_pool.get_connection() as db:
            await db.execute(
                "UPDATE user_threads SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?",
                (title, thread_id),
            )
            await db.commit()
    except Exception as e:
        logger.error(
            f"Error updating thread title for {thread_id}: {str(e)}", exc_info=True
        )
        raise


async def get_thread_by_id(thread_id: str) -> Dict[str, Any] | None:
    """
    Get a single thread by its ID.

    Args:
        thread_id: ID of the thread to retrieve

    Returns:
        Thread dictionary or None if not found
    """
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_threads WHERE thread_id = ?",
                (thread_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def get_user_threads(user_id: str) -> List[Dict[str, Any]]:
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM user_threads WHERE user_id = ? ORDER BY updated_at DESC",
                (user_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    except Exception as e:
        logger.error(
            f"Error getting threads for user {user_id}: {str(e)}", exc_info=True
        )
        raise


async def delete_thread(thread_id: str):
    """
    Delete a thread from the database.
    """
    try:
        async with db_pool.get_connection() as db:
            await db.execute(
                "DELETE FROM user_threads WHERE thread_id = ?",
                (thread_id,),
            )
            await db.commit()
            logger.info(f"Deleted thread {thread_id}")
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {str(e)}", exc_info=True)
        raise
