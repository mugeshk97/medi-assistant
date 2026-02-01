import React, { useState } from 'react';
import { View, TextInput, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { IconButton, useTheme } from 'react-native-paper';
import { spacing, borderRadius } from '../config/theme';

interface MessageInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled }) => {
    const [message, setMessage] = useState('');
    const theme = useTheme();

    const handleSend = () => {
        if (!message.trim() || disabled) {
            return; // Don't send empty messages
        }

        // Validate message length (already enforced by maxLength, but double-check)
        if (message.length > 2000) {
            return;
        }

        // Sanitize input - trim and normalize whitespace
        const sanitizedMessage = message.trim().replace(/\s+/g, ' ');

        onSend(sanitizedMessage);
        setMessage('');
    };

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
        >
            <View style={[styles.container, { backgroundColor: theme.colors.surface }]}>
                <View
                    style={[
                        styles.inputContainer,
                        {
                            backgroundColor: theme.colors.surfaceVariant,
                            borderColor: theme.colors.outline,
                        },
                    ]}
                >
                    <TextInput
                        style={[
                            styles.input,
                            { color: theme.colors.onSurface },
                        ]}
                        placeholder="Type your message..."
                        placeholderTextColor={theme.colors.onSurfaceVariant}
                        value={message}
                        onChangeText={setMessage}
                        multiline
                        maxLength={2000}
                        editable={!disabled}
                        onSubmitEditing={handleSend}
                        blurOnSubmit={false}
                    />
                    <IconButton
                        icon="send"
                        size={24}
                        iconColor={message.trim() && !disabled ? theme.colors.primary : theme.colors.outline}
                        onPress={handleSend}
                        disabled={!message.trim() || disabled}
                        style={styles.sendButton}
                    />
                </View>
            </View>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        paddingHorizontal: spacing.md,
        paddingVertical: spacing.sm,
        borderTopWidth: 1,
        borderTopColor: 'rgba(0, 0, 0, 0.1)',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        borderRadius: borderRadius.xl,
        paddingLeft: spacing.md,
        minHeight: 48,
        maxHeight: 120,
    },
    input: {
        flex: 1,
        fontSize: 16,
        paddingVertical: spacing.sm + 2,
        maxHeight: 100,
    },
    sendButton: {
        margin: 0,
    },
});
