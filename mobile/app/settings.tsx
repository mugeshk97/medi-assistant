import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { List, Switch, Button, Divider, Text, useTheme } from 'react-native-paper';
import { router } from 'expo-router';
import { useThemeMode } from '../src/context/ThemeContext';
import { useAuth } from '../src/context/AuthContext';
import { useSnackbar } from '../src/context/SnackbarContext';

export default function SettingsScreen() {
    const theme = useTheme();
    const { isDark, toggleTheme } = useThemeMode();
    const { user, logout } = useAuth();
    const { showSnackbar } = useSnackbar();

    const handleLogout = async () => {
        try {
            await logout();
            showSnackbar('Logged out successfully', 'success');
            router.replace('/auth/login');
        } catch (error) {
            showSnackbar('Logout failed', 'error');
        }
    };

    return (
        <ScrollView style={[styles.container, { backgroundColor: theme.colors.background }]}>
            <View style={styles.header}>
                <Text variant="headlineMedium" style={styles.headerText}>
                    Settings
                </Text>
            </View>

            {/* User Info Section */}
            {user && (
                <>
                    <List.Section>
                        <List.Subheader>Account</List.Subheader>
                        <List.Item
                            title={user.username}
                            description={user.email}
                            left={(props) => <List.Icon {...props} icon="account" />}
                        />
                    </List.Section>
                    <Divider />
                </>
            )}

            {/* Appearance Section */}
            <List.Section>
                <List.Subheader>Appearance</List.Subheader>
                <List.Item
                    title="Dark Mode"
                    description="Toggle dark/light theme"
                    left={(props) => <List.Icon {...props} icon="theme-light-dark" />}
                    right={() => (
                        <Switch value={isDark} onValueChange={toggleTheme} />
                    )}
                />
            </List.Section>
            <Divider />

            {/* About Section */}
            <List.Section>
                <List.Subheader>About</List.Subheader>
                <List.Item
                    title="Version"
                    description="1.0.0"
                    left={(props) => <List.Icon {...props} icon="information" />}
                />
            </List.Section>
            <Divider />

            {/* Logout Button */}
            {user && (
                <View style={styles.logoutContainer}>
                    <Button
                        mode="outlined"
                        onPress={handleLogout}
                        icon="logout"
                        style={styles.logoutButton}
                        textColor={theme.colors.error}
                    >
                        Logout
                    </Button>
                </View>
            )}
        </ScrollView>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
    },
    header: {
        padding: 20,
        paddingTop: 60,
    },
    headerText: {
        fontWeight: 'bold',
    },
    logoutContainer: {
        padding: 20,
        paddingTop: 40,
    },
    logoutButton: {
        borderColor: 'red',
    },
});
