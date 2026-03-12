import React, { createContext, useState, useContext, useEffect } from 'react';
import authService from '../services/authService';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const hasToken = !!authService.getAccessToken();

    useEffect(() => {
        const currentUser = authService.getCurrentUser();
        if (currentUser) {
            setUser(currentUser);
        } else {
            setUser(null);
        }
        setLoading(false);
    }, []);

    const login = async (email, password) => {
        try {
            const data = await authService.login(email, password);
            setUser(data.user);
            return { success: true, message: data.message };
        } catch (error) {
            return {
                success: false,
                message: error.response?.data?.error || 'Login failed'
            };
        }
    };

    const register = async (dataOrEmail, password, password2) => {
        try {
            const payload = typeof dataOrEmail === 'object'
                ? dataOrEmail
                : { email: dataOrEmail, password, password2 };

            const data = await authService.register(payload);
            setUser(data.user);
            return { success: true, message: data.message };
        } catch (error) {
            const responseData = error.response?.data;
            const fieldOrder = ['email', 'password', 'password2', 'age', 'goal', 'level'];

            let errorMsg = 'Registration failed';
            for (const field of fieldOrder) {
                const fieldError = responseData?.[field];
                if (Array.isArray(fieldError) && fieldError.length > 0) {
                    errorMsg = fieldError[0];
                    break;
                }
                if (typeof fieldError === 'string') {
                    errorMsg = fieldError;
                    break;
                }
            }

            if (errorMsg === 'Registration failed') {
                errorMsg = responseData?.error || errorMsg;
            }

            return { success: false, message: errorMsg };
        }
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    const value = {
        user,
        setUser,
        login,
        register,
        logout,
        loading,
        isAuthenticated: !!user && hasToken
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
