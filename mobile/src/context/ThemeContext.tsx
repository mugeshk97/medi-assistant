import React, { createContext, useContext, useState, useEffect } from 'react';
import { StorageService } from '../utils/storage';

type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
    isDark: boolean;
    themeMode: ThemeMode;
    toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

const THEME_STORAGE_KEY = '@medi_assistant_theme';

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [themeMode, setThemeMode] = useState<ThemeMode>('light');
    const [isLoading, setIsLoading] = useState(true);

    // Load theme preference on mount
    useEffect(() => {
        const loadTheme = async () => {
            try {
                const settings = await StorageService.getSettings();
                const savedTheme = settings.theme as ThemeMode | undefined;
                if (savedTheme) {
                    setThemeMode(savedTheme);
                }
            } catch (error) {
                console.error('Error loading theme:', error);
            } finally {
                setIsLoading(false);
            }
        };

        loadTheme();
    }, []);

    const toggleTheme = async () => {
        const newTheme: ThemeMode = themeMode === 'light' ? 'dark' : 'light';
        setThemeMode(newTheme);

        try {
            const settings = await StorageService.getSettings();
            await StorageService.setSettings({ ...settings, theme: newTheme });
        } catch (error) {
            console.error('Error saving theme:', error);
        }
    };

    if (isLoading) {
        return null; // or a loading screen
    }

    return (
        <ThemeContext.Provider
            value={{
                isDark: themeMode === 'dark',
                themeMode,
                toggleTheme,
            }}
        >
            {children}
        </ThemeContext.Provider>
    );
};

export const useThemeMode = () => {
    const context = useContext(ThemeContext);
    if (!context) {
        throw new Error('useThemeMode must be used within a ThemeProvider');
    }
    return context;
};
