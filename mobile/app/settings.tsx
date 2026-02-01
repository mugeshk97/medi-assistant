import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { List, Switch, Button, Divider, Text, useTheme, Surface, Appbar } from 'react-native-paper';
import { LinearGradient } from 'expo-linear-gradient';
import { router } from 'expo-router';
import { useThemeMode } from '../src/context/ThemeContext';
import { useAuth } from '../src/context/AuthContext';
import { useSnackbar } from '../src/context/SnackbarContext';
import { spacing, borderRadius, shadows, colors } from '../src/config/theme';
import { lightImpact, notificationWarning } from '../src/utils/haptics';

export default function SettingsScreen() {
    const theme = useTheme();
    const { isDark, toggleTheme } = useThemeMode();
    const { user, logout } = useAuth();
    const { showSnackbar } = useSnackbar();

    const handleLogout = async () => {
        notificationWarning();
        try {
            await logout();
            showSnackbar('Logged out successfully', 'success');
            router.replace('/auth/login');
        } catch (error) {
            showSnackbar('Logout failed', 'error');
        }
    };

    const handleThemeToggle = () => {
        lightImpact();
        toggleTheme();
    };

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
                    <Appbar.BackAction
                        onPress={() => {
                            lightImpact();
                            router.back();
                        }}
                        iconColor="#FFFFFF"
                    />
                    <Appbar.Content
                        title="Settings"
                        titleStyle={styles.headerTitle}
                    />
                </Appbar.Header>
            </LinearGradient>

            <ScrollView style={styles.scrollView}>
                {/* User Info Section */}
                {user && (
                    <Surface style={[styles.card, shadows.sm]}>
                        <List.Section style={styles.section}>
                            <List.Subheader style={styles.sectionHeader}>Account</List.Subheader>
                            <List.Item
                                title={user.username}
                                titleStyle={styles.userName}
                                description={user.email}
                                descriptionStyle={styles.userEmail}
                                left={(props) => (
                                    <View style={styles.avatarContainer}>
                                        <LinearGradient
                                            colors={[colors.primaryLight, colors.secondaryLight]}
                                            start={{ x: 0, y: 0 }}
                                            end={{ x: 1, y: 1 }}
                                            style={styles.avatar}
                                        >
                                            <Text style={styles.avatarText}>
                                                {user.username?.charAt(0).toUpperCase() || 'U'}
                                            </Text>
                                        </LinearGradient>
                                    </View>
                                )}
                            />
                        </List.Section>
                    </Surface>
                )}

                {/* Appearance Section */}
                <Surface style={[styles.card, shadows.sm]}>
                    <List.Section style={styles.section}>
                        <List.Subheader style={styles.sectionHeader}>Appearance</List.Subheader>
                        <List.Item
                            title="Dark Mode"
                            description="Toggle dark/light theme"
                            left={(props) => <List.Icon {...props} icon="theme-light-dark" color={colors.primaryMain} />}
                            right={() => (
                                <Switch value={isDark} onValueChange={handleThemeToggle} />
                            )}
                        />
                    </List.Section>
                </Surface>

                {/* About Section */}
                <Surface style={[styles.card, shadows.sm]}>
                    <List.Section style={styles.section}>
                        <List.Subheader style={styles.sectionHeader}>About</List.Subheader>
                        <List.Item
                            title="Version"
                            description="1.0.0"
                            left={(props) => <List.Icon {...props} icon="information" color={colors.primaryMain} />}
                        />
                        <Divider />
                        <List.Item
                            title="MediAssistant"
                            description="AI-powered medical assistant"
                            left={(props) => <List.Icon {...props} icon="robot" color={colors.primaryMain} />}
                        />
                    </List.Section>
                </Surface>

                {/* Logout Button */}
                {user && (
                    <View style={styles.logoutContainer}>
                        <Button
                            mode="outlined"
                            onPress={handleLogout}
                            icon="logout"
                            style={[styles.logoutButton, { borderColor: theme.colors.error }]}
                            textColor={theme.colors.error}
                        >
                            Logout
                        </Button>
                    </View>
                )}
            </ScrollView>
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
        fontWeight: '600',
        fontSize: 18,
    },
    scrollView: {
        flex: 1,
    },
    card: {
        marginHorizontal: spacing.md,
        marginTop: spacing.md,
        borderRadius: borderRadius.md,
        overflow: 'hidden',
    },
    section: {
        marginBottom: 0,
    },
    sectionHeader: {
        fontWeight: '600',
        fontSize: 14,
        textTransform: 'uppercase',
        letterSpacing: 0.5,
    },
    avatarContainer: {
        justifyContent: 'center',
        paddingLeft: spacing.md,
    },
    avatar: {
        width: 48,
        height: 48,
        borderRadius: 24,
        alignItems: 'center',
        justifyContent: 'center',
    },
    avatarText: {
        color: '#FFFFFF',
        fontSize: 20,
        fontWeight: '700',
    },
    userName: {
        fontWeight: '600',
        fontSize: 16,
    },
    userEmail: {
        fontSize: 14,
    },
    logoutContainer: {
        padding: spacing.lg,
        paddingTop: spacing.xl,
        paddingBottom: spacing.xxl,
    },
    logoutButton: {
        borderWidth: 2,
    },
});
