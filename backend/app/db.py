"""Database operations with connection pooling."""

import asyncio
from contextlib import asynccontextmanager
import logging
from typing import List, Dict, Any, Optional

from google.cloud.sql.connector import Connector
import asyncpg

from app.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class DatabasePool:
    """Database connection pool manager exclusively using Google Cloud SQL (PostgreSQL)."""

    def __init__(self):
        # PG state
        self._pg_pool: Optional[asyncpg.Pool] = None
        # Cloud SQL Connector state
        self._connector: Optional[Connector] = None

    async def connect(self):
        """Initialize Cloud SQL PostgreSQL connection pool."""
        if not self._pg_pool:
            if not settings.CLOUD_SQL_CONNECTION_NAME:
                raise ValueError(
                    "CLOUD_SQL_CONNECTION_NAME must be set in the environment."
                )

            # Initialize Cloud SQL Connector
            # Bind the connector to the caller's running loop.
            self._connector = Connector(loop=asyncio.get_running_loop())

            async def get_async_conn(*args, **kwargs) -> asyncpg.Connection:
                kwargs.pop("loop", None)
                conn: asyncpg.Connection = await self._connector.connect_async(
                    settings.CLOUD_SQL_CONNECTION_NAME,
                    "asyncpg",
                    user=settings.DB_USER,
                    password=settings.DB_PASS,
                    db=settings.DB_NAME,
                    **kwargs,
                )
                return conn

            self._pg_pool = await asyncpg.create_pool(
                connect=get_async_conn,
            )
            logger.info(
                f"Cloud SQL PostgreSQL connection pool initialized: {settings.CLOUD_SQL_CONNECTION_NAME}"
            )

    async def close(self):
        """Close database connection."""
        if self._pg_pool:
            await self._pg_pool.close()
            self._pg_pool = None

        if self._connector:
            await self._connector.close_async()
            self._connector = None
        logger.info("Cloud SQL PostgreSQL connection pool closed")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        try:
            if not self._pg_pool:
                await self.connect()
            async with self._pg_pool.acquire() as conn:
                yield conn
        except Exception as e:
            logger.error(f"Database operation error: {e}", exc_info=True)
            raise


# Global database pool instance
db_pool = DatabasePool()


async def init_db():
    """Initialize database schema."""
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
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id ON user_threads(user_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_updated_at ON user_threads(updated_at DESC)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_updated ON user_threads(user_id, updated_at DESC)
            """)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise


async def save_thread(thread_id: str, user_id: str, title: str = "New Chat"):
    """Save or update a thread in the database."""
    try:
        async with db_pool.get_connection() as db:
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
                "UPDATE user_threads SET title = $1, updated_at = CURRENT_TIMESTAMP WHERE thread_id = $2",
                title,
                thread_id,
            )
    except Exception as e:
        logger.error(
            f"Error updating thread title for {thread_id}: {str(e)}", exc_info=True
        )
        raise


async def get_thread_by_id(thread_id: str) -> Dict[str, Any] | None:
    """Get a single thread by its ID."""
    try:
        async with db_pool.get_connection() as db:
            row = await db.fetchrow(
                "SELECT * FROM user_threads WHERE thread_id = $1", thread_id
            )
            return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def get_user_threads(user_id: str) -> List[Dict[str, Any]]:
    """List threads for user_id."""
    try:
        async with db_pool.get_connection() as db:
            rows = await db.fetch(
                "SELECT * FROM user_threads WHERE user_id = $1 ORDER BY updated_at DESC",
                user_id,
            )
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
            await db.execute("DELETE FROM user_threads WHERE thread_id = $1", thread_id)
            logger.info(f"Deleted thread {thread_id}")
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def delete_all_user_threads(user_id: str):
    """Delete all threads for a specific user from the database."""
    try:
        async with db_pool.get_connection() as db:
            await db.execute("DELETE FROM user_threads WHERE user_id = $1", user_id)
            logger.info(f"Deleted all threads for user {user_id}")
    except Exception as e:
        logger.error(
            f"Error deleting all threads for user {user_id}: {str(e)}", exc_info=True
        )
        raise
