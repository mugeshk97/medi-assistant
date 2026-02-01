import React, { useEffect, useRef } from 'react';
import { View, StyleSheet, TouchableOpacity, Animated } from 'react-native';
import { Text, Surface, useTheme } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import * as Clipboard from 'expo-clipboard';
import { Message } from '../types';
import { spacing, borderRadius, shadows, colors } from '../config/theme';
import { useSnackbar } from '../context/SnackbarContext';
import { fadeIn, slideUp } from '../utils/animations';
import { lightImpact } from '../utils/haptics';

interface ChatBubbleProps {
    message: Message;
    index?: number;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message, index = 0 }) => {
    const theme = useTheme();
    const { showSnackbar } = useSnackbar();
    const isUser = message.role === 'user';

    // Animation values
    const fadeAnim = useRef(new Animated.Value(0)).current;
    const slideAnim = useRef(new Animated.Value(30)).current;

    useEffect(() => {
        // Entrance animation with stagger based on index
        Animated.parallel([
            fadeIn(fadeAnim, 300, index * 50),
            slideUp(slideAnim, 300, index * 50),
        ]).start();
    }, []);

    const handleLongPress = async () => {
        lightImpact();
        await Clipboard.setStringAsync(message.content);
        showSnackbar('Message copied to clipboard');
    };

    const animatedStyle = {
        opacity: fadeAnim,
        transform: [{ translateY: slideAnim }],
    };

    return (
        <Animated.View
            style={[
                styles.container,
                isUser ? styles.userContainer : styles.assistantContainer,
                animatedStyle,
            ]}
        >
            <TouchableOpacity
                onLongPress={handleLongPress}
                delayLongPress={500}
                activeOpacity={0.8}
            >
                {isUser ? (
                    // User message with gradient
                    <LinearGradient
                        colors={[colors.primaryMain, colors.secondaryMain]}
                        start={{ x: 0, y: 0 }}
                        end={{ x: 1, y: 1 }}
                        style={[styles.bubble, styles.userBubble, shadows.md]}
                    >
                        <Text style={[styles.text, styles.userText]}>
                            {message.content}
                        </Text>
                        {message.timestamp && (
                            <Text style={[styles.timestamp, styles.userTimestamp]}>
                                {new Date(message.timestamp).toLocaleTimeString([], {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                })}
                            </Text>
                        )}
                    </LinearGradient>
                ) : (
                    // Assistant message
                    <Surface
                        style={[
                            styles.bubble,
                            styles.assistantBubble,
                            {
                                backgroundColor: theme.colors.surfaceVariant,
                            },
                        ]}
                        elevation={2}
                    >
                        <Text
                            style={[
                                styles.text,
                                { color: theme.colors.onSurface },
                            ]}
                        >
                            {message.content}
                        </Text>
                        {message.timestamp && (
                            <Text
                                style={[
                                    styles.timestamp,
                                    { color: theme.colors.onSurfaceVariant },
                                ]}
                            >
                                {new Date(message.timestamp).toLocaleTimeString([], {
                                    hour: '2-digit',
                                    minute: '2-digit',
                                })}
                            </Text>
                        )}
                    </Surface>
                )}
            </TouchableOpacity>
        </Animated.View>
    );
};

const styles = StyleSheet.create({
    container: {
        marginVertical: spacing.xs,
        paddingHorizontal: spacing.md,
    },
    userContainer: {
        alignItems: 'flex-end',
    },
    assistantContainer: {
        alignItems: 'flex-start',
    },
    bubble: {
        paddingVertical: spacing.sm + 2,
        paddingHorizontal: spacing.md,
        maxWidth: '85%',
        borderRadius: borderRadius.lg,
    },
    userBubble: {
        borderBottomRightRadius: spacing.xs,
    },
    assistantBubble: {
        borderBottomLeftRadius: spacing.xs,
    },
    text: {
        fontSize: 16,
        lineHeight: 24,
        letterSpacing: 0.2,
    },
    userText: {
        color: '#FFFFFF',
        fontWeight: '500',
    },
    timestamp: {
        fontSize: 11,
        marginTop: spacing.xs,
        fontWeight: '400',
    },
    userTimestamp: {
        color: 'rgba(255, 255, 255, 0.75)',
    },
});
