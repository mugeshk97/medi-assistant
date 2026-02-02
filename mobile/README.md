# MediAssistant Mobile App

> Cross-platform mobile application for MediAssistant built with React Native, Expo, and Material Design 3.

## 📋 Overview

The MediAssistant mobile app provides a modern, intuitive interface for interacting with the AI medical assistant. Built with React Native and Expo, it works seamlessly across iOS, Android, and Web platforms.

**Key Capabilities:**
- 💬 **Real-time AI chat** with streaming responses
- 📱 **Thread management** for organizing conversations
- 🎨 **Material Design 3** for a polished, modern UI
- 💾 **Local persistence** with AsyncStorage
- 🔐 **Secure authentication** via JWT tokens
- ⚡ **Optimized performance** with React Native best practices

## ✨ Features

- 🤖 **Streaming AI Responses** - See responses as they're generated
- 💬 **Multi-Thread Support** - Organize conversations by topic
- 🎨 **Material Design 3** - Beautiful, accessible UI components
- 📱 **Cross-Platform** - Single codebase for iOS, Android, Web
- 🔐 **JWT Authentication** - Secure login and registration
- 💾 **Offline Storage** - Chat history persisted locally
- 🎭 **Custom Fonts** - Inter and Plus Jakarta Sans
- ✨ **Rich UI** - Blur effects, haptics, gradients, animations
- 📋 **Clipboard Support** - Copy messages with one tap
- 🌓 **Theme Support** - Ready for light/dark modes
- ⚡ **Expo Router** - File-based navigation

## 🏗️ Architecture

### App Structure

```
mobile/
├── app/                          # Expo Router (screens)
│   ├── _layout.tsx              # Root layout with providers
│   ├── index.tsx                # Home screen (thread list)
│   ├── auth/
│   │   ├── login.tsx            # Login screen
│   │   └── register.tsx         # Registration screen
│   ├── chat/
│   │   └── [threadId].tsx       # Dynamic chat screen
│   └── settings.tsx             # Settings screen
├── src/
│   ├── components/              # Reusable UI components
│   │   ├── ChatBubble.tsx      # Message display component
│   │   ├── MessageInput.tsx    # Input field with send button
│   │   ├── TypingIndicator.tsx # Loading animation
│   │   ├── EmptyState.tsx      # Empty thread placeholder
│   │   └── ThreadListItem.tsx  # Thread preview card
│   ├── context/                 # React Context
│   │   ├── ChatContext.tsx     # Chat state management
│   │   ├── AuthContext.tsx     # Authentication state
│   │   └── ThemeContext.tsx    # Theme management
│   ├── services/
│   │   └── api.ts              # API client & streaming
│   ├── config/
│   │   └── theme.ts            # Material Design theme config
│   ├── utils/
│   │   ├── storage.ts          # AsyncStorage wrapper
│   │   └── validation.ts       # Input validation
│   └── types/
│       └── index.ts            # TypeScript type definitions
├── assets/                      # Images, icons, fonts
├── app.json                     # Expo configuration
├── package.json                 # Dependencies
└── tsconfig.json                # TypeScript config
```

### Tech Stack

- **React Native** 0.81.5 - Mobile framework
- **Expo** SDK 54 - Development platform
- **TypeScript** - Type safety
- **Expo Router** - File-based navigation
- **React Native Paper** - Material Design 3 components
- **AsyncStorage** - Local persistence
- **Axios** - HTTP client (with streaming support)
- **React Context** - State management
- **Google Fonts** - Custom typography (Inter, Plus Jakarta Sans)

### Navigation Flow

```
┌─────────────┐
│   Login     │ ←→ Register
└──────┬──────┘
       ↓ (authenticated)
┌─────────────┐
│ Thread List │ ← Home Screen
└──────┬──────┘
       ↓ (select thread)
┌─────────────┐
│ Chat Screen │ ← Dynamic route: /chat/[threadId]
└──────┬──────┘
       ↓ (settings icon)
┌─────────────┐
│  Settings   │
└─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Expo CLI** (optional, npx works)
- **Backend** - MediAssistant backend running
- **Optional**:
  - Android Studio (for Android emulator)
  - Xcode (macOS only, for iOS simulator)
  - Expo Go app (for physical device testing)

### Installation

```bash
# 1. Navigate to mobile directory
cd mobile

# 2. Install dependencies
npm install

# 3. Verify installation
npx expo --version
```

### Configuration

Create a `.env` file based on your platform:

#### For Android Emulator
```bash
echo "EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1" > .env
echo "EXPO_PUBLIC_USER_ID=user-1" >> .env
```

#### For iOS Simulator
```bash
echo "EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env
echo "EXPO_PUBLIC_USER_ID=user-1" >> .env
```

#### For Physical Device
```bash
# Replace with your computer's IP address
echo "EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1" > .env
echo "EXPO_PUBLIC_USER_ID=user-1" >> .env
```

### Running the App

```bash
# Start Expo development server
npm start

# Then choose platform:
# - Press 'a' for Android
# - Press 'i' for iOS (macOS only)
# - Press 'w' for Web
# - Scan QR code with Expo Go app (physical device)
```

**Platform-Specific Commands:**
```bash
npm run android  # Launch Android emulator
npm run ios      # Launch iOS simulator (macOS only)
npm run web      # Open in web browser
```

## 📱 Platform-Specific Setup

### Android Development

#### Option 1: Android Emulator (Recommended)

1. **Install Android Studio**
   ```bash
   # Download from: https://developer.android.com/studio
   ```

2. **Create Virtual Device**
   - Open Android Studio
   - Tools → Device Manager → Create Device
   - Select Pixel 5 or similar
   - Download and select Android 13 (API 33) system image

3. **Run App**
   ```bash
   npm run android
   ```

#### Option 2: Physical Android Device

1. **Enable Developer Mode**
   - Settings → About Phone → Tap "Build Number" 7 times

2. **Enable USB Debugging**
   - Settings → Developer Options → USB Debugging

3. **Connect & Run**
   ```bash
   # Check device is connected
   adb devices
   
   # Run app
   npm run android
   ```

#### Option 3: Expo Go App (Easiest)

1. Install Expo Go from Google Play Store
2. Run `npm start`
3. Scan QR code from terminal

### iOS Development (macOS Only)

#### Option 1: iOS Simulator

1. **Install Xcode**
   ```bash
   # Download from App Store or:
   xcode-select --install
   ```

2. **Run App**
   ```bash
   npm run ios
   ```

#### Option 2: Physical iPhone

1. Install Expo Go from App Store
2. Run `npm start`
3. Scan QR code with Camera app

### Web Development

```bash
npm run web
# Opens in browser at http://localhost:8081
```

## 🛠️ Development

### Development Server

```bash
# Start with default settings
npm start

# Start with cache cleared
npx expo start -c

# Start in LAN mode (for physical devices)
npx expo start --lan

# Start in tunnel mode (easier for physical devices)
npx expo start --tunnel
```

### TypeScript

```bash
# Type check without emitting
npx tsc --noEmit

# Watch mode
npx tsc --noEmit --watch
```

### Debugging

#### React DevTools
```bash
# Install globally
npm install -g react-devtools

# Start
react-devtools

# Then reload app (Shift + R in terminal)
```

#### Flipper (Advanced)
1. Download Flipper from https://fbflipper.com
2. Run app in development mode
3. Flipper auto-detects app

### Code Quality

```bash
# ESLint (if configured)
npx eslint .

# Prettier (if configured)
npx prettier --write .
```

## 🎨 Customization

### Theme Configuration

Edit `src/config/theme.ts`:

```typescript
export const theme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#0891B2',        // Cyan-600
    secondary: '#6750A4',      // Purple
    // ... customize colors
  },
};
```

### Fonts

Custom fonts are loaded via `@expo-google-fonts`:
- **Inter** - UI text
- **Plus Jakarta Sans** - Headings

To add more fonts:
```bash
npm install @expo-google-fonts/[font-name]
```

### App Icon & Splash Screen

1. **Icon**: Replace `assets/icon.png` (1024x1024)
2. **Splash**: Replace `assets/splash.png` (1284x2778)
3. **Favicon**: Replace `assets/favicon.png` (48x48)

Regenerate with:
```bash
npx expo prebuild --clean
```

## 📚 Key Components

### ChatBubble
Displays individual messages with role-based styling.
```tsx
<ChatBubble
  role="user" | "assistant"
  content="message text"
  timestamp="2026-02-02T12:00:00"
/>
```

### MessageInput
Input field with send button and state management.
```tsx
<MessageInput
  onSend={(message) => handleSend(message)}
  disabled={isLoading}
/>
```

### TypingIndicator
Animated loading indicator during AI responses.
```tsx
<TypingIndicator visible={isStreaming} />
```

## 🔐 Authentication

The app uses JWT tokens stored in AsyncStorage:

```typescript
// Login flow
const { access_token } = await api.login(username, password);
await storage.setToken(access_token);

// API requests automatically include token
headers: { Authorization: `Bearer ${token}` }

// Logout
await storage.removeToken();
```

## 🐛 Troubleshooting

### Cannot Connect to Backend

**Android Emulator:**
```bash
# Use 10.0.2.2 instead of localhost
echo "EXPO_PUBLIC_API_URL=http://10.0.2.2:8000/api/v1" > .env
```

**Physical Device:**
```bash
# Find your computer's IP
# macOS/Linux: ifconfig | grep inet
# Windows: ipconfig

# Use that IP
echo "EXPO_PUBLIC_API_URL=http://192.168.1.100:8000/api/v1" > .env
```

**Verify Backend:**
```bash
curl http://localhost:8000/health
```

### Metro Bundler Issues

```bash
# Clear cache
npx expo start -c

# Reset everything
rm -rf node_modules .expo
npm install
npx expo start -c
```

### Dependency Conflicts

```bash
# Fix Expo SDK version mismatches
npx expo install --fix

# Reinstall specific package
npm uninstall [package]
npm install [package]@latest
```

### Android Build Errors

```bash
# Clear Gradle cache
cd android
./gradlew clean
cd ..

# Rebuild
npx expo run:android
```

### iOS Build Errors (macOS)

```bash
# Clear derived data
rm -rf ~/Library/Developer/Xcode/DerivedData

# Reinstall pods
cd ios
pod deintegrate
pod install
cd ..

# Rebuild
npx expo run:ios
```

### TypeScript Errors

```bash
# Regenerate types
npx expo customize tsconfig.json

# Restart TypeScript server in VS Code
# Cmd+Shift+P → "TypeScript: Restart TS Server"
```

## 📦 Building for Production

### Android APK

```bash
# Configure app.json with proper bundle ID and credentials

# Build APK
eas build --platform android --profile preview

# Or build AAB for Play Store
eas build --platform android
```

### iOS IPA

```bash
# Requires macOS and Apple Developer account

# Build for App Store
eas build --platform ios

# Build for TestFlight
eas build --platform ios --profile preview
```

### Over-the-Air Updates

```bash
# Publish update without rebuilding
eas update --branch production --message "Bug fixes"
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Login/Register flows
- [ ] Create new thread
- [ ] Send message and receive streaming response
- [ ] Switch between threads
- [ ] Delete thread
- [ ] Logout
- [ ] Handle network errors
- [ ] Test on different screen sizes
- [ ] Test offline behavior

### Automated Testing (Future)

```bash
# Jest for unit tests
npm test

# Detox for E2E tests
npx detox test
```

## 📊 Performance

- **Bundle Size**: ~15MB (production build)
- **Initial Load**: ~2-3 seconds
- **Frame Rate**: 60 FPS on modern devices
- **Memory Usage**: ~100MB average

### Performance Tips

1. **Optimize Images**: Use WebP format
2. **Lazy Load**: Load screens on-demand
3. **Memoization**: Use React.memo for expensive components
4. **FlatList**: Use for long message lists
5. **Remove Console**: Disable console.log in production

## 🔄 Future Enhancements

- [ ] Offline mode with queue
- [ ] Push notifications
- [ ] Voice input
- [ ] Image attachments
- [ ] Export chat history
- [ ] Dark mode toggle
- [ ] Multi-language support
- [ ] Accessibility improvements
- [ ] In-app feedback
- [ ] Analytics integration

## 🌍 Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EXPO_PUBLIC_API_URL` | Backend API base URL | `http://10.0.2.2:8000/api/v1` |
| `EXPO_PUBLIC_USER_ID` | Default user ID (dev only) | `user-1` |

## 📄 License

[Add your license here]

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/medi-assistant/issues)
- **Main Docs**: [../README.md](../README.md)
- **Backend Docs**: [../backend/README.md](../backend/README.md)
- **Expo Docs**: https://docs.expo.dev

## 💡 Resources

- [React Native Documentation](https://reactnative.dev)
- [Expo Documentation](https://docs.expo.dev)
- [React Native Paper](https://callstack.github.io/react-native-paper/)
- [Material Design 3](https://m3.material.io)
- [Expo Router](https://docs.expo.dev/router/introduction/)

---

**Part of the MediAssistant project** • [Main README](../README.md) • [Backend README](../backend/README.md)
