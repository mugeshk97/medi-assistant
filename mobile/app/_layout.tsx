import { Stack } from 'expo-router';
import { PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ErrorBoundary } from 'react-error-boundary';
import { ChatProvider } from '../src/context/ChatContext';
import { AuthProvider } from '../src/context/AuthContext';
import { SnackbarProvider } from '../src/context/SnackbarContext';
import { ThemeProvider, useThemeMode } from '../src/context/ThemeContext';
import { lightTheme, darkTheme } from '../src/config/theme';
import { ErrorFallback } from '../src/components/ErrorFallback';

function AppContent() {
    const { isDark } = useThemeMode();
    const theme = isDark ? darkTheme : lightTheme;

    return (
        <PaperProvider theme={theme}>
            <SnackbarProvider>
                <AuthProvider>
                    <ChatProvider>
                        <Stack
                            screenOptions={{
                                headerShown: false,
                            }}
                        >
                            <Stack.Screen name="index" />
                            <Stack.Screen name="chat/[threadId]" />
                            <Stack.Screen name="settings" />
                            <Stack.Screen name="auth/login" />
                            <Stack.Screen name="auth/register" />
                        </Stack>
                    </ChatProvider>
                </AuthProvider>
            </SnackbarProvider>
        </PaperProvider>
    );
}

export default function RootLayout() {
    return (
        <SafeAreaProvider>
            <ErrorBoundary FallbackComponent={ErrorFallback}>
                <ThemeProvider>
                    <AppContent />
                </ThemeProvider>
            </ErrorBoundary>
        </SafeAreaProvider>
    );
}
