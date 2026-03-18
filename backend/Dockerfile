# Production-optimized multi-stage Dockerfile for GCP Cloud Run

# Stage 1: Builder - Install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim as builder

WORKDIR /app

# Enable bytecode compilation and specify path to venv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install system dependencies needed for compilation (like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency files first to maximize Docker layer cache
COPY pyproject.toml uv.lock* ./

# Install Python dependencies and create virtual environment using UV
RUN uv sync --frozen --no-dev --no-cache

# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim-bookworm

WORKDIR /app

# Install explicit runtime dependencies (PostgreSQL client libs without dev tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy the pre-built, compiled virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./main.py /app/main.py

# Switch to non-root user
USER appuser

# Configure environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Native Health check endpoint (doesn't require curl, saving space)
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Expose port (Cloud Run uses PORT environment variable dynamically)
EXPOSE 8000

# Run with Gunicorn using Uvicorn workers
CMD ["sh", "-c", "gunicorn main:app --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --timeout 120"]
