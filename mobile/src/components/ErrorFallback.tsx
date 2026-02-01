import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, Button, useTheme } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';

interface ErrorFallbackProps {
    error: Error;
    resetErrorBoundary: () => void;
}

export const ErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetErrorBoundary }) => {
    const theme = useTheme();

    return (
        <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
            <MaterialCommunityIcons
                name="alert-circle-outline"
                size={64}
                color={theme.colors.error}
            />
            <Text variant="headlineSmall" style={[styles.title, { color: theme.colors.onBackground }]}>
                Oops! Something went wrong
            </Text>
            <Text
                variant="bodyMedium"
                style={[styles.message, { color: theme.colors.onSurfaceVariant }]}
            >
                We're sorry for the inconvenience. The app encountered an unexpected error.
            </Text>
            {__DEV__ && (
                <View style={styles.errorDetails}>
                    <Text variant="bodySmall" style={{ color: theme.colors.error, fontFamily: 'monospace' }}>
                        {error.message}
                    </Text>
                </View>
            )}
            <Button
                mode="contained"
                onPress={resetErrorBoundary}
                style={styles.button}
            >
                Try Again
            </Button>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 24,
    },
    title: {
        marginTop: 16,
        marginBottom: 8,
        textAlign: 'center',
    },
    message: {
        marginBottom: 24,
        textAlign: 'center',
        maxWidth: 300,
    },
    errorDetails: {
        marginBottom: 24,
        padding: 12,
        backgroundColor: '#ffebee',
        borderRadius: 8,
        maxWidth: '90%',
    },
    button: {
        minWidth: 150,
    },
});
