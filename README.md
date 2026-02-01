# MediAssistant

A full-stack intelligent medical assistant application combining AI-powered chat with safety guardrails and persistent conversation history.

## 📁 Project Structure

```
medi-assistant/
├── backend/          # FastAPI backend with LangGraph AI agent
│   ├── app/         # Application modules
│   ├── main.py      # FastAPI entry point
│   └── README.md    # Backend-specific documentation
├── mobile/          # React Native mobile app (Expo)
│   ├── app/         # Expo Router screens
│   ├── src/         # Components, services, context
│   └── README.md    # Mobile app documentation
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

### Mobile App Setup

Navigate to the mobile directory and follow the setup instructions:

```bash
cd mobile
# See mobile/README.md for detailed setup
```

**Prerequisites:**
- Node.js 18+ and npm
- Expo CLI (optional, uses npx)
- Backend server running at `http://localhost:8000`

**Quick commands:**
```bash
# Install dependencies
cd mobile
npm install

# Configure environment (update with your backend URL)
cp .env.example .env

# Start the app
npm start
# Then press 'a' for Android, 'i' for iOS, or scan QR with Expo Go
```

The mobile app will connect to the backend API.

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

### Mobile App
- **Framework**: React Native with Expo
- **Navigation**: Expo Router (file-based)
- **UI Library**: React Native Paper (Material Design 3)
- **State Management**: React Context
- **API Client**: Axios with streaming fetch support
- **Features**:
  - 📱 Cross-platform (iOS, Android, Web)
  - 💬 Thread-based conversations
  - ⚡ Real-time streaming responses
  - 🎨 Modern Material Design 3 UI
  - 💾 Persistent user sessions

## 📚 Documentation

- **Backend API**: See [backend/README.md](backend/README.md)
- **Mobile App**: See [mobile/README.md](mobile/README.md)
- **API Docs (Interactive)**: http://localhost:8000/docs (when running)

## 🔧 Development

### Backend Development
```bash
cd backend
python main.py  # Runs with hot-reload
```

### Mobile App Development
```bash
cd mobile
npm start  # Opens Expo development menu
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
