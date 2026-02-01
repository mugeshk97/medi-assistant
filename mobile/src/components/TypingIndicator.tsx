import React from 'react';
import { View, StyleSheet } from 'react-native';
import { ActivityIndicator, useTheme } from 'react-native-paper';
import { spacing } from '../config/theme';

export const TypingIndicator: React.FC = () => {
    const theme = useTheme();

    return (
        <View style={styles.container}>
            <View
                style={[
                    styles.bubble,
                    { backgroundColor: theme.colors.surfaceVariant },
                ]}
            >
                <ActivityIndicator size="small" color={theme.colors.primary} />
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginVertical: spacing.xs,
        paddingHorizontal: spacing.md,
        alignItems: 'flex-start',
    },
    bubble: {
        paddingVertical: spacing.md,
        paddingHorizontal: spacing.lg,
        borderRadius: 20,
    },
});
