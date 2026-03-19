# MediAssistant

> An intelligent medical assistant powered by LLM with built-in safety guardrails and quiz generation from PDFs.

## Overview

MediAssistant is a FastAPI backend service that provides:
- **AI-powered medical chat** using LangGraph and OpenAI
- **Safety guardrails** with LLM-based input validation to ensure medical relevance
- **Quiz generation** — upload a PDF and get a structured MCQ quiz
- **Thread management** with persistent history via Firestore
- **Real-time streaming** responses (token-by-token SSE)
- **Cloud-ready deployment** for Google Cloud Run

## Key Features

- **Medical AI Agent** — LangGraph state machine backed by GPT-4o-mini
- **Safety Guardrails** — LLM validates every message for medical relevance before routing to the agent
- **PDF Quiz Generator** — Upload any PDF, get back a structured multiple-choice quiz with explanations
- **Multi-thread Support** — Multiple independent conversations per user, with full history
- **Anonymous Sessions** — Simple `X-User-ID` header-based session isolation (no registration required)
- **Rate Limiting** — Per-IP limits on all endpoints (10–30 req/min)
- **Security Headers** — CORS, CSP, HSTS (production), X-Frame-Options, XSS Protection
- **GCP Native** — Firestore for state and thread metadata, Cloud Run for hosting

## Architecture

### LangGraph State Machine

```
User Input
    ↓
[guardrail_check] ← LLM validates medical relevance
    ↓
  {is_safe?}
  ├── Yes → [agent] → GPT-4o-mini → Stream tokens to client
  └── No  → [unsafe_input] → "Medical topics only" rejection
```

### Data Persistence

Two separate Firestore stores are used together:

| Store | Purpose |
|-------|---------|
| `user_threads` collection | Thread metadata (title, timestamps, user association) |
| LangGraph Firestore checkpointer | Full message history and agent state per thread |

Both are cleaned up on thread deletion.

## Project Structure

```
medi-assistant/
├── backend/
│   ├── app/
│   │   ├── api.py              # Chat & thread REST endpoints
│   │   ├── db.py               # Firestore thread metadata operations
│   │   ├── deps.py             # FastAPI dependencies (auth, graph)
│   │   ├── errors.py           # Custom exception hierarchy
│   │   ├── graph.py            # LangGraph agent definition
│   │   ├── guardrails.py       # LLM-based safety validation
│   │   ├── history.py          # Chat history serialization
│   │   ├── schema.py           # Pydantic request/response models
│   │   ├── settings.py         # Environment-driven configuration
│   │   └── quiz/
│   │       ├── router.py       # PDF upload & quiz generation endpoint
│   │       ├── generator.py    # LLM quiz generation logic
│   │       ├── ingest.py       # PDF text extraction
│   │       └── models.py       # Quiz Pydantic models
│   ├── tests/
│   │   ├── conftest.py         # Pytest fixtures
│   │   ├── test_api.py         # API endpoint tests
│   │   └── test_db.py          # Database tests
│   ├── main.py                 # Application entry point
│   ├── Dockerfile              # Multi-stage production build
│   └── pyproject.toml          # Dependencies & project config
├── MediAssistant.postman_collection.json
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.12+
- OpenAI API key **or** Azure OpenAI credentials
- Google Cloud project with Firestore enabled
- Application Default Credentials configured (`gcloud auth application-default login`)

### Installation

```bash
cd backend

# Install dependencies (using uv — recommended)
pip install uv
uv sync

# Or using pip
pip install -e .
```

### Configuration

Create a `backend/.env` file:

```bash
# API Key Authentication (optional but recommended)
# If set, all /api/* requests must include X-API-Key: <value>
API_KEY=your-secret-api-key-here

# OpenAI
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o-mini

# Google Cloud / Firestore (required)
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
FIRESTORE_DATABASE=(default)

# Application Settings
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
```

### Run the Server

```bash
cd backend
python main.py
```

Server endpoints:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health: `http://localhost:8000/health`

## API Reference

### Authentication

All `/api/*` endpoints require:

| Header | Required | Description |
|--------|----------|-------------|
| `X-API-Key` | If `API_KEY` env var is set | Authenticates the caller |
| `X-User-ID` | Always (chat endpoints) | Identifies the user session |

If `API_KEY` is not configured, the key check is skipped entirely.

---

### Chat Endpoints

All chat endpoints require an `X-User-ID: <your-user-id>` header.

#### Send a Message (Streaming)

```bash
POST /api/v1/chat
X-API-Key: your-secret-api-key-here
X-User-ID: user-123
Content-Type: application/json

{
  "thread_id": "thread-abc",
  "message": "What are the symptoms of the flu?"
}

# Response: text/event-stream (token-by-token)
```

Rate limit: **10 req/min**

#### List Threads

```bash
GET /api/v1/threads
X-User-ID: user-123

# Response:
[
  {
    "thread_id": "thread-abc",
    "title": "What are the symptoms of the flu?",
    "created_at": "2026-03-19T12:00:00"
  }
]
```

Rate limit: **30 req/min**

#### Get Chat History

```bash
GET /api/v1/history/{thread_id}
X-User-ID: user-123

# Response:
{
  "thread_id": "thread-abc",
  "messages": [
    {"role": "user", "content": "What are the symptoms of the flu?", "timestamp": "..."},
    {"role": "assistant", "content": "Common flu symptoms include...", "timestamp": "..."}
  ]
}
```

Rate limit: **30 req/min**

#### Delete a Thread

```bash
DELETE /api/v1/threads/{thread_id}
X-User-ID: user-123
```

Rate limit: **10 req/min**

#### Delete All Threads

```bash
DELETE /api/v1/threads
X-User-ID: user-123
```

Rate limit: **5 req/min**

---

### Quiz Generation

No authentication required.

#### Generate Quiz from PDF

```bash
POST /api/generate
Content-Type: multipart/form-data

pdf=<file.pdf>
num_questions=10          # optional, default 10
model=gpt-4o-mini         # optional
quiz_name=My Quiz         # optional

# Response:
{
  "title": "Introduction to Cardiology",
  "questions": [
    {
      "question": "Which chamber of the heart pumps blood to the lungs?",
      "options": [
        {"label": "A", "text": "Left ventricle"},
        {"label": "B", "text": "Right ventricle"},
        {"label": "C", "text": "Left atrium"},
        {"label": "D", "text": "Right atrium"}
      ],
      "correct_answer": "B",
      "explanation": "The right ventricle pumps deoxygenated blood to the lungs via the pulmonary artery.",
      "source_page": 4
    }
  ]
}
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | Static API key for `X-API-Key` header auth. Unset = auth disabled | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `MODEL_NAME` | OpenAI model to use | `gpt-4o-mini` |
| `GOOGLE_CLOUD_PROJECT` | GCP project ID (required) | — |
| `FIRESTORE_DATABASE` | Firestore database ID | `(default)` |
| `ENVIRONMENT` | `development` or `production` | `development` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `*` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` |

## Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific file
pytest tests/test_api.py -v
```

## Deployment

### Docker

```bash
cd backend

# Build image
docker build -t medi-assistant .

# Run container
docker run -d \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  -e GOOGLE_CLOUD_PROJECT=your-project \
  -e ENVIRONMENT=production \
  medi-assistant
```

### Google Cloud Run

```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/medi-assistant ./backend

# 2. Deploy to Cloud Run
gcloud run deploy medi-assistant \
  --image gcr.io/PROJECT_ID/medi-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=PROJECT_ID,ENVIRONMENT=production \
  --set-secrets OPENAI_API_KEY=openai-api-key:latest \
  --max-instances 10 \
  --memory 512Mi
```

## Security

- `X-User-ID` header isolates each user's threads — users can only access their own data
- Rate limiting on all endpoints (SlowAPI)
- Security headers on every response: `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy`
- HSTS enabled in production
- Non-root Docker container (`appuser`)
- Never commit `.env` — use GCP Secret Manager in production

## Disclaimer

MediAssistant is an informational tool and **not a replacement for professional medical care**. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.
