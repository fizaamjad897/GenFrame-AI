'use client';

import * as React from 'react';
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';
import { useServerInsertedHTML } from 'next/navigation';
import CssBaseline from '@mui/material/CssBaseline';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { Inter } from 'next/font/google';
import { CREAM, INK, ACCENT, BORDER_L, SHADOW_SM } from '../theme/terminal';

const inter = Inter({
    subsets: ['latin'],
    display: 'swap',
});

const theme = createTheme({
    palette: {
        primary: {
            main: ACCENT,
            light: '#A78BFA',
            contrastText: '#FFFFFF',
        },
        background: {
            default: CREAM,
            paper: '#FFFFFF',
        },
        text: {
            primary: INK,
        },
    },
    typography: {
        fontFamily: inter.style.fontFamily,
        h1: { fontSize: '2.5rem', fontWeight: 500, letterSpacing: '-0.02em' },
        h2: { fontSize: '2rem', fontWeight: 500, letterSpacing: '-0.02em' },
        h3: { fontSize: '1.5rem', fontWeight: 500, letterSpacing: '-0.01em' },
        h4: { fontSize: '1.25rem', fontWeight: 500 },
        h5: { fontSize: '1.1rem', fontWeight: 500 },
        h6: { fontSize: '0.95rem', fontWeight: 500 },
        subtitle1: { fontSize: '0.9rem', fontWeight: 500 },
        subtitle2: { fontSize: '0.8rem', fontWeight: 500 },
        body1: { fontSize: '0.85rem', fontWeight: 400 },
        body2: { fontSize: '0.75rem', fontWeight: 400 },
        button: { fontSize: '0.85rem', fontWeight: 500, textTransform: 'none' },
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: '14px',
                    padding: '8px 16px',
                    boxShadow: SHADOW_SM,
                    '&:hover': {
                        boxShadow: SHADOW_SM,
                        filter: 'brightness(0.96)',
                    },
                },
                containedPrimary: {
                    color: '#FFFFFF',
                    backgroundImage: 'linear-gradient(135deg, #A78BFA, #8B5CF6)',
                    '&:hover': {
                        backgroundImage: 'linear-gradient(135deg, #A78BFA, #8B5CF6)',
                        filter: 'brightness(1.04)',
                        boxShadow: SHADOW_SM,
                    },
                },
            },
        },
        MuiCard: {
            styleOverrides: {
                root: {
                    borderRadius: '20px',
                    border: `1px solid ${BORDER_L}`,
                    boxShadow: SHADOW_SM,
                    backgroundColor: '#FFFFFF',
                }
            }
        },
        MuiPaper: {
            styleOverrides: {
                root: {
                    backgroundImage: 'none',
                },
            },
        },
    },
});

export default function ThemeRegistry({ children }: { children: React.ReactNode }) {
    const [{ cache, flush }] = React.useState(() => {
        const cache = createCache({ key: 'mui', prepend: true });
        cache.compat = true;

        const prevInsert = cache.insert;
        let inserted: string[] = [];
        cache.insert = (...args: Parameters<typeof cache.insert>) => {
            const serialized = args[1];
            if (cache.inserted[serialized.name] === undefined) {
                inserted.push(serialized.name);
            }
            return prevInsert.apply(cache, args);
        };

        const flush = () => {
            const prev = inserted;
            inserted = [];
            return prev;
        };

        return { cache, flush };
    });

    useServerInsertedHTML(() => {
        const names = flush();
        if (names.length === 0) return null;

        let styles = '';
        for (const name of names) {
            styles += cache.inserted[name];
        }

        return (
            <style
                data-emotion={`${cache.key} ${names.join(' ')}`}
                // eslint-disable-next-line react/no-danger
                dangerouslySetInnerHTML={{ __html: styles }}
            />
        );
    });

    return (
        <CacheProvider value={cache}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                {children}
            </ThemeProvider>
        </CacheProvider>
    );
}
