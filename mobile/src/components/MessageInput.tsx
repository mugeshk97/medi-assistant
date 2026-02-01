import React, { useState, useRef } from 'react';
import { View, TextInput, StyleSheet, KeyboardAvoidingView, Platform, Animated } from 'react-native';
import { IconButton, useTheme, Text } from 'react-native-paper';
import { BlurView } from 'expo-blur';
import { spacing, borderRadius, shadows, colors } from '../config/theme';
import { mediumImpact, notificationSuccess } from '../utils/haptics';

interface MessageInputProps {
    onSend: (message: string) => void;
    disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled }) => {
    const [message, setMessage] = useState('');
    const [isFocused, setIsFocused] = useState(false);
    const theme = useTheme();
    const scaleAnim = useRef(new Animated.Value(1)).current;
    const focusAnim = useRef(new Animated.Value(0)).current;

    const MAX_LENGTH = 2000;
    const SHOW_COUNTER_AT = 1800;
    const showCounter = message.length >= SHOW_COUNTER_AT;

    const handleSend = () => {
        if (!message.trim() || disabled) {
            return;
        }

        if (message.length > MAX_LENGTH) {
            return;
        }

        const sanitizedMessage = message.trim().replace(/\s+/g, ' ');

        // Button press animation
        Animated.sequence([
            Animated.spring(scaleAnim, {
                toValue: 0.9,
                useNativeDriver: true,
            }),
            Animated.spring(scaleAnim, {
                toValue: 1,
                friction: 3,
                useNativeDriver: true,
            }),
        ]).start();

        notificationSuccess();
        onSend(sanitizedMessage);
        setMessage('');
    };

    const handleFocus = () => {
        setIsFocused(true);
        Animated.timing(focusAnim, {
            toValue: 1,
            duration: 200,
            useNativeDriver: false,
        }).start();
    };

    const handleBlur = () => {
        setIsFocused(false);
        Animated.timing(focusAnim, {
            toValue: 0,
            duration: 200,
            useNativeDriver: false,
        }).start();
    };

    const borderColor = focusAnim.interpolate({
        inputRange: [0, 1],
        outputRange: [theme.colors.outline, colors.primaryMain],
    });

    return (
        <KeyboardAvoidingView
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
        >
            <View style={[styles.container, { backgroundColor: theme.colors.surface }]}>
                <Animated.View
                    style={[
                        styles.inputContainer,
                        {
                            backgroundColor: theme.colors.surfaceVariant,
                            borderColor: borderColor,
                            borderWidth: 2,
                            ...shadows.sm,
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
                        onFocus={handleFocus}
                        onBlur={handleBlur}
                        multiline
                        maxLength={MAX_LENGTH}
                        editable={!disabled}
                        onSubmitEditing={handleSend}
                        blurOnSubmit={false}
                    />
                    <View style={styles.actionsContainer}>
                        {showCounter && (
                            <Text
                                style={[
                                    styles.counter,
                                    {
                                        color:
                                            message.length >= MAX_LENGTH
                                                ? theme.colors.error
                                                : theme.colors.onSurfaceVariant,
                                    },
                                ]}
                            >
                                {message.length}/{MAX_LENGTH}
                            </Text>
                        )}
                        <Animated.View style={{ transform: [{ scale: scaleAnim }] }}>
                            <IconButton
                                icon="send"
                                size={24}
                                iconColor={
                                    message.trim() && !disabled
                                        ? colors.primaryMain
                                        : theme.colors.outline
                                }
                                onPress={() => {
                                    mediumImpact();
                                    handleSend();
                                }}
                                disabled={!message.trim() || disabled}
                                style={styles.sendButton}
                            />
                        </Animated.View>
                    </View>
                </Animated.View>
            </View>
        </KeyboardAvoidingView>
    );
};

const styles = StyleSheet.create({
    container: {
        paddingHorizontal: spacing.md,
        paddingVertical: spacing.sm,
        borderTopWidth: 1,
        borderTopColor: 'rgba(0, 0, 0, 0.05)',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'flex-end',
        borderRadius: borderRadius.xl,
        paddingLeft: spacing.md,
        minHeight: 52,
        maxHeight: 120,
    },
    input: {
        flex: 1,
        fontSize: 16,
        paddingVertical: spacing.md,
        maxHeight: 100,
        lineHeight: 22,
    },
    actionsContainer: {
        alignItems: 'center',
        justifyContent: 'flex-end',
        paddingBottom: spacing.xs,
    },
    counter: {
        fontSize: 11,
        marginBottom: spacing.xs,
        fontWeight: '500',
    },
    sendButton: {
        margin: 0,
    },
});
