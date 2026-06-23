'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { User } from '@/types/billing';

interface AuthContextType {
    user: User | null;
    loading: boolean;
    refreshUser: () => Promise<void>;
    logout: () => void;
}


const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    const refreshUser = useCallback(async () => {
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
            // Call main backend for ALL users (both org module and legacy JWTs)
            // Backend handles both JWT types automatically via get_current_user()
            const response = await fetch(`${API_BASE_URL}/users/me?t=${Date.now()}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const userData = await response.json();
                setUser(userData);
                localStorage.setItem('user', JSON.stringify(userData));
            } else {
                // Token invalid/expired, or backend rejected the request — don't trust the stale cache
                localStorage.removeItem('auth_token');
                localStorage.removeItem('user');
                setUser(null);
            }
        } catch (error) {
            // Backend unreachable — can't verify the session, so don't keep showing a stale logged-in state
            console.error('Error refreshing user:', error);
            localStorage.removeItem('auth_token');
            localStorage.removeItem('user');
            setUser(null);
        }
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        setUser(null);
    }, []);

    useEffect(() => {
        const initializeAuth = async () => {
            const storedUser = localStorage.getItem('user');
            if (storedUser) {
                try {
                    setUser(JSON.parse(storedUser));
                } catch (e) {
                    console.error('Error parsing stored user:', e);
                }
            }

            try {
                await refreshUser();
            } finally {
                setLoading(false);
            }
        };

        initializeAuth();
    }, []);

    return (
        <AuthContext.Provider value={{ user, loading, refreshUser, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useUser() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useUser must be used within an AuthProvider');
    }
    return context;
}

export const useAuth = useUser;
