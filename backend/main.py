import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from app.api import router
from app.db import db_pool, init_db
from app.errors import MediAssistantError, ThreadNotFoundError, UnauthorizedError
from app.graph import builder
from app.settings import get_settings
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
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

    # Initialize async persistence based on driver
    logger.info("Initializing LangGraph checkpointer...")

    # Use langchain-google-cloud-sql-pg which natively handles the Cloud SQL
    # Connector, psycopg3, and LangGraph checkpointing in one cohesive API.
    from langchain_google_cloud_sql_pg import PostgresEngine
    from langchain_google_cloud_sql_pg import (
        PostgresSaver as CloudSQLPostgresSaver,
    )

    # CLOUD_SQL_CONNECTION_NAME is "project:region:instance"
    project_id, region, instance = settings.CLOUD_SQL_CONNECTION_NAME.split(":")

    # create_sync builds the engine using Cloud SQL IAM / user+password auth
    engine = await asyncio.to_thread(
        PostgresEngine.from_instance,
        project_id=project_id,
        region=region,
        instance=instance,
        database=settings.DB_NAME,
        user=settings.DB_USER,
        password=settings.DB_PASS,
    )

    # init_checkpoint_table creates LangGraph checkpoint tables if absent.
    # It does not use IF NOT EXISTS, so we catch DuplicateTable on restarts.
    try:
        await asyncio.to_thread(engine.init_checkpoint_table)
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            logger.info("LangGraph checkpoint tables already exist — skipping init")
        else:
            raise

    checkpointer = CloudSQLPostgresSaver.create_sync(engine)
    app.state.graph = builder.compile(checkpointer=checkpointer)
    logger.info(
        "MediAssistant started with Cloud SQL (langchain-google-cloud-sql-pg) checkpointer"
    )
    yield
    logger.info("Shutting down MediAssistant backend")
    await engine.close()

    # Cleanup
    await db_pool.close()


app = FastAPI(title="MediAssistant Chat Backend", lifespan=lifespan)

# Get settings
settings = get_settings()

# Configure rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(ThreadNotFoundError)
async def thread_not_found_handler(request: Request, exc: ThreadNotFoundError):
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError):
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(MediAssistantError)
async def medi_assistant_error_handler(request: Request, exc: MediAssistantError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# Enable CORS with restrictions
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins_list(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],  # Only necessary methods
    allow_headers=["Content-Type", "Authorization", "X-User-ID"],
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


# Serve the chat UI
STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/")
async def serve_ui():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def main():
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
