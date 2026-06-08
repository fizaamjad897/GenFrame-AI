'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

interface PageHeaderState {
    title: string;
    actionLabel?: string;
    onAction?: () => void;
    actionDisabled?: boolean;
    secondaryActionLabel?: string;
    onSecondaryAction?: () => void;
    simpleMode?: boolean;
    isSidebarOpen?: boolean;
    onToggleSidebar?: () => void;
    hideHeader?: boolean;
    icon?: React.ReactNode;
    onBack?: () => void;
    sidebarCollapsed?: boolean;
}

interface PageHeaderContextType {
    header: PageHeaderState;
    setHeader: (state: Partial<PageHeaderState>) => void;
    resetHeader: () => void;
}

const defaultHeader: PageHeaderState = {
    title: '',
};

const PageHeaderContext = createContext<PageHeaderContextType | undefined>(undefined);

export function PageHeaderProvider({ children }: { children: React.ReactNode }) {
    const [header, setHeaderState] = useState<PageHeaderState>(defaultHeader);

    const setHeader = useCallback((state: Partial<PageHeaderState>) => {
        setHeaderState(prev => ({ ...prev, ...state }));
    }, []);

    const resetHeader = useCallback(() => {
        setHeaderState(defaultHeader);
    }, []);

    return (
        <PageHeaderContext.Provider value={{ header, setHeader, resetHeader }}>
            {children}
        </PageHeaderContext.Provider>
    );
}

export function usePageHeader() {
    const context = useContext(PageHeaderContext);
    if (context === undefined) {
        throw new Error('usePageHeader must be used within a PageHeaderProvider');
    }
    return context;
}
