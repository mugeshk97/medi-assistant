import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import { useTheme } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { spacing, borderRadius, colors } from '../config/theme';

export const TypingIndicator: React.FC = () => {
    const theme = useTheme();

    // Animation values for each dot
    const dot1 = useRef(new Animated.Value(0)).current;
    const dot2 = useRef(new Animated.Value(0)).current;
    const dot3 = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        // Create wave animation for dots
        const createDotAnimation = (animValue: Animated.Value, delay: number) => {
            return Animated.loop(
                Animated.sequence([
                    Animated.timing(animValue, {
                        toValue: -6,
                        duration: 400,
                        delay,
                        useNativeDriver: true,
                    }),
                    Animated.timing(animValue, {
                        toValue: 0,
                        duration: 400,
                        useNativeDriver: true,
                    }),
                ])
            );
        };

        // Start animations with stagger
        Animated.parallel([
            createDotAnimation(dot1, 0),
            createDotAnimation(dot2, 150),
            createDotAnimation(dot3, 300),
        ]).start();
    }, []);

    return (
        <View style={styles.container}>
            <View
                style={[
                    styles.bubble,
                    { backgroundColor: theme.colors.surfaceVariant },
                ]}
            >
                <View style={styles.dotsContainer}>
                    <Animated.View style={{ transform: [{ translateY: dot1 }] }}>
                        <LinearGradient
                            colors={[colors.primaryLight, colors.secondaryLight]}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 1, y: 1 }}
                            style={styles.dot}
                        />
                    </Animated.View>
                    <Animated.View style={{ transform: [{ translateY: dot2 }] }}>
                        <LinearGradient
                            colors={[colors.primaryLight, colors.secondaryLight]}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 1, y: 1 }}
                            style={styles.dot}
                        />
                    </Animated.View>
                    <Animated.View style={{ transform: [{ translateY: dot3 }] }}>
                        <LinearGradient
                            colors={[colors.primaryLight, colors.secondaryLight]}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 1, y: 1 }}
                            style={styles.dot}
                        />
                    </Animated.View>
                </View>
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
        paddingVertical: spacing.sm + 4,
        paddingHorizontal: spacing.md + 4,
        borderRadius: borderRadius.lg,
        borderBottomLeftRadius: spacing.xs,
    },
    dotsContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        gap: 6,
    },
    dot: {
        width: 8,
        height: 8,
        borderRadius: 4,
    },
});
