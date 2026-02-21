import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from app.api import router
from app.db import db_pool, init_db
from app.graph import builder
from app.settings import get_settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Initialize database pool
    logger.info("Initializing database pool...")
    await db_pool.connect()

    # Initialize database schema
    logger.info("Initializing databases...")
    await init_db()

    # Initialize async persistence
    logger.info("Initializing LangGraph checkpointer...")
    async with AsyncSqliteSaver.from_conn_string("chat_history.db") as checkpointer:
        # Compile graph with checkpointer
        app.state.graph = builder.compile(checkpointer=checkpointer)
        logger.info("MediAssistant backend started successfully")
        yield
        logger.info("Shutting down MediAssistant backend")

    # Cleanup
    await db_pool.close()


app = FastAPI(title="MediAssistant Chat Backend", lifespan=lifespan)

# Get settings
settings = get_settings()

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS with restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Only necessary methods
    allow_headers=["Content-Type", "Authorization"],
)


# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Add HSTS only in production
    if settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


app.include_router(router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
