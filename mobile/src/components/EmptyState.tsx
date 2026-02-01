import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { spacing } from '../config/theme';

interface EmptyStateProps {
    icon: keyof typeof MaterialCommunityIcons.glyphMap;
    title: string;
    message: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, message }) => {
    const theme = useTheme();

    return (
        <View style={styles.container}>
            <MaterialCommunityIcons
                name={icon}
                size={64}
                color={theme.colors.outline}
                style={styles.icon}
            />
            <Text variant="headlineSmall" style={[styles.title, { color: theme.colors.onSurface }]}>
                {title}
            </Text>
            <Text
                variant="bodyMedium"
                style={[styles.message, { color: theme.colors.onSurfaceVariant }]}
            >
                {message}
            </Text>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        paddingHorizontal: spacing.xl,
    },
    icon: {
        marginBottom: spacing.md,
        opacity: 0.6,
    },
    title: {
        marginBottom: spacing.sm,
        textAlign: 'center',
        fontWeight: '600',
    },
    message: {
        textAlign: 'center',
        lineHeight: 22,
    },
});
