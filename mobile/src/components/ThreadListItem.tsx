import React, { useState } from 'react';
import { View, StyleSheet, Animated, TouchableOpacity } from 'react-native';
import { Text, Surface, useTheme, Icon } from 'react-native-paper';
import { Swipeable } from 'react-native-gesture-handler';
import { Thread } from '../types';
import { spacing, borderRadius } from '../config/theme';

interface ThreadListItemProps {
    thread: Thread;
    onPress: () => void;
    onDelete: () => void;
}

export const ThreadListItem: React.FC<ThreadListItemProps> = ({ thread, onPress, onDelete }) => {
    const theme = useTheme();

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
                    <Icon source="delete" color={theme.colors.onError} size={24} />
                    <Text style={{ color: theme.colors.onError, marginTop: 4 }}>Delete</Text>
                </Animated.View>
            </TouchableOpacity>
        );
    };

    return (
        <Swipeable renderRightActions={renderRightActions}>
            <Surface style={[styles.container, { backgroundColor: theme.colors.surface }]} elevation={1}>
                <TouchableOpacity onPress={onPress} style={styles.touchable}>
                    <View style={styles.iconContainer}>
                        <Icon source="message-outline" size={24} color={theme.colors.primary} />
                    </View>
                    <View style={styles.content}>
                        <Text variant="titleMedium" numberOfLines={1}>
                            {thread.title || 'New Chat'}
                        </Text>
                        <Text
                            variant="bodySmall"
                            style={{ color: theme.colors.onSurfaceVariant }}
                            numberOfLines={1}
                        >
                            {new Date(thread.updated_at).toLocaleDateString()} •{' '}
                            {new Date(thread.updated_at).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                            })}
                        </Text>
                    </View>
                    <Icon source="chevron-right" size={24} color={theme.colors.onSurfaceVariant} />
                </TouchableOpacity>
            </Surface>
        </Swipeable>
    );
};

const styles = StyleSheet.create({
    container: {
        marginHorizontal: spacing.md,
        marginVertical: spacing.xs,
        borderRadius: borderRadius.md,
        overflow: 'hidden',
    },
    touchable: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: spacing.md,
    },
    iconContainer: {
        marginRight: spacing.md,
    },
    content: {
        flex: 1,
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
});
