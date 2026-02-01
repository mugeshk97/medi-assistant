import React, { useState, useRef, useEffect } from 'react';
import { View, StyleSheet, Animated, TouchableOpacity, Platform } from 'react-native';
import { Text, Surface, useTheme, Icon } from 'react-native-paper';
import { Swipeable } from 'react-native-gesture-handler';
import { LinearGradient } from 'expo-linear-gradient';
import { Thread } from '../types';
import { spacing, borderRadius, shadows, colors } from '../config/theme';
import { lightImpact } from '../utils/haptics';

interface ThreadListItemProps {
    thread: Thread;
    onPress: () => void;
    onDelete: () => void;
    index?: number;
}

// Helper to format relative time
const formatRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
};

export const ThreadListItem: React.FC<ThreadListItemProps> = ({
    thread,
    onPress,
    onDelete,
    index = 0
}) => {
    const theme = useTheme();
    const scaleAnim = useRef(new Animated.Value(1)).current;
    const fadeAnim = useRef(new Animated.Value(0)).current;

    useEffect(() => {
        // Entrance animation with stagger
        Animated.timing(fadeAnim, {
            toValue: 1,
            duration: 300,
            delay: index * 50,
            useNativeDriver: true,
        }).start();
    }, []);

    const handlePressIn = () => {
        lightImpact();
        Animated.spring(scaleAnim, {
            toValue: 0.97,
            useNativeDriver: true,
        }).start();
    };

    const handlePressOut = () => {
        Animated.spring(scaleAnim, {
            toValue: 1,
            friction: 5,
            tension: 40,
            useNativeDriver: true,
        }).start();
    };

    const renderRightActions = (
        progress: Animated.AnimatedInterpolation<number>,
        dragX: Animated.AnimatedInterpolation<number>
    ) => {
        const trans = dragX.interpolate({
            inputRange: [-100, 0],
            outputRange: [0, 100],
            extrapolate: 'clamp',
        });

        return (
            <TouchableOpacity
                style={[styles.deleteAction, { backgroundColor: theme.colors.error }]}
                onPress={onDelete}
            >
                <Animated.View
                    style={[
                        styles.deleteActionContent,
                        {
                            transform: [{ translateX: trans }],
                        },
                    ]}
                >
                    <Icon source="delete" color="#FFFFFF" size={24} />
                    <Text style={styles.deleteText}>Delete</Text>
                </Animated.View>
            </TouchableOpacity>
        );
    };

    return (
        <Animated.View style={{ opacity: fadeAnim }}>
            <Swipeable
                renderRightActions={renderRightActions}
                overshootRight={false}
                friction={2}
            >
                <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
                    <Surface
                        style={[
                            styles.container,
                            { backgroundColor: theme.colors.surface },
                            shadows.sm
                        ]}
                        elevation={0}
                    >
                        {/* Gradient accent on left edge */}
                        <LinearGradient
                            colors={[colors.primaryMain, colors.secondaryMain]}
                            start={{ x: 0, y: 0 }}
                            end={{ x: 0, y: 1 }}
                            style={styles.accentBar}
                        />

                        <TouchableOpacity
                            onPress={onPress}
                            onPressIn={handlePressIn}
                            onPressOut={handlePressOut}
                            style={styles.touchable}
                            activeOpacity={1}
                        >
                            <View style={styles.iconContainer}>
                                <LinearGradient
                                    colors={[colors.primaryLight, colors.secondaryLight]}
                                    start={{ x: 0, y: 0 }}
                                    end={{ x: 1, y: 1 }}
                                    style={styles.iconGradient}
                                >
                                    <Icon source="message-outline" size={22} color="#FFFFFF" />
                                </LinearGradient>
                            </View>
                            <View style={styles.content}>
                                <Text
                                    variant="titleMedium"
                                    numberOfLines={1}
                                    style={styles.title}
                                >
                                    {thread.title || 'New Chat'}
                                </Text>
                                <Text
                                    variant="bodySmall"
                                    style={[styles.subtitle, { color: theme.colors.onSurfaceVariant }]}
                                    numberOfLines={1}
                                >
                                    {formatRelativeTime(thread.updated_at)}
                                </Text>
                            </View>
                            <Icon source="chevron-right" size={20} color={theme.colors.onSurfaceVariant} />
                        </TouchableOpacity>
                    </Surface>
                </Animated.View>
            </Swipeable>
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginHorizontal: spacing.md,
        marginVertical: spacing.xs,
        borderRadius: borderRadius.md,
        overflow: 'hidden',
        flexDirection: 'row',
    },
    accentBar: {
        width: 4,
    },
    touchable: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
        padding: spacing.md,
    },
    iconContainer: {
        marginRight: spacing.md,
    },
    iconGradient: {
        width: 44,
        height: 44,
        borderRadius: borderRadius.md,
        alignItems: 'center',
        justifyContent: 'center',
    },
    content: {
        flex: 1,
    },
    title: {
        fontWeight: '600',
        marginBottom: spacing.xs - 2,
    },
    subtitle: {
        fontSize: 13,
    },
    deleteAction: {
        justifyContent: 'center',
        alignItems: 'flex-end',
        paddingHorizontal: spacing.lg,
        marginVertical: spacing.xs,
        borderTopRightRadius: borderRadius.md,
        borderBottomRightRadius: borderRadius.md,
    },
    deleteActionContent: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    deleteText: {
        color: '#FFFFFF',
        marginTop: 4,
        fontWeight: '600',
        fontSize: 13,
    },
});
