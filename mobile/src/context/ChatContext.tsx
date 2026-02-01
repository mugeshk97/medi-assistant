import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import ApiService from '../services/api';
import { Thread, Message as MessageType, ChatRequest } from '../types';
import { useAuth } from './AuthContext';

interface ChatContextType {
    threads: Thread[];
    currentThreadId: string | null;
    messages: MessageType[];
    isLoading: boolean;
    error: string | null;
    streamingMessage: string;
    loadThreads: () => Promise<void>;
    switchThread: (threadId: string) => Promise<void>;
    createNewThread: () => string;
    deleteThread: (threadId: string) => Promise<void>;
    sendMessage: (message: string, onChunk?: (chunk: string) => void) => Promise<void>;
    clearError: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [threads, setThreads] = useState<Thread[]>([]);
    const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
    const [messages, setMessages] = useState<MessageType[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [streamingMessage, setStreamingMessage] = useState<string>('');
    const { isAuthenticated } = useAuth();

    // Load threads only when authenticated
    useEffect(() => {
        if (isAuthenticated) {
            loadThreads();
        }
    }, [isAuthenticated]);

    const clearError = () => setError(null);

    const loadThreads = async () => {
        if (!isAuthenticated) return;

        try {
            setIsLoading(true);
            setError(null);
            const fetchedThreads = await ApiService.getThreads();
            setThreads(fetchedThreads.sort((a, b) =>
                new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
            ));
        } catch (err: any) {
            setError(err.message || 'Failed to load threads');
            console.error('Error loading threads:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const switchThread = async (threadId: string) => {
        if (!isAuthenticated) return;

        try {
            setCurrentThreadId(threadId);
            setIsLoading(true);
            setError(null);
            const history = await ApiService.getChatHistory(threadId);
            setMessages(history.messages);
        } catch (err: any) {
            setError(err.message || 'Failed to load chat history');
            console.error('Error switching thread:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const createNewThread = () => {
        const newThreadId = `thread-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
        setCurrentThreadId(newThreadId);
        setMessages([]);
        return newThreadId;
    };

    const sendMessage = async (message: string, onChunk?: (chunk: string) => void) => {
        if (!currentThreadId || !isAuthenticated) return;

        const userMessage: MessageType = {
            role: 'user',
            content: message,
            timestamp: new Date().toISOString(),
        };

        // Add user message immediately
        setMessages((prev) => [...prev, userMessage]);
        setIsLoading(true);
        setError(null);

        try {
            let fullResponse = '';

            const request: Omit<ChatRequest, 'user_id'> = {
                message,
                thread_id: currentThreadId,
            };

            await ApiService.sendMessage(request, (chunk) => {
                fullResponse += chunk;
                setStreamingMessage(fullResponse);
                if (onChunk) {
                    onChunk(fullResponse);
                }
            });

            // Add complete assistant message
            const assistantMessage: MessageType = {
                role: 'assistant',
                content: fullResponse,
                timestamp: new Date().toISOString(),
            };

            setMessages((prev) => [...prev, assistantMessage]);
            setStreamingMessage('');

            // Reload threads to get updated list with new thread title
            // Non-blocking: errors are logged but don't fail the message send
            try {
                await loadThreads();
            } catch (reloadError) {
                console.error('Failed to reload threads after message:', reloadError);
                // Don't throw - message was sent successfully
            }
        } catch (err: any) {
            setError(err.message || 'Failed to send message');
            console.error('Error sending message:', err);
            setStreamingMessage('');
        } finally {
            setIsLoading(false);
        }
    };

    const deleteThread = async (threadId: string) => {
        if (!isAuthenticated) return;

        try {
            setError(null);
            await ApiService.deleteThread(threadId);

            // Remove from local state
            setThreads((prev) => prev.filter((t) => t.thread_id !== threadId));

            // If deleting current thread, clear messages
            if (threadId === currentThreadId) {
                setCurrentThreadId(null);
                setMessages([]);
            }
        } catch (err: any) {
            setError(err.message || 'Failed to delete thread');
            console.error('Error deleting thread:', err);
            throw err;
        }
    };

    return (
        <ChatContext.Provider
            value={{
                threads,
                currentThreadId,
                messages,
                isLoading,
                error,
                streamingMessage,
                loadThreads,
                switchThread,
                createNewThread,
                deleteThread,
                sendMessage,
                clearError,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};

export const useChat = () => {
    const context = useContext(ChatContext);
    if (!context) {
        throw new Error('useChat must be used within a ChatProvider');
    }
    return context;
};
