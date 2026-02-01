import { Stack } from 'expo-router';
import { PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { ErrorBoundary } from 'react-error-boundary';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { ChatProvider } from '../src/context/ChatContext';
import { AuthProvider } from '../src/context/AuthContext';
import { SnackbarProvider } from '../src/context/SnackbarContext';
import { ThemeProvider, useThemeMode } from '../src/context/ThemeContext';
import { lightTheme, darkTheme } from '../src/config/theme';
import { ErrorFallback } from '../src/components/ErrorFallback';
import { useFonts, Inter_400Regular, Inter_500Medium, Inter_600SemiBold, Inter_700Bold } from '@expo-google-fonts/inter';
import { PlusJakartaSans_700Bold } from '@expo-google-fonts/plus-jakarta-sans';
import { useEffect } from 'react';
import * as SplashScreen from 'expo-splash-screen';

// Keep splash screen visible while loading resources
SplashScreen.preventAutoHideAsync();

function AppContent() {
    const { isDark } = useThemeMode();
    const theme = isDark ? darkTheme : lightTheme;

    const [fontsLoaded] = useFonts({
        Inter_400Regular,
        Inter_500Medium,
        Inter_600SemiBold,
        Inter_700Bold,
        PlusJakartaSans_700Bold,
    });

    useEffect(() => {
        if (fontsLoaded) {
            SplashScreen.hideAsync();
        }
    }, [fontsLoaded]);

    if (!fontsLoaded) {
        return null;
    }

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
        <GestureHandlerRootView style={{ flex: 1 }}>
            <SafeAreaProvider>
                <ErrorBoundary FallbackComponent={ErrorFallback}>
                    <ThemeProvider>
                        <AppContent />
                    </ThemeProvider>
                </ErrorBoundary>
            </SafeAreaProvider>
        </GestureHandlerRootView>
    );
}
