"use client";

import { useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Box, CircularProgress, Container, Typography, Button, Paper, Stack } from '@mui/material';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import { getPlanLabel, hasEngineActiveSubscription, getEnginePlan } from '@/types/billing';
import { useUser } from '@/app/context/AuthContext';
import { usePageHeader } from '@/app/context/PageHeaderContext';
import { useRouter } from 'next/navigation';
import { CREAM, INK, ACCENT, TEXT_MUTED_L, BORDER_L } from '@/app/theme/terminal';
import { PopIn } from '@/components/motion/Reveal';

const ImageProcessor = dynamic(() => import('@/app/components/ImageProcessor'), {
    ssr: false,
    loading: () => (
        <Box sx={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <CircularProgress />
        </Box>
    ),
});

export default function CreationEnginePage() {
    const router = useRouter();
    const { user, loading: authLoading } = useUser();
    const { setHeader, resetHeader } = usePageHeader();
    const engineType = 'creation';

    useEffect(() => {
        setHeader({ title: 'Creation Engine' });
        return () => resetHeader();
    }, [setHeader, resetHeader]);

    if (authLoading || !user) {
        return (
            <Box sx={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CircularProgress size={32} sx={{ color: ACCENT }} />
            </Box>
        );
    }

    const isPostpaid = Boolean(user.is_postpaid);
    const availableEngines = (user.available_engines && user.available_engines.length > 0)
        ? user.available_engines
        : ['transformation', 'creation'];
    const hasAllocatedEngine = availableEngines.includes(engineType);

    useEffect(() => {
        if (!hasAllocatedEngine) {
            router.replace('/dashboard');
        }
    }, [hasAllocatedEngine, router]);

    if (!hasAllocatedEngine) {
        return (
            <Box sx={{ minHeight: '60vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <CircularProgress size={32} sx={{ color: ACCENT }} />
            </Box>
        );
    }

    const hasSubscription = hasEngineActiveSubscription(user, engineType);
    const enginePlan = getEnginePlan(user, engineType);
    const planLabel = hasSubscription ? getPlanLabel(enginePlan) : 'No active subscription';

    const selectedCredits = user.engine_data?.[engineType]?.credits;
    const effectiveCredits = hasSubscription ? (selectedCredits || user.credits) : null;

    const monthlyRemaining = hasSubscription
        ? Math.max(0, (effectiveCredits?.monthly_units_max || 0) - (effectiveCredits?.monthly_units_used || 0))
        : 0;
    const addonCredits = selectedCredits || user.credits;
    const addonRemaining = Math.max(0, (addonCredits?.addon_units_max || 0) - (addonCredits?.addon_units_used || 0));
    const remainingUnits = monthlyRemaining + addonRemaining;
    const hasNoCredits = remainingUnits <= 0;

    if (!isPostpaid && !hasSubscription) {
        return (
            <Container maxWidth="md" sx={{ py: { xs: 4, md: 6 } }}>
                <PopIn>
                <Paper
                    elevation={0}
                    sx={{
                        p: { xs: 4, md: 8 },
                        textAlign: 'center',
                        borderRadius: '18px',
                        border: `1px solid ${BORDER_L}`,
                        bgcolor: '#FFFFFF',
                    }}
                >
                    <Box sx={{
                        mb: 3, width: 80, height: 80, borderRadius: '18px',
                        border: `1px solid ${ACCENT}55`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto'
                    }}>
                        <AccountBalanceWalletIcon sx={{ fontSize: 36, color: ACCENT }} />
                    </Box>
                    <Typography variant="h4" gutterBottom sx={{ fontWeight: 500, color: INK }}>
                        Subscription required
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 4, color: TEXT_MUTED_L, maxWidth: '500px', mx: 'auto', lineHeight: 1.6 }}>
                        Your account has <b>{planLabel}</b>. Choose a plan to activate monthly credits and start using the Creation engine.
                    </Typography>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} justifyContent="center">
                        <Button
                            variant="contained"
                            size="large"
                            onClick={() => router.push('/pricing')}
                            sx={{
                                borderRadius: '18px', px: 4, py: 1.2, fontSize: '13px',
                                bgcolor: ACCENT, color: '#FFFFFF', fontWeight: 600, boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                                '&:hover': { bgcolor: ACCENT, filter: 'brightness(0.94)', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' }
                            }}
                        >
                            View Plans
                        </Button>
                    </Stack>
                </Paper>
                </PopIn>
            </Container>
        );
    }

    if (!isPostpaid && hasNoCredits) {
        return (
            <Container maxWidth="md" sx={{ py: { xs: 4, md: 6 } }}>
                <PopIn>
                <Paper
                    elevation={0}
                    sx={{
                        p: { xs: 4, md: 8 },
                        textAlign: 'center',
                        borderRadius: '18px',
                        border: `1px solid ${BORDER_L}`,
                        bgcolor: '#FFFFFF',
                    }}
                >
                    <Box sx={{
                        mb: 3, width: 80, height: 80, borderRadius: '18px',
                        border: `1px solid ${ACCENT}55`,
                        display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto'
                    }}>
                        <AccountBalanceWalletIcon sx={{ fontSize: 36, color: ACCENT }} />
                    </Box>
                    <Typography variant="h4" gutterBottom sx={{ fontWeight: 500, color: INK }}>
                        No credits available
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 4, color: TEXT_MUTED_L, maxWidth: '520px', mx: 'auto', lineHeight: 1.6 }}>
                        Your Creation engine currently has 0 remaining credits.
                    </Typography>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5} justifyContent="center">
                        <Button variant="contained" size="large" onClick={() => router.push('/billing')}
                            sx={{ borderRadius: '18px', px: 4, py: 1.2, fontSize: '13px', bgcolor: ACCENT, color: '#FFFFFF', fontWeight: 600, boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' }}>
                            Billing & Addons
                        </Button>
                    </Stack>
                </Paper>
                </PopIn>
            </Container>
        );
    }

    return <ImageProcessor engineType="creation" />;
}
