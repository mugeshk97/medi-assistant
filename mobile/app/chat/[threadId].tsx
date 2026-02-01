import React, { useEffect, useRef } from 'react';
import { View, FlatList, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { Appbar, useTheme } from 'react-native-paper';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { useChat } from '../../src/context/ChatContext';
import { ChatBubble } from '../../src/components/ChatBubble';
import { MessageInput } from '../../src/components/MessageInput';
import { TypingIndicator } from '../../src/components/TypingIndicator';
import { EmptyState } from '../../src/components/EmptyState';
import { Message } from '../../src/types';
import { spacing } from '../../src/config/theme';

export default function ChatScreen() {
    const theme = useTheme();
    const router = useRouter();
    const { threadId } = useLocalSearchParams();
    const { messages, sendMessage, isLoading, streamingMessage, currentThreadId, threads } = useChat();
    const flatListRef = useRef<FlatList>(null);

    // Get thread title
    const thread = threads.find(t => t.thread_id === currentThreadId);
    const threadTitle = thread?.title || 'New Chat';

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (messages.length > 0 || streamingMessage) {
            setTimeout(() => {
                flatListRef.current?.scrollToEnd({ animated: true });
            }, 100);
        }
    }, [messages, streamingMessage]);

    const handleSendMessage = async (content: string) => {
        await sendMessage(content);
    };

    // Combine regular messages with streaming message
    const displayMessages = [...messages];
    if (streamingMessage) {
        displayMessages.push({
            role: 'assistant',
            content: streamingMessage,
            timestamp: new Date().toISOString(),
        } as Message);
    }

    return (
        <KeyboardAvoidingView
            style={[styles.container, { backgroundColor: theme.colors.background }]}
            behavior={Platform.OS === 'ios' ? 'padding' : undefined}
            keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 0}
        >
            <Appbar.Header elevated>
                <Appbar.BackAction onPress={() => router.back()} />
                <Appbar.Content title={threadTitle} />
            </Appbar.Header>

            {displayMessages.length === 0 && !isLoading ? (
                <EmptyState
                    icon="robot-outline"
                    title="Start a conversation"
                    message="Ask me anything about your health and medical concerns"
                />
            ) : (
                <FlatList
                    ref={flatListRef}
                    data={displayMessages}
                    keyExtractor={(item, index) => `${item.role}-${index}`}
                    renderItem={({ item }) => <ChatBubble message={item} />}
                    contentContainerStyle={styles.messageList}
                    onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
                />
            )}

            {isLoading && !streamingMessage && <TypingIndicator />}

            <MessageInput onSend={handleSendMessage} disabled={isLoading} />
        </KeyboardAvoidingView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    messageList: {
        paddingVertical: spacing.md,
        flexGrow: 1,
    },
});
