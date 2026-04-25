"""Database operations with Firestore."""

import logging
from typing import List, Dict, Any, Optional

from google.cloud import firestore_v1
from google.cloud.firestore_v1.base_query import FieldFilter

from app.settings import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()


class Database:
    """Database connection manager for Google Cloud Firestore."""

    def __init__(self):
        self._client: Optional[firestore_v1.AsyncClient] = None

    async def connect(self):
        """Initialize Firestore AsyncClient."""
        if not self._client:
            try:
                # Initialize client. It will automatically use GOOGLE_APPLICATION_CREDENTIALS
                # or the default service account if deployed on GCP.
                kwargs = {"database": settings.FIRESTORE_DATABASE}
                if settings.GOOGLE_CLOUD_PROJECT:
                    kwargs["project"] = settings.GOOGLE_CLOUD_PROJECT
                self._client = firestore_v1.AsyncClient(**kwargs)
                logger.info("Firestore client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing Firestore client: {e}", exc_info=True)
                raise

    async def close(self):
        """Close Firestore connection."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("Firestore client closed")

    @property
    def client(self) -> firestore_v1.AsyncClient:
        """Get the Firestore client."""
        if not self._client:
            raise RuntimeError(
                "Firestore client is not initialized. Call connect() first."
            )
        return self._client


# Global database instance
db = Database()


async def init_db():
    """Initialize database schema/connection."""
    # Firestore is schema-less, so we just ensure we can connect.
    try:
        await db.connect()
        logger.info("Database initialized successfully (Firestore)")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}", exc_info=True)
        raise


async def save_thread(thread_id: str, user_id: str, title: str | None = None):
    """Save or update a thread in the database.

    On first message, pass title to set it. On subsequent messages, omit title
    so the existing title is not overwritten.
    """
    try:
        doc_ref = db.client.collection("user_threads").document(thread_id)
        data: dict = {
            "thread_id": thread_id,
            "user_id": user_id,
            "updated_at": firestore_v1.SERVER_TIMESTAMP,
        }
        if title is not None:
            data["title"] = title
        await doc_ref.set(data, merge=True)
    except Exception as e:
        logger.error(f"Error saving thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def update_thread_title(thread_id: str, title: str):
    """
    Update the title of an existing thread.
    """
    try:
        doc_ref = db.client.collection("user_threads").document(thread_id)
        await doc_ref.update(
            {
                "title": title,
                "updated_at": firestore_v1.SERVER_TIMESTAMP,
            }
        )
    except Exception as e:
        logger.error(
            f"Error updating thread title for {thread_id}: {str(e)}", exc_info=True
        )
        raise


async def get_thread_by_id(thread_id: str) -> Dict[str, Any] | None:
    """Get a single thread by its ID."""
    try:
        doc_ref = db.client.collection("user_threads").document(thread_id)
        doc = await doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error(f"Error getting thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def get_user_threads(user_id: str) -> List[Dict[str, Any]]:
    """List threads for user_id."""
    try:
        threads_ref = db.client.collection("user_threads")
        query = threads_ref.where(
            filter=FieldFilter("user_id", "==", user_id)
        ).order_by("updated_at", direction=firestore_v1.Query.DESCENDING)
        docs = query.stream()
        return [doc.to_dict() async for doc in docs]
    except Exception as e:
        logger.error(
            f"Error getting threads for user {user_id}: {str(e)}", exc_info=True
        )
        raise


async def delete_thread(thread_id: str):
    """Delete a thread from the database."""
    try:
        doc_ref = db.client.collection("user_threads").document(thread_id)
        await doc_ref.delete()
        logger.info(f"Deleted thread {thread_id}")
    except Exception as e:
        logger.error(f"Error deleting thread {thread_id}: {str(e)}", exc_info=True)
        raise


async def delete_all_user_threads(user_id: str):
    """Delete all threads for a specific user from the database."""
    try:
        threads_ref = db.client.collection("user_threads")
        query = threads_ref.where(filter=FieldFilter("user_id", "==", user_id))
        docs = query.stream()

        # Batch deletion
        batch = db.client.batch()
        count = 0
        async for doc in docs:
            batch.delete(doc.reference)
            count += 1
            # Firestore batches are limited to 500 operations
            if count >= 500:
                await batch.commit()
                batch = db.client.batch()
                count = 0

        if count > 0:
            await batch.commit()

        logger.info(f"Deleted all threads for user {user_id}")
    except Exception as e:
        logger.error(
            f"Error deleting all threads for user {user_id}: {str(e)}", exc_info=True
        )
        raise
