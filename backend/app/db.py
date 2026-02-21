"""Database operations with connection pooling."""

import aiosqlite
import asyncpg
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
import logging

from app.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class DatabasePool:
    """Database connection pool manager spanning SQLite and PostgreSQL."""

    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.is_postgres = self.db_url.startswith(
            "postgresql"
        ) or self.db_url.startswith("postgres")

        # SQLite state
        self._sqlite_pool: Optional[aiosqlite.Connection] = None
        # PG state
        self._pg_pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Initialize database connection based on configured driver."""
        if self.is_postgres:
            if not self._pg_pool:
                # asyncpg expects postgres:// or postgresql://
                self._pg_pool = await asyncpg.create_pool(dsn=self.db_url)
                logger.info("PostgreSQL connection pool initialized")
        else:
            if not self._sqlite_pool:
                # Parse out sqlite:/// scheme if present
                clean_db_name = self.db_url.replace("sqlite:///", "").replace(
                    "sqlite://", ""
                )
                self._sqlite_pool = await aiosqlite.connect(
                    clean_db_name, check_same_thread=False
                )
                # Enable row factory for dict-like access
                self._sqlite_pool.row_factory = aiosqlite.Row
                logger.info(f"SQLite connection pool initialized: {clean_db_name}")

    async def close(self):
        """Close database connection."""
        if self.is_postgres and self._pg_pool:
            await self._pg_pool.close()
            self._pg_pool = None
            logger.info("PostgreSQL connection pool closed")
        elif not self.is_postgres and self._sqlite_pool:
            await self._sqlite_pool.close()
            self._sqlite_pool = None
            logger.info("SQLite connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        try:
            if self.is_postgres:
                if not self._pg_pool:
                    await self.connect()
                async with self._pg_pool.acquire() as conn:
                    yield conn
            else:
                if not self._sqlite_pool:
                    await self.connect()
                yield self._sqlite_pool
        except Exception as e:
            logger.error(f"Database operation error: {e}", exc_info=True)
            raise


# Global database pool instance
db_pool = DatabasePool()


async def init_db():
    """Initialize database schema."""
    try:
        async with db_pool.get_connection() as db:
            if db_pool.is_postgres:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_threads (
                        thread_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_id ON user_threads(user_id)
                """)
                await db.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_updated ON user_threads(user_id, updated_at DESC)
                """)
            else:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS user_threads (
                        thread_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
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
            if db_pool.is_postgres:
                # Postgres UPSERT
                await db.execute(
                    """
                    INSERT INTO user_threads (thread_id, user_id, title) 
                    VALUES ($1, $2, $3)
                    ON CONFLICT (thread_id) DO UPDATE 
                    SET updated_at = CURRENT_TIMESTAMP
                    """,
                    thread_id,
                    user_id,
                    title,
                )
            else:
                # SQLite fallback
                async with db.execute(
                    "SELECT 1 FROM user_threads WHERE thread_id = ?", (thread_id,)
                ) as cursor:
                    if await cursor.fetchone():
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
            if db_pool.is_postgres:
                await db.execute(
                    "UPDATE user_threads SET title = $1, updated_at = CURRENT_TIMESTAMP WHERE thread_id = $2",
                    title,
                    thread_id,
                )
            else:
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
    """Get a single thread by its ID."""
    try:
        async with db_pool.get_connection() as db:
            if db_pool.is_postgres:
                row = await db.fetchrow(
                    "SELECT * FROM user_threads WHERE thread_id = $1", thread_id
                )
                return dict(row) if row else None
            else:
                async with db.execute(
                    "SELECT * FROM user_threads WHERE thread_id = ?", (thread_id,)
                ) as cursor:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def get_user_threads(user_id: str) -> List[Dict[str, Any]]:
    """List threads for user_id."""
    try:
        async with db_pool.get_connection() as db:
            if db_pool.is_postgres:
                rows = await db.fetch(
                    "SELECT * FROM user_threads WHERE user_id = $1 ORDER BY updated_at DESC",
                    user_id,
                )
                return [dict(row) for row in rows]
            else:
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
    """Delete a thread from the database."""
    try:
        async with db_pool.get_connection() as db:
            if db_pool.is_postgres:
                await db.execute(
                    "DELETE FROM user_threads WHERE thread_id = $1", thread_id
                )
            else:
                await db.execute(
                    "DELETE FROM user_threads WHERE thread_id = ?", (thread_id,)
                )
                await db.commit()
            logger.info(f"Deleted thread {thread_id}")
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def delete_all_user_threads(user_id: str):
    """Delete all threads for a specific user from the database."""
    try:
        async with db_pool.get_connection() as db:
            if db_pool.is_postgres:
                await db.execute("DELETE FROM user_threads WHERE user_id = $1", user_id)
            else:
                await db.execute(
                    "DELETE FROM user_threads WHERE user_id = ?", (user_id,)
                )
                await db.commit()
            logger.info(f"Deleted all threads for user {user_id}")
    except Exception as e:
        logger.error(
            f"Error deleting all threads for user {user_id}: {str(e)}", exc_info=True
        )
        raise
