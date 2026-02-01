import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';

// Modern medical-themed color palette
const colors = {
    // Primary: Vibrant teal gradient
    primaryLight: '#06B6D4',
    primaryMain: '#0891B2',
    primaryDark: '#0E7490',

    // Secondary: Complementary blue
    secondaryLight: '#3B82F6',
    secondaryMain: '#2563EB',
    secondaryDark: '#1D4ED8',

    // Accent: Warm orange for highlights
    accentLight: '#FB923C',
    accentMain: '#F97316',
    accentDark: '#EA580C',

    // Success: Medical green
    success: '#10B981',

    // Error: Warm red
    error: '#EF4444',

    // Neutral grays
    gray50: '#F9FAFB',
    gray100: '#F3F4F6',
    gray200: '#E5E7EB',
    gray300: '#D1D5DB',
    gray400: '#9CA3AF',
    gray500: '#6B7280',
    gray600: '#4B5563',
    gray700: '#374151',
    gray800: '#1F2937',
    gray900: '#111827',
};

const lightTheme = {
    ...MD3LightTheme,
    colors: {
        ...MD3LightTheme.colors,
        primary: colors.primaryMain,
        primaryContainer: colors.primaryLight,
        secondary: colors.secondaryMain,
        secondaryContainer: colors.secondaryLight,
        tertiary: colors.accentMain,
        tertiaryContainer: colors.accentLight,
        background: colors.gray50,
        surface: '#FFFFFF',
        surfaceVariant: colors.gray100,
        error: colors.error,
        onPrimary: '#FFFFFF',
        onSecondary: '#FFFFFF',
        onTertiary: '#FFFFFF',
        onBackground: colors.gray900,
        onSurface: colors.gray900,
        onSurfaceVariant: colors.gray600,
        outline: colors.gray300,
        outlineVariant: colors.gray200,
        elevation: {
            level0: 'transparent',
            level1: '#FFFFFF',
            level2: '#FAFAFA',
            level3: '#F5F5F5',
            level4: '#F0F0F0',
            level5: '#EBEBEB',
        },
        // Custom additions
        success: colors.success,
        surfaceGradientStart: colors.primaryLight + '15',
        surfaceGradientEnd: colors.secondaryLight + '10',
    },
};

const darkTheme = {
    ...MD3DarkTheme,
    colors: {
        ...MD3DarkTheme.colors,
        primary: colors.primaryLight,
        primaryContainer: colors.primaryDark,
        secondary: colors.secondaryLight,
        secondaryContainer: colors.secondaryDark,
        tertiary: colors.accentLight,
        tertiaryContainer: colors.accentDark,
        background: colors.gray900,
        surface: colors.gray800,
        surfaceVariant: colors.gray700,
        error: colors.error,
        onPrimary: colors.gray900,
        onSecondary: colors.gray900,
        onTertiary: colors.gray900,
        onBackground: colors.gray50,
        onSurface: colors.gray50,
        onSurfaceVariant: colors.gray400,
        outline: colors.gray600,
        outlineVariant: colors.gray700,
        elevation: {
            level0: 'transparent',
            level1: '#1E293B',
            level2: '#253345',
            level3: '#2D3E50',
            level4: '#324252',
            level5: '#394A5C',
        },
        // Custom additions
        success: colors.success,
        surfaceGradientStart: colors.primaryDark + '20',
        surfaceGradientEnd: colors.secondaryDark + '15',
    },
};

// Spacing system
export const spacing = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
    xxxl: 64,
};

// Border radius tokens
export const borderRadius = {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
    full: 9999,
};

// Typography system
export const typography = {
    fontFamily: {
        regular: 'Inter_400Regular',
        medium: 'Inter_500Medium',
        semiBold: 'Inter_600SemiBold',
        bold: 'Inter_700Bold',
        heading: 'PlusJakartaSans_700Bold',
    },
    fontSize: {
        xs: 12,
        sm: 14,
        md: 16,
        lg: 18,
        xl: 20,
        xxl: 24,
        xxxl: 32,
    },
    lineHeight: {
        tight: 1.2,
        normal: 1.5,
        relaxed: 1.75,
    },
};

// Animation timing
export const animations = {
    duration: {
        fast: 150,
        normal: 250,
        slow: 350,
        slower: 500,
    },
    easing: {
        easeIn: 'ease-in',
        easeOut: 'ease-out',
        easeInOut: 'ease-in-out',
        spring: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
    },
};

// Shadow presets
export const shadows = {
    sm: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 2,
        elevation: 2,
    },
    md: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 4,
    },
    lg: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.15,
        shadowRadius: 8,
        elevation: 8,
    },
    xl: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.2,
        shadowRadius: 16,
        elevation: 12,
    },
};

export { lightTheme, darkTheme, colors };
