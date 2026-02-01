# MediAssistant Mobile App

A modern React Native mobile application for the MediAssistant chat backend built with Expo and Material Design 3.

## Features

- 🤖 **AI-Powered Medical Chat**: Real-time streaming responses from GPT-4o-mini
- 💬 **Thread Management**: Create and switch between multiple conversation threads
- 📱 **Cross-Platform**: Works on iOS, Android, and Web
- 🎨 **Material Design 3**: Beautiful, modern UI with React Native Paper
- 💾 **Persistent Storage**: Chat history and user sessions saved locally
- ⚡ **Real-time Streaming**: See AI responses as they're generated

## Prerequisites

- Node.js 18+ and npm
- Expo CLI (`npm install -g expo-cli`)
- For iOS: macOS with Xcode (or use Expo Go app)
- For Android: Android Studio (or use Expo Go app)
- Backend server running at `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
cd mobile
npm install
```

### 2. Configure Environment

Update the `.env` file with your backend URL:

```env
EXPO_PUBLIC_API_URL=http://your-backend-url/api/v1
EXPO_PUBLIC_USER_ID=user-1
```

**Important**: 
- For Android Emulator: Use `http://10.0.2.2:8000/api/v1` (maps to localhost on host machine)
- For iOS Simulator: Use `http://localhost:8000/api/v1`
- For Physical Devices: Use your computer's IP address, e.g., `http://192.168.1.100:8000/api/v1`

### 3. Start the App

```bash
npm start
```

Then choose your platform:
- Press `a` for Android emulator
- Press `i` for iOS simulator
- Press `w` for web browser
- Scan QR code with Expo Go app on your physical device

## Project Structure

```
mobile/
├── app/                    # Expo Router screens
│   ├── _layout.tsx        # Root layout with providers
│   ├── index.tsx          # Home screen (thread list)
│   └── chat/
│       └── [threadId].tsx # Chat screen (dynamic route)
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ChatBubble.tsx
│   │   ├── MessageInput.tsx
│   │   ├── TypingIndicator.tsx
│   │   ├── EmptyState.tsx
│   │   └── ThreadListItem.tsx
│   ├── context/           # React Context for state
│   │   └── ChatContext.tsx
│   ├── services/          # API and external services
│   │   └── api.ts
│   ├── config/            # App configuration
│   │   └── theme.ts
│   ├── utils/             # Utility functions
│   │   └── storage.ts
│   └── types/             # TypeScript type definitions
│       └── index.ts
├── .env                   # Environment variables
├── app.json              # Expo configuration
└── package.json          # Dependencies
```

## Development

### Running on Android Emulator

```bash
npm run android
```

Make sure you have Android Studio installed and an emulator running, or use:
```bash
npm start
# Then press 'a' in the terminal
```

### Running on iOS Simulator (macOS only)

```bash
npm run ios
```

Or use:
```bash
npm start
# Then press 'i' in the terminal
```

### Running on Physical Device

1. Install the Expo Go app from App Store or Google Play
2. Run `npm start`
3. Scan the QR code with your device camera (iOS) or Expo Go app (Android)

## Backend Integration

This app requires the MediAssistant backend to be running. The backend provides:

- `POST /api/v1/chat` - Send messages with streaming responses
- `GET /api/v1/threads/{user_id}` - Get user's conversation threads
- `GET /api/v1/history/{thread_id}` - Get chat history for a thread

See the backend README for setup instructions.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `EXPO_PUBLIC_API_URL` | Backend API base URL | `http://10.0.2.2:8000/api/v1` |
| `EXPO_PUBLIC_USER_ID` | Default user ID | `user-1` |

## Building for Production

### Android APK

```bash
npx expo build:android
```

### iOS App

```bash
npx expo build:ios
```

## Troubleshooting

### Cannot connect to backend

- **Android Emulator**: Use `http://10.0.2.2:8000` instead of `localhost`
- **Physical Device**: Ensure device is on same network and use computer's IP address
- **iOS Simulator**: `http://localhost:8000` should work

### Metro bundler issues

```bash
npx expo start -c  # Clear cache
```

### Dependency issues

If you see errors about missing `react-native-web` or version mismatches:

```bash
npx expo install react-native-web react-dom @expo/metro-runtime
npx expo install --fix  # Fixes all version mismatches
```

### Android SDK not found

If you don't have Android Studio installed, you can still test on:
- Physical Android device with Expo Go app (scan QR code)
- iOS Simulator (macOS only)
- Web browser (press 'w')

```bash
rm -rf node_modules package-lock.json
npm install
```

## Tech Stack

- **React Native** - Mobile framework
- **Expo** - Development platform
- **Expo Router** - File-based navigation
- **React Native Paper** - Material Design components
- **TypeScript** - Type safety
- **Axios** - HTTP client
- **AsyncStorage** - Local data persistence

## License

[Add your license here]
