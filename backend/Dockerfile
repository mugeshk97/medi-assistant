# Production-optimized multi-stage Dockerfile for GCP Cloud Run

# Stage 1: Builder - Install dependencies
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies needed for compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv==0.1.18

# Copy only dependency files first (for better caching)
COPY pyproject.toml uv.lock* ./

# Install Python dependencies to virtual environment
# This layer only rebuilds when dependencies change
RUN uv sync --frozen --no-dev --no-cache

# Stage 2: Runtime - Minimal production image
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies (PostgreSQL client libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser ./app /app/app
COPY --chown=appuser:appuser ./main.py /app/main.py

# Switch to non-root user
USER appuser

# Add virtual env to PATH
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE 8000

# Run with uvicorn (production ASGI server)
# Cloud Run will inject PORT environment variable dynamically
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1
