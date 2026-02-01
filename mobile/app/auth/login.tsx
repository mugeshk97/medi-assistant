import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, ScrollView, Platform } from 'react-native';
import { TextInput, Button, Text, Surface, useTheme, HelperText } from 'react-native-paper';
import { useRouter } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { useSnackbar } from '../../src/context/SnackbarContext';

export default function LoginScreen() {
    const theme = useTheme();
    const router = useRouter();
    const { login, isLoading: authLoading } = useAuth();
    const { showSnackbar } = useSnackbar();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [errors, setErrors] = useState({ username: '', password: '' });

    const validate = () => {
        const newErrors = { username: '', password: '' };
        let isValid = true;

        if (!username.trim()) {
            newErrors.username = 'Username or email is required';
            isValid = false;
        }

        if (!password) {
            newErrors.password = 'Password is required';
            isValid = false;
        }

        setErrors(newErrors);
        return isValid;
    };

    const handleLogin = async () => {
        if (!validate()) return;

        setIsLoading(true);
        try {
            await login(username.trim(), password);
            showSnackbar('Login successful!', 'success');
            router.replace('/');
        } catch (error: any) {
            showSnackbar(error.message || 'Login failed', 'error');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <KeyboardAvoidingView
            style={styles.container}
            behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        >
            <ScrollView contentContainerStyle={styles.scrollContent}>
                <Surface style={styles.surface} elevation={1}>
                    <Text variant="headlineMedium" style={styles.title}>
                        Welcome Back
                    </Text>
                    <Text variant="bodyMedium" style={styles.subtitle}>
                        Sign in to continue
                    </Text>

                    <TextInput
                        label="Username or Email"
                        value={username}
                        onChangeText={(text) => {
                            setUsername(text);
                            setErrors({ ...errors, username: '' });
                        }}
                        mode="outlined"
                        style={styles.input}
                        autoCapitalize="none"
                        autoCorrect={false}
                        error={!!errors.username}
                        disabled={isLoading}
                    />
                    <HelperText type="error" visible={!!errors.username}>
                        {errors.username}
                    </HelperText>

                    <TextInput
                        label="Password"
                        value={password}
                        onChangeText={(text) => {
                            setPassword(text);
                            setErrors({ ...errors, password: '' });
                        }}
                        mode="outlined"
                        secureTextEntry={!showPassword}
                        style={styles.input}
                        error={!!errors.password}
                        disabled={isLoading}
                        right={
                            <TextInput.Icon
                                icon={showPassword ? 'eye-off' : 'eye'}
                                onPress={() => setShowPassword(!showPassword)}
                            />
                        }
                    />
                    <HelperText type="error" visible={!!errors.password}>
                        {errors.password}
                    </HelperText>

                    <Button
                        mode="contained"
                        onPress={handleLogin}
                        loading={isLoading}
                        disabled={isLoading || authLoading}
                        style={styles.button}
                    >
                        Sign In
                    </Button>

                    <View style={styles.footer}>
                        <Text variant="bodyMedium">Don't have an account? </Text>
                        <Button
                            mode="text"
                            onPress={() => router.push('/auth/register')}
                            disabled={isLoading}
                        >
                            Sign Up
                        </Button>
                    </View>
                </Surface>
            </ScrollView>
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    scrollContent: {
        flexGrow: 1,
        justifyContent: 'center',
        padding: 20,
    },
    surface: {
        padding: 24,
        borderRadius: 12,
    },
    title: {
        textAlign: 'center',
        marginBottom: 8,
        fontWeight: 'bold',
    },
    subtitle: {
        textAlign: 'center',
        marginBottom: 24,
        opacity: 0.7,
    },
    input: {
        marginBottom: 4,
    },
    button: {
        marginTop: 16,
        marginBottom: 16,
    },
    footer: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
    },
});
