import AsyncStorage from '@react-native-async-storage/async-storage';

export interface Settings {
    theme?: 'light' | 'dark';
    [key: string]: any;  // Allow additional settings
}

const STORAGE_KEYS = {
    USER_ID: '@medi_assistant_user_id',
    SETTINGS: '@medi_assistant_settings',
};

export const StorageService = {
    async getUserId(): Promise<string | null> {
        try {
            return await AsyncStorage.getItem(STORAGE_KEYS.USER_ID);
        } catch (error) {
            console.error('Error getting user ID:', error);
            return null;
        }
    },

    async setUserId(userId: string): Promise<void> {
        try {
            await AsyncStorage.setItem(STORAGE_KEYS.USER_ID, userId);
        } catch (error) {
            console.error('Error setting user ID:', error);
        }
    },

    async getSettings(): Promise<Settings> {
        try {
            const settings = await AsyncStorage.getItem(STORAGE_KEYS.SETTINGS);
            return settings ? JSON.parse(settings) : {};
        } catch (error) {
            console.error('Error getting settings:', error);
            return {};
        }
    },

    async setSettings(settings: Settings): Promise<void> {
        try {
            await AsyncStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(settings));
        } catch (error) {
            console.error('Error setting settings:', error);
        }
    },

    async clear(): Promise<void> {
        try {
            await AsyncStorage.clear();
        } catch (error) {
            console.error('Error clearing storage:', error);
        }
    },
};
