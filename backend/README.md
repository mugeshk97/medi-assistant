# MediAssistant

A full-stack intelligent medical assistant application combining AI-powered chat with safety guardrails and persistent conversation history.

## � Project Structure

```
medi-assistant/
├── backend/          # FastAPI backend with LangGraph AI agent
│   ├── app/         # Application modules
│   ├── main.py      # FastAPI entry point
│   └── README.md    # Backend-specific documentation
└── README.md        # This file
```

## 🚀 Quick Start

### Backend Setup

Navigate to the backend directory and follow the setup instructions:

```bash
cd backend
# See backend/README.md for detailed setup
```

**Prerequisites:**
- Python 3.12+
- OpenAI API key

**Quick commands:**
```bash
# Install dependencies
cd backend
uv sync  # or: pip install -e .

# Configure environment
echo "OPENAI_API_KEY=your-key-here" > .env

# Run server
python main.py
```

The backend API will be available at `http://localhost:8000`

## 🏗️ Architecture

### Backend
- **Framework**: FastAPI (async)
- **AI**: OpenAI GPT-4o-mini via LangChain & LangGraph
- **Database**: SQLite with async support
- **Features**:
  - 🤖 AI-powered conversational agent
  - 🛡️ Input/output safety guardrails
  - 💾 Persistent chat history
  - 👥 Multi-user thread management
  - ⚡ Real-time streaming responses

## � Documentation

- **Backend API**: See [backend/README.md](backend/README.md)
- **API Docs (Interactive)**: http://localhost:8000/docs (when running)

## 🔧 Development

### Backend Development
```bash
cd backend
python main.py  # Runs with hot-reload
```

## 📄 License

[Add your license here]

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. Code follows existing style
2. All tests pass
3. Documentation is updated

## 📞 Support

For issues and questions, please open an issue on the repository.
