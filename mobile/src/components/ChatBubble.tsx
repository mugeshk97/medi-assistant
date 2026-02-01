import React from 'react';
import { View, StyleSheet, TouchableOpacity } from 'react-native';
import { Text, Surface, useTheme } from 'react-native-paper';
import * as Clipboard from 'expo-clipboard';
import { Message } from '../types';
import { spacing, borderRadius } from '../config/theme';
import { useSnackbar } from '../context/SnackbarContext';

interface ChatBubbleProps {
    message: Message;
}

export const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
    const theme = useTheme();
    const { showSnackbar } = useSnackbar();
    const isUser = message.role === 'user';

    const handleLongPress = async () => {
        await Clipboard.setStringAsync(message.content);
        showSnackbar('Message copied to clipboard');
    };

    return (
        <View
            style={[
                styles.container,
                isUser ? styles.userContainer : styles.assistantContainer,
            ]}
        >
            <TouchableOpacity
                onLongPress={handleLongPress}
                delayLongPress={500}
                activeOpacity={0.8}
            >
                <Surface
                    style={[
                        styles.bubble,
                        {
                            backgroundColor: isUser
                                ? theme.colors.primary
                                : theme.colors.surfaceVariant,
                            maxWidth: '80%',
                        },
                    ]}
                    elevation={1}
                >
                    <Text
                        style={[
                            styles.text,
                            { color: isUser ? theme.colors.onPrimary : theme.colors.onSurface },
                        ]}
                    >
                        {message.content}
                    </Text>
                    {message.timestamp && (
                        <Text
                            style={[
                                styles.timestamp,
                                {
                                    color: isUser
                                        ? theme.colors.onPrimary + '99'
                                        : theme.colors.onSurfaceVariant,
                                },
                            ]}
                        >
                            {new Date(message.timestamp).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                            })}
                        </Text>
                    )}
                </Surface>
            </TouchableOpacity>
        </View>
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
        paddingVertical: spacing.sm,
        paddingHorizontal: spacing.md,
        borderRadius: borderRadius.lg,
    },
    text: {
        fontSize: 16,
        lineHeight: 22,
    },
    timestamp: {
        fontSize: 11,
        marginTop: spacing.xs,
    },
});
