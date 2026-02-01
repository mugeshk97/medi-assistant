"""User database operations for authentication."""

import aiosqlite
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import logging

from app.db import DB_NAME, db_pool

logger = logging.getLogger(__name__)


async def create_user(
    user_id: str, email: str, username: str, hashed_password: str
) -> None:
    """Create a new user in the database."""
    try:
        async with db_pool.get_connection() as db:
            await db.execute(
                """
                INSERT INTO users (id, email, username, hashed_password, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    email,
                    username,
                    hashed_password,
                    datetime.now(timezone.utc),
                    True,
                ),
            )
            await db.commit()
        logger.info(f"Created user: {username} ({email})")
    except aiosqlite.IntegrityError as e:
        logger.error(f"User creation failed - duplicate: {str(e)}")
        raise ValueError("Email or username already exists")
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email address."""
    try:
        async with db_pool.get_connection() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,),
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting user by email: {str(e)}", exc_info=True)
        return None


async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username."""
    try:
        async with db_pool.get_connection() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,),
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting user by username: {str(e)}", exc_info=True)
        return None


async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    try:
        async with db_pool.get_connection() as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}", exc_info=True)
        return None


async def init_users_table():
    """Initialize users table - call this in init_db."""
    try:
        async with aiosqlite.connect(DB_NAME) as db:
            # Create users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    hashed_password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)

            # Create indexes
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
            """)

            await db.commit()
        logger.info("Users table initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing users table: {str(e)}", exc_info=True)
        raise
