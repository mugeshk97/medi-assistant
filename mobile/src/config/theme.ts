import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';

const lightTheme = {
    ...MD3LightTheme,
    colors: {
        ...MD3LightTheme.colors,
        primary: '#6750A4',
        secondary: '#625B71',
        tertiary: '#7D5260',
        background: '#F8F9FA',
        surface: '#FFFFFF',
        surfaceVariant: '#E7E0EC',
        error: '#B3261E',
        onPrimary: '#FFFFFF',
        onSecondary: '#FFFFFF',
        onBackground: '#1C1B1F',
        onSurface: '#1C1B1F',
        onSurfaceVariant: '#49454F',
        outline: '#79747E',
        outlineVariant: '#CAC4D0',
        elevation: {
            level0: 'transparent',
            level1: '#F3EDF7',
            level2: '#EEE8F2',
            level3: '#E9E3ED',
            level4: '#E7E1EB',
            level5: '#E3DDE7',
        },
    },
};

const darkTheme = {
    ...MD3DarkTheme,
    colors: {
        ...MD3DarkTheme.colors,
        primary: '#D0BCFF',
        secondary: '#CCC2DC',
        tertiary: '#EFB8C8',
        background: '#1C1B1F',
        surface: '#1C1B1F',
        surfaceVariant: '#49454F',
        error: '#F2B8B5',
        onPrimary: '#381E72',
        onSecondary: '#332D41',
        onBackground: '#E6E1E5',
        onSurface: '#E6E1E5',
        onSurfaceVariant: '#CAC4D0',
        outline: '#938F99',
        outlineVariant: '#49454F',
        elevation: {
            level0: 'transparent',
            level1: '#242228',
            level2: '#2A272F',
            level3: '#302C36',
            level4: '#33303A',
            level5: '#37343E',
        },
    },
};

export const spacing = {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
    xxl: 48,
};

export const borderRadius = {
    sm: 4,
    md: 8,
    lg: 16,
    xl: 24,
    full: 9999,
};

export { lightTheme, darkTheme };
