import React, { useEffect, useState } from 'react';
import { FlatList, View, StyleSheet, RefreshControl } from 'react-native';
import { FAB, Appbar, useTheme, Dialog, Portal, Button, Snackbar, Text } from 'react-native-paper';
import { useRouter } from 'expo-router';
import { useChat } from '../src/context/ChatContext';
import { ThreadListItem } from '../src/components/ThreadListItem';
import { EmptyState } from '../src/components/EmptyState';
import { spacing } from '../src/config/theme';
import ProtectedRoute from '../src/components/ProtectedRoute';

function HomeScreenContent() {
    const theme = useTheme();
    const router = useRouter();
    const { threads, loadThreads, switchThread, createNewThread, deleteThread, isLoading, error } = useChat();
    const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
    const [threadToDelete, setThreadToDelete] = useState<string | null>(null);

    useEffect(() => {
        loadThreads();
    }, []);

    const handleThreadPress = async (threadId: string) => {
        await switchThread(threadId);
        router.push(`/chat/${threadId}`);
    };

    const handleNewChat = () => {
        createNewThread();
        router.push(`/chat/new`);
    };

    const handleDeletePress = (threadId: string) => {
        setThreadToDelete(threadId);
        setDeleteDialogVisible(true);
    };

    const confirmDelete = async () => {
        if (threadToDelete) {
            try {
                await deleteThread(threadToDelete);
            } catch (error) {
                // Error is handled in ChatContext
            }
        }
        setDeleteDialogVisible(false);
        setThreadToDelete(null);
    };

    const cancelDelete = () => {
        setDeleteDialogVisible(false);
        setThreadToDelete(null);
    };

    return (
        <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
            <Appbar.Header elevated>
                <Appbar.Content title="MediAssistant" />
                <Appbar.Action icon="cog" onPress={() => router.push('/settings')} />
            </Appbar.Header>

            {threads.length === 0 && !isLoading ? (
                <EmptyState
                    icon="chat-outline"
                    title="No conversations yet"
                    message="Start a new chat to get medical assistance"
                />
            ) : (
                <FlatList
                    data={threads}
                    keyExtractor={(item) => item.thread_id}
                    renderItem={({ item }) => (
                        <ThreadListItem
                            thread={item}
                            onPress={() => handleThreadPress(item.thread_id)}
                            onDelete={() => handleDeletePress(item.thread_id)}
                        />
                    )}
                    contentContainerStyle={styles.listContent}
                    refreshControl={
                        <RefreshControl
                            refreshing={isLoading}
                            onRefresh={loadThreads}
                            colors={[theme.colors.primary]}
                        />
                    }
                />
            )}

            <FAB
                icon="plus"
                style={[styles.fab, { backgroundColor: theme.colors.primary }]}
                onPress={handleNewChat}
                label="New Chat"
            />

            <Portal>
                <Dialog visible={deleteDialogVisible} onDismiss={cancelDelete}>
                    <Dialog.Title>Delete Chat?</Dialog.Title>
                    <Dialog.Content>
                        <Text>This conversation will be permanently deleted.</Text>
                    </Dialog.Content>
                    <Dialog.Actions>
                        <Button onPress={cancelDelete}>Cancel</Button>
                        <Button onPress={confirmDelete} textColor={theme.colors.error}>
                            Delete
                        </Button>
                    </Dialog.Actions>
                </Dialog>
            </Portal>

            {error && (
                <Snackbar
                    visible={!!error}
                    onDismiss={() => { }}
                    duration={3000}
                    action={{
                        label: 'Dismiss',
                        onPress: () => { },
                    }}
                >
                    {error}
                </Snackbar>
            )}
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    listContent: {
        paddingVertical: spacing.sm,
    },
    fab: {
        position: 'absolute',
        right: spacing.md,
        bottom: spacing.md,
    },
});

export default function HomeScreen() {
    return (
        <ProtectedRoute>
            <HomeScreenContent />
        </ProtectedRoute>
    );
}

