import * as Haptics from 'expo-haptics';
import { Platform } from 'react-native';

/**
 * Haptic feedback helpers for enhanced tactile interactions
 */

// Light impact (subtle feedback)
export const lightImpact = () => {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    }
};

// Medium impact (standard feedback)
export const mediumImpact = () => {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
};

// Heavy impact (strong feedback)
export const heavyImpact = () => {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
    }
};

// Selection feedback (for picker/tab changes)
export const selectionFeedback = () => {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
        Haptics.selectionAsync();
    }
};

// Success notification
export const notificationSuccess = () => {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
};

// Warning notification
export const notificationWarning = () => {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    }
};

// Error notification
export const notificationError = () => {
    if (Platform.OS === 'ios' || Platform.OS === 'android') {
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
    }
};
