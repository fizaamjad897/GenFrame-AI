"use client";

import React, { Suspense, useEffect, useState } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Button,
    CircularProgress,
} from '@mui/material';
import {
    CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useUser } from '@/app/context/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';
import { usePageHeader } from '@/app/context/PageHeaderContext';
import { getPlanLabel } from '@/types/billing';
import { PopIn } from '@/components/motion/Reveal';

const BillingSuccessContent = () => {
    const { user, refreshUser } = useUser();
    const router = useRouter();
    const searchParams = useSearchParams();
    const { setHeader, resetHeader } = usePageHeader();
    const [isRefreshing, setIsRefreshing] = useState(true);
    const [statusMessage, setStatusMessage] = useState('Verifying your payment...');
    const [manualSyncLoading, setManualSyncLoading] = useState(false);
    const [showSyncButton, setShowSyncButton] = useState(false);

    const sessionId = searchParams.get('session_id');

    useEffect(() => {
        setHeader({ title: 'Payment Success' });
        return () => resetHeader();
    }, [setHeader, resetHeader]);

    const handleManualSync = async () => {
        setManualSyncLoading(true);
        setStatusMessage('Forcing account synchronization...');
        const token = localStorage.getItem('auth_token');
        if (!token) return;

        try {
            const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
            const response = await fetch(`${API_BASE_URL}/stripe/manual-sync`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: user?.email,
                    session_id: sessionId
                })
            });

            if (response.ok) {
                await refreshUser();
                setIsRefreshing(false);
                setStatusMessage('Account forced-synced successfully!');
            } else {
                const errorData = await response.json();
                setStatusMessage(`Sync failed: ${errorData.detail || 'Try refreshing in a moment'}`);
            }
        } catch (error) {
            console.error('Manual sync error:', error);
            setStatusMessage('Error during sync. Please try again or go to Home.');
        } finally {
            setManualSyncLoading(false);
        }
    };

    useEffect(() => {
        let pollCount = 0;
        const maxPolls = 12;
        let pollInterval: NodeJS.Timeout;

        const syncButtonTimeout = setTimeout(() => {
            setShowSyncButton(true);
        }, 3000);

        const poll = async () => {
            const token = localStorage.getItem('auth_token');
            if (!token) return;

            try {
                const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';

                if (pollCount % 3 === 0) {
                    try {
                        if (sessionId) {
                            await fetch(`${API_BASE_URL}/stripe/manual-sync`, {
                                method: 'POST',
                                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                                body: JSON.stringify({ email: user?.email, session_id: sessionId })
                            });
                        } else {
                            await fetch(`${API_BASE_URL}/stripe/refresh-subscription`, {
                                method: 'POST',
                                headers: { 'Authorization': `Bearer ${token}` }
                            });
                        }
                    } catch (err) {
                        console.error('Polling sync error:', err);
                    }
                }

                const response = await fetch(`${API_BASE_URL}/users/me?t=${Date.now()}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (response.ok) {
                    const latestUser = await response.json();
                    pollCount++;

                    const hasCredits = (latestUser.credits?.remaining_units || 0) > 0 || (latestUser.remainingUnits || 0) > 0;

                    if (hasCredits) {
                        await refreshUser();
                        setIsRefreshing(false);
                        setStatusMessage('Your credits have been updated!');
                        setShowSyncButton(false);
                        clearInterval(pollInterval);
                    } else if (pollCount >= maxPolls) {
                        await refreshUser();
                        setIsRefreshing(false);
                        setShowSyncButton(true);
                        setStatusMessage('If your credits still show 0, please click "Sync Now" below.');
                        clearInterval(pollInterval);
                    }
                }
            } catch (error) {
                console.error('Polling error:', error);
            }
        };

        poll();
        pollInterval = setInterval(poll, 2500);

        return () => {
            clearInterval(pollInterval);
            clearTimeout(syncButtonTimeout);
        };
    }, [refreshUser]);

    return (
        <Box>
            <Container maxWidth="md" sx={{ py: { xs: 6, md: 10 } }}>
                <PopIn>
                <Paper elevation={0} sx={{ p: { xs: 4, md: 6 }, borderRadius: '18px', border: '1px solid #E5E7EB', bgcolor: '#FFFFFF', textAlign: 'center', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' }}>
                    <Box sx={{ width: 80, height: 80, borderRadius: '18px', border: `1px solid ${isRefreshing ? 'rgba(139, 92, 246, 0.4)' : 'rgba(62, 125, 92, 0.4)'}`, bgcolor: 'transparent', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 3 }}>
                        {isRefreshing ? (
                            <CircularProgress size={40} sx={{ color: 'rgba(139, 92, 246, 1)' }} />
                        ) : (
                            <CheckCircleIcon sx={{ fontSize: 48, color: '#10B981' }} />
                        )}
                    </Box>

                    <Typography variant="h4" sx={{ fontSize: { xs: '24px', md: '32px' }, fontWeight: 500, color: '#111827', mb: 2 }}>
                        {isRefreshing ? 'Checking payment...' : 'Payment Successful!'}
                    </Typography>

                    <Typography sx={{ fontSize: '16px', color: '#6B7280', mb: 4, maxWidth: '500px', mx: 'auto' }}>
                        {statusMessage}
                    </Typography>

                    {user && (
                        <Box sx={{ p: 3, borderRadius: '18px', bgcolor: '#FFFFFF', border: '1px solid #E5E7EB', mb: 4, opacity: isRefreshing ? 0.7 : 1 }}>
                            <Typography sx={{ fontSize: '14px', color: '#6B7280', mb: 2 }}>Your Updated Account</Typography>
                            <Box sx={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: 3 }}>
                                <Box>
                                    <Typography sx={{ fontSize: '12px', color: '#9CA3AF', mb: 0.5 }}>Current Plan</Typography>
                                    <Typography sx={{ fontSize: '20px', fontWeight: 500, color: '#111827' }}>{getPlanLabel(user.plan)}</Typography>
                                </Box>
                                <Box>
                                    <Typography sx={{ fontSize: '12px', color: '#9CA3AF', mb: 0.5 }}>Engine Type</Typography>
                                    <Typography sx={{ fontSize: '20px', fontWeight: 500, color: '#111827' }}>
                                        {user.engineType ? (user.engineType.charAt(0).toUpperCase() + user.engineType.slice(1)) : 'Transformation'}
                                    </Typography>
                                </Box>
                                <Box>
                                    <Typography sx={{ fontSize: '12px', color: '#9CA3AF', mb: 0.5 }}>Total Credits</Typography>
                                    <Typography sx={{ fontSize: '20px', fontWeight: 500, color: '#10B981' }}>
                                        {(user.remainingUnits || user.credits?.remaining_units || 0).toLocaleString()}
                                    </Typography>
                                </Box>
                            </Box>
                        </Box>
                    )}

                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                        {showSyncButton && isRefreshing && (
                            <Button variant="contained" onClick={handleManualSync} disabled={manualSyncLoading}
                                sx={{ bgcolor: 'rgba(139, 92, 246, 1)', textTransform: 'none', fontWeight: 500, px: 4, py: 1.2, borderRadius: '18px', '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.9)' } }}>
                                {manualSyncLoading ? 'Syncing...' : 'Sync Now'}
                            </Button>
                        )}
                        <Button variant="contained" onClick={() => router.push('/dashboard')}
                            sx={{ bgcolor: 'rgba(139, 92, 246, 1)', textTransform: 'none', fontWeight: 500, px: 4, py: 1.2, borderRadius: '18px', '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.9)' } }}>
                            Go to Home
                        </Button>
                        <Button variant="outlined" onClick={() => router.push('/billing')}
                            sx={{ borderColor: '#E5E7EB', color: '#111827', textTransform: 'none', fontWeight: 500, px: 4, py: 1.2, borderRadius: '18px', '&:hover': { borderColor: 'rgba(139, 92, 246, 1)', bgcolor: 'rgba(139, 92, 246, 0.02)' } }}>
                            My Plan
                        </Button>
                    </Box>

                    {sessionId && (
                        <Typography sx={{ fontSize: '11px', color: '#9CA3AF', mt: 4 }}>
                            Session ID: {sessionId}
                        </Typography>
                    )}
                </Paper>
                </PopIn>
            </Container>
        </Box>
    );
};

export default function BillingSuccessPage() {
    return (
        <Suspense fallback={
            <Box sx={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CircularProgress />
            </Box>
        }>
            <BillingSuccessContent />
        </Suspense>
    );
}
