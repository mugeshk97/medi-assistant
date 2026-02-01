import React, { useEffect, useState, useRef } from 'react';
import { FlatList, View, StyleSheet, RefreshControl, Animated } from 'react-native';
import { FAB, Appbar, useTheme, Dialog, Portal, Button, Snackbar, Text } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { useChat } from '../src/context/ChatContext';
import { ThreadListItem } from '../src/components/ThreadListItem';
import { EmptyState } from '../src/components/EmptyState';
import { spacing, colors } from '../src/config/theme';
import ProtectedRoute from '../src/components/ProtectedRoute';
import { lightImpact, notificationWarning } from '../src/utils/haptics';

function HomeScreenContent() {
    const theme = useTheme();
    const router = useRouter();
    const { threads, loadThreads, switchThread, createNewThread, deleteThread, isLoading, error } = useChat();
    const [deleteDialogVisible, setDeleteDialogVisible] = useState(false);
    const [threadToDelete, setThreadToDelete] = useState<string | null>(null);
    const fabRotation = useRef(new Animated.Value(0)).current;
    const fabScale = useRef(new Animated.Value(1)).current;

    useEffect(() => {
        loadThreads();
    }, []);

    const handleThreadPress = async (threadId: string) => {
        lightImpact();
        await switchThread(threadId);
        router.push(`/chat/${threadId}`);
    };

    const handleNewChat = () => {
        lightImpact();
        // Animate FAB
        Animated.parallel([
            Animated.sequence([
                Animated.timing(fabRotation, {
                    toValue: 1,
                    duration: 200,
                    useNativeDriver: true,
                }),
                Animated.timing(fabRotation, {
                    toValue: 0,
                    duration: 0,
                    useNativeDriver: true,
                }),
            ]),
            Animated.sequence([
                Animated.spring(fabScale, {
                    toValue: 0.9,
                    useNativeDriver: true,
                }),
                Animated.spring(fabScale, {
                    toValue: 1,
                    friction: 3,
                    useNativeDriver: true,
                }),
            ]),
        ]).start();

        createNewThread();
        router.push(`/chat/new`);
    };

    const handleDeletePress = (threadId: string) => {
        notificationWarning();
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

    const rotation = fabRotation.interpolate({
        inputRange: [0, 1],
        outputRange: ['0deg', '135deg'],
    });

    return (
        <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
            {/* Gradient Header */}
            <LinearGradient
                colors={[colors.primaryMain, colors.secondaryMain]}
                start={{ x: 0, y: 0 }}
                end={{ x: 1, y: 0 }}
                style={styles.headerGradient}
            >
                <Appbar.Header style={styles.transparentHeader}>
                    <Appbar.Content
                        title="MediAssistant"
                        titleStyle={styles.headerTitle}
                    />
                    <Appbar.Action
                        icon="cog"
                        onPress={() => {
                            lightImpact();
                            router.push('/settings');
                        }}
                        iconColor="#FFFFFF"
                    />
                </Appbar.Header>
            </LinearGradient>

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
                    renderItem={({ item, index }) => (
                        <ThreadListItem
                            thread={item}
                            index={index}
                            onPress={() => handleThreadPress(item.thread_id)}
                            onDelete={() => handleDeletePress(item.thread_id)}
                        />
                    )}
                    contentContainerStyle={styles.listContent}
                    refreshControl={
                        <RefreshControl
                            refreshing={isLoading}
                            onRefresh={loadThreads}
                            colors={[colors.primaryMain]}
                            tintColor={colors.primaryMain}
                        />
                    }
                />
            )}

            <Animated.View
                style={{
                    transform: [
                        { rotate: rotation },
                        { scale: fabScale },
                    ],
                }}
            >
                <FAB
                    icon="plus"
                    style={[styles.fab]}
                    onPress={handleNewChat}
                    label="New Chat"
                    color="#FFFFFF"
                    customSize={56}
                />
            </Animated.View>

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
    headerGradient: {
        elevation: 4,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    transparentHeader: {
        backgroundColor: 'transparent',
        elevation: 0,
    },
    headerTitle: {
        color: '#FFFFFF',
        fontWeight: '700',
        fontSize: 20,
    },
    listContent: {
        paddingVertical: spacing.sm,
    },
    fab: {
        position: 'absolute',
        right: spacing.md,
        bottom: spacing.md,
        backgroundColor: colors.primaryMain,
    },
});

export default function HomeScreen() {
    return (
        <ProtectedRoute>
            <HomeScreenContent />
        </ProtectedRoute>
    );
}
