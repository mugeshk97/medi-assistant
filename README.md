# MediAssistant

> An intelligent medical assistant powered by GPT-4o-mini with built-in safety guardrails and cross-platform mobile support.

## 📋 Overview

MediAssistant is a production-ready, full-stack medical chatbot application that combines:
- **AI-powered conversational agent** using LangGraph and OpenAI
- **Safety-first design** with input/output validation guardrails
- **Cross-platform mobile app** (iOS, Android, Web) built with React Native + Expo
- **Enterprise security** features including strict header validation and rate limiting
- **Cloud-ready deployment** optimized for Google Cloud Run

## ✨ Key Features

- 🤖 **Medical AI Agent** - GPT-4o-mini trained for healthcare queries
- 🛡️ **Safety Guardrails** - LLM-based input validation to ensure medical relevance
- 💬 **Thread Management** - Multi-conversation support with persistent history
- ⚡ **Real-time Streaming** - Token-by-token response streaming
- 🔐 **Anonymous Security** - Simple `X-User-ID` header-based session isolation
- 🚦 **Rate Limiting** - Protection against abuse (10-30 req/min)
- 📱 **Cross-Platform** - Single codebase for iOS, Android, and Web
- 🎨 **Material Design 3** - Modern, polished UI
- 🐳 **Docker Support** - Development and production containers
- ☁️ **Cloud-Ready** - GCP Cloud Run, Secret Manager, Cloud SQL support

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           Mobile App (React Native + Expo)          │
│  • Expo Router (file-based navigation)              │
│  • Material Design 3 UI                             │
│  • AsyncStorage for local persistence               │
└───────────────────┬─────────────────────────────────┘
                    │ REST API + Streaming
                    │ Anonymous X-User-ID Header
┌───────────────────▼─────────────────────────────────┐
│              Backend (FastAPI)                      │
│  • LangGraph State Machine                          │
│  • OpenAI GPT-4o-mini                               │
│  • SQLite/PostgreSQL                                │
│  • Rate Limiting & Security Headers                 │
└─────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (async Python web framework)
- LangChain & LangGraph (AI agent orchestration)
- OpenAI GPT-4o-mini
- SQLite (with PostgreSQL support for production)
- HTTP header validation
- Rate limiting (SlowAPI)
- Uvicorn (ASGI server)

**Mobile:**
- React Native 0.81.5
- Expo SDK 54
- TypeScript
- React Native Paper (Material Design 3)
- Expo Router
- AsyncStorage
- Axios

## 📁 Project Structure

```
medi-assistant/
├── backend/                      # FastAPI backend
│   ├── app/
│   │   ├── api.py               # Chat & thread endpoints
│   │   ├── auth_api.py          # Authentication endpoints
│   │   ├── graph.py             # LangGraph AI agent
│   │   ├── guardrails.py        # Safety validation
│   │   ├── db.py                # Database operations
│   │   ├── user_db.py           # User management
│   │   ├── schema.py            # Pydantic models
│   │   └── settings.py          # Configuration
│   ├── tests/                   # Pytest test suite
│   ├── main.py                  # Application entry point
│   ├── Dockerfile               # Multi-stage production build
│   └── pyproject.toml           # Python dependencies
├── mobile/                       # React Native app
│   ├── app/                     # Expo Router screens
│   │   ├── _layout.tsx          # Root layout
│   │   ├── index.tsx            # Thread list
│   │   ├── chat/[threadId].tsx  # Chat screen
│   │   └── auth/                # Login/Register
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   ├── context/             # React Context
│   │   ├── services/api.ts      # API client
│   │   ├── config/theme.ts      # Theme configuration
│   │   └── types/               # TypeScript types
│   └── package.json
├── docker-compose.yml            # Development setup
└── docker-compose.prod.yml       # Production setup
```

## 🚀 Quick Start

### Prerequisites

- **Backend**: Python 3.12+, OpenAI API key
- **Mobile**: Node.js 18+, npm
- **Docker** (optional): Docker Desktop or Docker Engine

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone <repository-url>
cd medi-assistant

# 2. Set environment variables
export OPENAI_API_KEY="your-openai-key-here"

# 3. Start backend with Docker
docker-compose up -d

# 4. Install mobile dependencies
cd mobile
npm install

# 5. Configure mobile environment
echo "EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env
echo "EXPO_PUBLIC_USER_ID=user-1" >> .env

# 6. Start mobile app
npm start
```

### Option 2: Manual Setup

#### Backend

```bash
cd backend

# Install dependencies (using uv - faster)
pip install uv
uv sync

# Or use pip
pip install -e .

# Configure environment
cat > .env << EOF
OPENAI_API_KEY=your-key-here
MODEL_NAME=gpt-4o-mini
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:8081,exp://192.168.1.100:8081
EOF

# Run server
python main.py
```

Backend will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

#### Mobile App

```bash
cd mobile

# Install dependencies
npm install

# Configure environment
# For Android Emulator
echo "EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1" > .env

# For iOS Simulator
echo "EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env

# For Physical Device (use your computer's IP)
echo "EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1" > .env

# Start Expo
npm start
# Then: 'a' for Android, 'i' for iOS, 'w' for web
```

## 🔐 Security Features

- ✅ **Anonymous Sessions** - Secure header-based (`X-User-ID`) tracking
- ✅ **Rate Limiting** - Per-IP limits on all endpoints
- ✅ **CORS Configuration** - Restricted origins
- ✅ **Security Headers** - X-Frame-Options, CSP, XSS Protection
- ✅ **HSTS** - Enabled in production
- ✅ **Input Validation** - LLM-based medical domain guardrails
- ✅ **Thread Ownership** - Users can only access their own data
- ✅ **Non-root Docker** - Runs as unprivileged user

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py -v
```

## 🚢 Deployment

### Docker Production Build

```bash
# Build and run production containers
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop containers
docker-compose -f docker-compose.prod.yml down
```

### Google Cloud Run

The backend is optimized for Cloud Run deployment:

```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/PROJECT_ID/medi-assistant

# Deploy to Cloud Run
gcloud run deploy medi-assistant \
  --image gcr.io/PROJECT_ID/medi-assistant \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars OPENAI_API_KEY=your-key,ENVIRONMENT=production
```

**Cloud Features:**
- PostgreSQL support via Cloud SQL
- Secret Manager integration
- Structured logging (Cloud Logging)
- Health checks and auto-scaling

## 📚 API Documentation

### Chat Endpoints

All chat endpoints require an `X-User-ID: <uuid>` header to isolate and retrieve the correct history.

```bash
# Send message (streaming response)
POST /api/v1/chat
{
  "thread_id": "thread-123",
  "message": "What are the symptoms of flu?"
}

# List threads
GET /api/v1/threads

# Get chat history
GET /api/v1/history/{thread_id}

# Delete thread
DELETE /api/v1/threads/{thread_id}
```

**Rate Limits:**
- Chat: 10 requests/minute
- List/History: 30 requests/minute
- Delete: 10 requests/minute

Full interactive documentation: `http://localhost:8000/docs`

## 🛠️ Development

### Backend

```bash
cd backend

# Run with hot-reload
python main.py

# Run tests in watch mode
pytest-watch

# Format code
black app tests

# Lint
ruff check app
```

### Mobile

```bash
cd mobile

# Start with cache clear
npx expo start -c

# Run on specific platform
npm run android  # Android
npm run ios      # iOS (macOS only)
npm run web      # Web browser

# TypeScript check
npx tsc --noEmit
```

## 🐛 Troubleshooting

### Backend Won't Start
- Verify Python version: `python --version` (should be 3.12+)
- Check OpenAI API key is set in `.env`
- Ensure port 8000 is not in use: `lsof -i :8000`

### Mobile Can't Connect
- **Android Emulator**: Use `http://10.0.2.2:8000/api/v1`
- **iOS Simulator**: Use `http://localhost:8000/api/v1`
- **Physical Device**: Use computer's network IP (e.g., `http://192.168.1.100:8000/api/v1`)
- Verify backend is running: `curl http://localhost:8000/health`

### Docker Issues
```bash
# Clear everything and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## 📊 Project Status

**Current Version:** 1.0.0 (MVP/Beta)

**Implemented:**
- ✅ AI chat with streaming
- ✅ Multi-thread support
- ✅ Anonymous session tracking
- ✅ Safety guardrails
- ✅ Mobile app (iOS/Android/Web)
- ✅ Docker deployment
- ✅ Rate limiting

**Roadmap:**
- ⏳ Enhanced test coverage
- ⏳ CI/CD pipeline
- ⏳ PostgreSQL migration
- ⏳ Offline mobile support
- ⏳ Push notifications
- ⏳ Admin dashboard
- ⏳ Multi-language support

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Guidelines:**
- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and well-described

## 📄 License

[Add your license here - e.g., MIT, Apache 2.0]

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/medi-assistant/issues)
- **Documentation**: See `/backend/README.md` and `/mobile/README.md`
- **API Docs**: http://localhost:8000/docs

## ⚠️ Disclaimer

MediAssistant is an informational tool and **not a replacement for professional medical care**. Always consult qualified healthcare professionals for medical advice, diagnosis, or treatment.

---

**Built with ❤️ using FastAPI, LangGraph, and React Native**
