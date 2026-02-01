import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import { Text, useTheme } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { spacing, colors } from '../config/theme';
import { pulse, float } from '../utils/animations';

interface EmptyStateProps {
    icon: keyof typeof MaterialCommunityIcons.glyphMap;
    title: string;
    message: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ icon, title, message }) => {
    const theme = useTheme();
    const pulseAnim = useRef(new Animated.Value(1)).current;
    const floatAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        // Start animations
        pulse(pulseAnim, 0.95, 1.05, 2000).start();
        float(floatAnim, 8, 3000).start();
    }, []);

    return (
        <View style={styles.container}>
            <Animated.View
                style={{
                    transform: [
                        { scale: pulseAnim },
                        { translateY: floatAnim },
                    ],
                }}
            >
                <LinearGradient
                    colors={[colors.primaryLight, colors.secondaryLight]}
                    start={{ x: 0, y: 0 }}
                    end={{ x: 1, y: 1 }}
                    style={styles.iconGradient}
                >
                    <MaterialCommunityIcons
                        name={icon}
                        size={48}
                        color="#FFFFFF"
                    />
                </LinearGradient>
            </Animated.View>

            <Text
                variant="headlineSmall"
                style={[styles.title, { color: theme.colors.onSurface }]}
            >
                {title}
            </Text>
            <Text
                variant="bodyLarge"
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
    iconGradient: {
        width: 96,
        height: 96,
        borderRadius: 48,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: spacing.lg,
    },
    title: {
        marginBottom: spacing.md,
        textAlign: 'center',
        fontWeight: '700',
    },
    message: {
        textAlign: 'center',
        lineHeight: 26,
        opacity: 0.8,
    },
});
