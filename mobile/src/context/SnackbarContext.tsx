import React, { useState } from 'react';
import { Snackbar } from 'react-native-paper';
import { useTheme } from 'react-native-paper';

type SnackbarType = 'success' | 'error' | 'info';

interface SnackbarContextType {
    showSnackbar: (message: string, type?: SnackbarType) => void;
}

const SnackbarContext = React.createContext<SnackbarContextType | undefined>(undefined);

export const SnackbarProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [visible, setVisible] = useState(false);
    const [message, setMessage] = useState('');
    const [type, setType] = useState<SnackbarType>('info');
    const theme = useTheme();

    const showSnackbar = (msg: string, snackbarType: SnackbarType = 'info') => {
        setMessage(msg);
        setType(snackbarType);
        setVisible(true);
    };

    const onDismiss = () => setVisible(false);

    // Color based on type
    const backgroundColor =
        type === 'error'
            ? theme.colors.error
            : type === 'success'
                ? theme.colors.primary
                : theme.colors.inverseSurface;

    return (
        <SnackbarContext.Provider value={{ showSnackbar }}>
            {children}
            <Snackbar
                visible={visible}
                onDismiss={onDismiss}
                duration={3000}
                action={{
                    label: 'OK',
                    onPress: onDismiss,
                }}
                style={{ backgroundColor }}
            >
                {message}
            </Snackbar>
        </SnackbarContext.Provider>
    );
};

export const useSnackbar = () => {
    const context = React.useContext(SnackbarContext);
    if (!context) {
        throw new Error('useSnackbar must be used within a SnackbarProvider');
    }
    return context;
};
