"use client";

import React from 'react';
import {
    Box,
    Typography,
    Paper,
    Grid,
    LinearProgress,
    Chip,
    Button,
    CircularProgress,
} from '@mui/material';
import {
    CreditCard as CreditCardIcon,
    Settings as SettingsIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { getPlanLabel, type User, type EngineType } from '@/types/billing';

interface BillingOverviewProps {
    user: User;
    selectedEngine: EngineType;
    isPendingCancellation: boolean;
    processingItem: string | null;
    onManage?: () => void;
    onCancel?: () => void;
}

const BillingOverview: React.FC<BillingOverviewProps> = ({
    user,
    selectedEngine,
    isPendingCancellation,
    processingItem,
    onManage,
    onCancel,
}) => {
    const router = useRouter();
    const engineInfo = user.engine_data?.[selectedEngine];
    const enginePlan = engineInfo?.plan || '';
    const hasEnginePlan = Boolean(enginePlan.trim());

    let credits;
    if (hasEnginePlan && engineInfo?.credits) {
        credits = { ...engineInfo.credits };
    } else if (hasEnginePlan && user.credits) {
        credits = { ...user.credits };
    } else {
        credits = {
            monthly_units_used: 0,
            monthly_units_max: 0,
            addon_units_used: engineInfo?.credits?.addon_units_used || user.credits?.addon_units_used || 0,
            addon_units_max: engineInfo?.credits?.addon_units_max || user.credits?.addon_units_max || 0,
            remaining_units: 0,
        };
    }

    if (credits.remaining_units === undefined || credits.remaining_units === null || !hasEnginePlan) {
        const monthlyRemaining = Math.max(0, (credits.monthly_units_max || 0) - (credits.monthly_units_used || 0));
        const addonRemaining = Math.max(0, (credits.addon_units_max || 0) - (credits.addon_units_used || 0));
        credits.remaining_units = monthlyRemaining + addonRemaining;
    }

    const currentPlanRaw = enginePlan;
    const effectiveSubId = engineInfo?.stripeSubscriptionId || (user.engineType === selectedEngine ? user.stripeSubscriptionId : null);
    const engineHasActivePlan = hasEnginePlan && Boolean(effectiveSubId) && !isPendingCancellation;
    const currentPlanLabel = (engineHasActivePlan || isPendingCancellation) ? getPlanLabel(currentPlanRaw) : 'No active plan';

    const monthlyRemaining = Math.max(0, credits.monthly_units_max - credits.monthly_units_used);
    const addonRemaining = Math.max(0, credits.addon_units_max - credits.addon_units_used);
    const monthlyProgress = credits.monthly_units_max > 0
        ? (credits.monthly_units_used / credits.monthly_units_max) * 100
        : 0;
    const addonProgress = credits.addon_units_max > 0
        ? (credits.addon_units_used / credits.addon_units_max) * 100
        : 0;

    return (
        <Paper
            elevation={0}
            sx={{
                p: 4, borderRadius: '24px', border: '1px solid #e5e7eb',
                bgcolor: 'white', mb: 4, boxShadow: '0 4px 20px -5px rgba(0,0,0,0.05)',
            }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                <CreditCardIcon sx={{ fontSize: 28, color: 'rgba(3, 105, 161, 1)' }} />
                <Typography variant="h5" sx={{ fontSize: '20px', fontWeight: 600, color: '#111827' }}>
                    Your Current Plan
                </Typography>
                <Chip
                    label={currentPlanLabel}
                    sx={{ bgcolor: 'rgba(3, 105, 161, 0.1)', color: 'rgba(3, 105, 161, 1)', fontWeight: 600, fontSize: '12px' }}
                />
                {isPendingCancellation && (
                    <Chip label="Cancelled (Resumable)" size="small" color="error" variant="outlined"
                        sx={{ fontWeight: 600, fontSize: '11px', height: '24px', bgcolor: '#fef2f2', borderColor: '#fee2e2', color: '#b91c1c' }}
                    />
                )}
            </Box>

            <Grid container spacing={3}>
                <Grid size={12}>
                    <Box sx={{
                        p: 2.5, borderRadius: '16px', bgcolor: 'rgba(3, 105, 161, 0.03)',
                        border: '1px solid rgba(3, 105, 161, 0.1)', mb: 1,
                        display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                    }}>
                        <Box>
                            <Typography sx={{ fontSize: '14px', color: '#6b7280', mb: 0.5 }}>Current Usage (Total)</Typography>
                            <Typography sx={{ fontSize: '32px', fontWeight: 700, color: '#111827', lineHeight: 1 }}>
                                {((credits.monthly_units_used || 0) + (credits.addon_units_used || 0)).toLocaleString()} / {((credits.monthly_units_max || 0) + (credits.addon_units_max || 0)).toLocaleString()}
                            </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                            <Typography sx={{ fontSize: '13px', color: 'rgba(3, 105, 161, 1)', fontWeight: 600 }}>
                                {credits.remaining_units.toLocaleString()} Available
                            </Typography>
                            <Typography sx={{ fontSize: '12px', color: '#6b7280' }}>
                                {monthlyRemaining.toLocaleString()} Plan + {addonRemaining.toLocaleString()} Bonus
                            </Typography>
                        </Box>
                    </Box>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                    <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography sx={{ fontSize: '14px', fontWeight: 600, color: '#111827' }}>Monthly Plan Credits</Typography>
                            <Typography sx={{ fontSize: '14px', fontWeight: 600, color: '#111827' }}>
                                {monthlyRemaining.toLocaleString()} / {credits.monthly_units_max.toLocaleString()}
                            </Typography>
                        </Box>
                        <LinearProgress variant="determinate" value={monthlyProgress}
                            sx={{ height: 8, borderRadius: 4, bgcolor: '#e5e7eb', '& .MuiLinearProgress-bar': { bgcolor: 'rgba(3, 105, 161, 1)', borderRadius: 4 } }}
                        />
                        <Typography sx={{ fontSize: '12px', color: '#6b7280', mt: 0.5 }}>Resets monthly</Typography>
                    </Box>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                    <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography sx={{ fontSize: '14px', fontWeight: 600, color: '#111827' }}>Bonus Add-on Credits</Typography>
                            <Typography sx={{ fontSize: '14px', fontWeight: 600, color: '#111827' }}>
                                {addonRemaining.toLocaleString()} / {credits.addon_units_max.toLocaleString()}
                            </Typography>
                        </Box>
                        <LinearProgress variant="determinate" value={addonProgress}
                            sx={{ height: 8, borderRadius: 4, bgcolor: '#e5e7eb', '& .MuiLinearProgress-bar': { bgcolor: '#10b981', borderRadius: 4 } }}
                        />
                        <Typography sx={{ fontSize: '12px', color: '#6b7280', mt: 0.5 }}>Never expires</Typography>
                    </Box>
                </Grid>

                <Grid size={12}>
                    <Box sx={{ p: 2, borderRadius: '12px', bgcolor: '#f9fafb', border: '1px solid #e5e7eb' }}>
                        <Typography sx={{ fontSize: '12px', color: '#6b7280', mb: 0.5 }}>Overall Capacity (Used / Total)</Typography>
                        <Typography sx={{ fontSize: '28px', fontWeight: 700, color: '#111827' }}>
                            {((credits.monthly_units_used || 0) + (credits.addon_units_used || 0)).toLocaleString()} / {((credits.monthly_units_max || 0) + (credits.addon_units_max || 0)).toLocaleString()}
                        </Typography>
                    </Box>
                </Grid>
            </Grid>

            {(engineHasActivePlan || isPendingCancellation) && user.stripeCustomerId && (
                <Box sx={{ mt: 3 }}>
                    <Grid container spacing={1.5}>
                        <Grid size={{ xs: 12, md: 6 }}>
                            <Button fullWidth variant="outlined"
                                startIcon={processingItem === 'portal' ? <CircularProgress size={16} color="inherit" /> : <SettingsIcon />}
                                onClick={onManage} disabled={!!processingItem}
                                sx={{ height: '48px', borderColor: isPendingCancellation ? 'rgba(3, 105, 161, 1)' : '#e5e7eb', color: '#111827', textTransform: 'none', fontWeight: 600, borderRadius: '12px' }}
                            >
                                {isPendingCancellation ? 'Resume Subscription' : 'Manage'}
                            </Button>
                        </Grid>
                        <Grid size={{ xs: 12, md: 6 }}>
                            <Button fullWidth variant="contained" color="error"
                                onClick={onCancel}
                                disabled={!!processingItem || isPendingCancellation}
                                sx={{ height: '48px', textTransform: 'none', fontWeight: 600, borderRadius: '12px', boxShadow: 'none' }}
                            >
                                {isPendingCancellation ? 'Access Plan End' : 'Cancel'}
                            </Button>
                        </Grid>
                    </Grid>
                </Box>
            )}
        </Paper>
    );
};

export default BillingOverview;
