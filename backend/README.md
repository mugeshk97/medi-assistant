# MediAssistant Backend

> FastAPI backend service with LangGraph AI agent, safety guardrails, and JWT authentication.

## 📋 Overview

The MediAssistant backend is a production-ready FastAPI application that provides:
- **AI-powered chat** using LangGraph state machine and OpenAI GPT-4o-mini
- **Safety guardrails** with LLM-based input validation
- **JWT authentication** for secure user sessions
- **Real-time streaming** responses for better UX
- **Rate limiting** to prevent abuse
- **Cloud-ready deployment** for GCP Cloud Run

## ✨ Features

- 🤖 **LangGraph Agent** - State-based AI orchestration
- 🛡️ **Input Guardrails** - Medical domain validation
- 💾 **Persistent Storage** - SQLite/PostgreSQL with async support
- 🔐 **JWT Auth** - Secure token-based authentication
- 🚦 **Rate Limiting** - 10-30 req/min per IP
- ⚡ **Streaming Responses** - Token-by-token generation
- 📊 **Thread Management** - Multi-conversation support
- 🔒 **Security Headers** - CORS, CSP, HSTS, X-Frame-Options
- 🐳 **Docker Ready** - Multi-stage production builds
- ☁️ **Cloud Optimized** - GCP Secret Manager, Cloud SQL, Logging

## 🏗️ Architecture

### LangGraph State Machine

```
User Input
    ↓
[guardrail_check] ← Validates medical relevance
    ↓
  {is_safe?}
    ↓
  Yes → [agent] → LLM Response → Stream to client
    ↓
  No → [unsafe_input] → "Medical topics only" message
```

### Project Structure

```
backend/
├── app/
│   ├── api.py              # Chat & thread endpoints
│   ├── auth_api.py         # Authentication (register/login)
│   ├── auth.py             # JWT & password utilities
│   ├── db.py               # Thread database operations
│   ├── user_db.py          # User database operations
│   ├── graph.py            # LangGraph AI agent definition
│   ├── guardrails.py       # Input/output safety validation
│   ├── schema.py           # Pydantic request/response models
│   ├── settings.py         # Configuration & environment
│   ├── deps.py             # FastAPI dependencies
│   ├── errors.py           # Custom exceptions
│   └── history.py          # Chat history serialization
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_api.py         # API endpoint tests
│   └── test_db.py          # Database tests
├── main.py                 # Application entry point
├── Dockerfile              # Multi-stage production build
├── pyproject.toml          # Dependencies & project config
├── pytest.ini              # Pytest configuration
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key
- (Optional) Docker for containerized deployment

### Installation

```bash
# 1. Navigate to backend directory
cd backend

# 2. Install dependencies (using uv - recommended)
pip install uv
uv sync

# Alternative: using pip
pip install -e .

# For development dependencies
uv sync --all-extras
# Or: pip install -e ".[dev]"
```

### Configuration

Create a `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o-mini

# Application Settings
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:8081,exp://192.168.1.100:8081
LOG_LEVEL=INFO

# Security
RATE_LIMIT_ENABLED=true
SECRET_KEY=your-secret-key-for-jwt  # Generate with: openssl rand -hex 32

# Database (optional, defaults to SQLite)
# DATABASE_URL=postgresql+asyncpg://user:pass@host/db
```

### Run the Server

```bash
# Development (with hot-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will start at:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs` (Swagger UI)
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## 📚 API Endpoints

### Authentication

#### Register
```bash
POST /api/v1/register
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password123"
}

Response: {
  "id": "user-uuid",
  "username": "user@example.com"
}
```

#### Login
```bash
POST /api/v1/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secure_password123

Response: {
  "access_token": "eyJ0eXAiOiJKV1...",
  "token_type": "bearer"
}
```

### Chat Endpoints

All chat endpoints require `Authorization: Bearer <token>` header.

#### Send Message (Streaming)
```bash
POST /api/v1/chat
Authorization: Bearer <token>
Content-Type: application/json

{
  "thread_id": "thread-123",
  "message": "What are the symptoms of flu?"
}

Response: text/event-stream (streaming)
```

**Rate Limit:** 10 requests/minute

#### List Threads
```bash
GET /api/v1/threads
Authorization: Bearer <token>

Response: [
  {
    "thread_id": "thread-123",
    "title": "What are the symptoms of flu?",
    "created_at": "2026-02-02T12:00:00"
  }
]
```

**Rate Limit:** 30 requests/minute

#### Get Chat History
```bash
GET /api/v1/history/{thread_id}
Authorization: Bearer <token>

Response: {
  "thread_id": "thread-123",
  "messages": [
    {
      "role": "user",
      "content": "What are the symptoms of flu?",
      "timestamp": "2026-02-02T12:00:00"
    },
    {
      "role": "assistant",
      "content": "Common flu symptoms include...",
      "timestamp": "2026-02-02T12:00:05"
    }
  ]
}
```

**Rate Limit:** 30 requests/minute

#### Delete Thread
```bash
DELETE /api/v1/threads/{thread_id}
Authorization: Bearer <token>

Response: {
  "status": "success",
  "message": "Thread thread-123 deleted"
}
```

**Rate Limit:** 10 requests/minute

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v

# Run with detailed output
pytest -vv -s

# Run only specific test
pytest tests/test_api.py::test_chat_endpoint -v
```

Coverage report will be generated in `htmlcov/index.html`.

## 🏗️ Development

### Code Formatting & Linting

```bash
# Format code with Black
black app tests

# Lint with Ruff
ruff check app tests

# Type checking with mypy
mypy app
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `MODEL_NAME` | OpenAI model to use | `gpt-4o-mini` |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` |
| `SECRET_KEY` | JWT secret key | Auto-generated |
| `CLOUD_SQL_CONNECTION_NAME` | Cloud SQL instance | `project:region:instance` |

### Database

**SQLite (Development):**
**PostgreSQL (Production):**
```bash
# Set Cloud SQL credentials
export CLOUD_SQL_CONNECTION_NAME="project:region:instance"
export DB_USER="postgres"
export DB_PASS="password"
export DB_NAME="mediassistant"
```

## 🐳 Docker Deployment

### Development

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

### Production

```bash
# Build production image
docker build -t medi-assistant-backend .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e ENVIRONMENT=production \
  --name medi-assistant \
  medi-assistant-backend

# Using docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

## ☁️ Cloud Deployment (GCP)

### Google Cloud Run

```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/medi-assistant

# 2. Deploy to Cloud Run
gcloud run deploy medi-assistant \
  --image gcr.io/PROJECT_ID/medi-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=projects/PROJECT_ID/secrets/openai-key/versions/latest \
  --set-env-vars ENVIRONMENT=production \
  --max-instances 10 \
  --memory 512Mi \
  --cpu 1

# 3. Get service URL
gcloud run services describe medi-assistant --region us-central1 --format 'value(status.url)'
```

### Cloud SQL (PostgreSQL)

```bash
# 1. Create PostgreSQL instance
gcloud sql instances create medi-assistant-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# 2. Create database
gcloud sql databases create mediassistant --instance=medi-assistant-db

# 3. Set connection in Cloud Run
gcloud run services update medi-assistant \
  --add-cloudsql-instances PROJECT_ID:us-central1:medi-assistant-db \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME="PROJECT_ID:us-central1:medi-assistant-db" \
  --set-env-vars DB_USER="postgres" \
  --set-env-vars DB_PASS="your-secure-password" \
  --set-env-vars DB_NAME="mediassistant"
```

## 🔐 Security Best Practices

1. **Never commit `.env` files** - Use Secret Manager in production
2. **Rotate JWT secret keys** regularly
3. **Use HTTPS** in production (Cloud Run provides this automatically)
4. **Enable HSTS** in production (automatically enabled)
5. **Monitor rate limits** and adjust as needed
6. **Review logs** for suspicious activity
7. **Keep dependencies updated** - Run `uv sync` or `pip install -U` regularly

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Locked (SQLite)
```bash
# Remove lock file
rm chat_history.db-shm chat_history.db-wal

# Or use a new database
mv chat_history.db chat_history.db.backup
```

### OpenAI API Errors
- Verify API key is correct
- Check rate limits on OpenAI dashboard
- Ensure billing is active

### Import Errors
```bash
# Reinstall dependencies
rm -rf .venv
uv sync

# Or clear pip cache
pip cache purge
pip install -e . --force-reinstall
```

## 📊 Performance

- **Response Time**: ~2-5s for streaming start (depends on OpenAI)
- **Throughput**: ~100 req/s (with rate limiting disabled)
- **Memory**: ~150MB base + ~50MB per active connection
- **Startup**: ~2-3 seconds

## 🔄 Future Enhancements

- [ ] Database migrations (Alembic)
- [ ] Caching layer (Redis)
- [ ] Observability (Prometheus metrics)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Background tasks (Celery)
- [ ] WebSocket support
- [ ] Multi-language support
- [ ] Admin dashboard

## 📄 License

[Add your license here]

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/medi-assistant/issues)
- **Main Docs**: [../README.md](../README.md)
- **API Docs**: http://localhost:8000/docs

---

**Part of the MediAssistant project** • [Main README](../README.md) • [Mobile README](../mobile/README.md)
