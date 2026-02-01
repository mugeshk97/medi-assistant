import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, ScrollView, Platform } from 'react-native';
import { TextInput, Button, Text, Surface, HelperText } from 'react-native-paper';
import { useRouter } from 'expo-router';
import { useAuth } from '../../src/context/AuthContext';
import { useSnackbar } from '../../src/context/SnackbarContext';

export default function RegisterScreen() {
    const router = useRouter();
    const { register, isLoading: authLoading } = useAuth();
    const { showSnackbar } = useSnackbar();

    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [errors, setErrors] = useState({
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
    });

    const validate = () => {
        const newErrors = { email: '', username: '', password: '', confirmPassword: '' };
        let isValid = true;

        // Email validation
        if (!email.trim()) {
            newErrors.email = 'Email is required';
            isValid = false;
        } else if (!/\S+@\S+\.\S+/.test(email)) {
            newErrors.email = 'Email is invalid';
            isValid = false;
        }

        // Username validation
        if (!username.trim()) {
            newErrors.username = 'Username is required';
            isValid = false;
        } else if (username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
            isValid = false;
        } else if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
            newErrors.username = 'Username can only contain letters, numbers, dashes, and underscores';
            isValid = false;
        }

        // Password validation
        if (!password) {
            newErrors.password = 'Password is required';
            isValid = false;
        } else if (password.length < 8) {
            newErrors.password = 'Password must be at least 8 characters';
            isValid = false;
        }

        // Confirm password validation
        if (password !== confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
            isValid = false;
        }

        setErrors(newErrors);
        return isValid;
    };

    const handleRegister = async () => {
        if (!validate()) return;

        setIsLoading(true);
        try {
            await register(email.trim(), username.trim(), password);
            showSnackbar('Registration successful!', 'success');
            router.replace('/');
        } catch (error: any) {
            showSnackbar(error.message || 'Registration failed', 'error');
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
                        Create Account
                    </Text>
                    <Text variant="bodyMedium" style={styles.subtitle}>
                        Sign up to get started
                    </Text>

                    <TextInput
                        label="Email"
                        value={email}
                        onChangeText={(text) => {
                            setEmail(text);
                            setErrors({ ...errors, email: '' });
                        }}
                        mode="outlined"
                        style={styles.input}
                        autoCapitalize="none"
                        keyboardType="email-address"
                        autoCorrect={false}
                        error={!!errors.email}
                        disabled={isLoading}
                    />
                    <HelperText type="error" visible={!!errors.email}>
                        {errors.email}
                    </HelperText>

                    <TextInput
                        label="Username"
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

                    <TextInput
                        label="Confirm Password"
                        value={confirmPassword}
                        onChangeText={(text) => {
                            setConfirmPassword(text);
                            setErrors({ ...errors, confirmPassword: '' });
                        }}
                        mode="outlined"
                        secureTextEntry={!showPassword}
                        style={styles.input}
                        error={!!errors.confirmPassword}
                        disabled={isLoading}
                    />
                    <HelperText type="error" visible={!!errors.confirmPassword}>
                        {errors.confirmPassword}
                    </HelperText>

                    <Button
                        mode="contained"
                        onPress={handleRegister}
                        loading={isLoading}
                        disabled={isLoading || authLoading}
                        style={styles.button}
                    >
                        Sign Up
                    </Button>

                    <View style={styles.footer}>
                        <Text variant="bodyMedium">Already have an account? </Text>
                        <Button
                            mode="text"
                            onPress={() => router.back()}
                            disabled={isLoading}
                        >
                            Sign In
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
