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
import { INK, ACCENT, TEXT_MUTED_L, BORDER_L, GOOD, BAD, MONO } from '@/app/theme/terminal';

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
                p: 4, borderRadius: '18px', border: `1px solid ${BORDER_L}`,
                bgcolor: '#FFFFFF', mb: 4, boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
            }}
        >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3, flexWrap: 'wrap' }}>
                <CreditCardIcon sx={{ fontSize: 28, color: ACCENT }} />
                <Typography variant="h5" sx={{ fontSize: '20px', fontWeight: 600, color: INK }}>
                    Your Current Plan
                </Typography>
                <Chip
                    label={currentPlanLabel}
                    sx={{ borderRadius: '18px', border: `1px solid ${ACCENT}`, bgcolor: 'transparent', color: ACCENT, fontWeight: 500, fontSize: '12px' }}
                />
                {isPendingCancellation && (
                    <Chip label="Cancelled (Resumable)" size="small" variant="outlined"
                        sx={{ fontWeight: 500, fontSize: '11px', height: '24px', bgcolor: 'transparent', borderRadius: '18px', borderColor: BAD, color: BAD }}
                    />
                )}
            </Box>

            <Grid container spacing={3}>
                <Grid size={12}>
                    <Box sx={{
                        p: 2.5, borderRadius: '18px', bgcolor: 'transparent',
                        border: `1px solid ${BORDER_L}`, mb: 1,
                        display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2,
                        alignItems: { xs: 'flex-start', sm: 'center' }, justifyContent: 'space-between'
                    }}>
                        <Box>
                            <Typography sx={{ fontSize: '14px', color: TEXT_MUTED_L, mb: 0.5 }}>Current Usage (Total)</Typography>
                            <Typography sx={{ fontSize: { xs: '26px', md: '32px' }, fontWeight: 600, color: INK, lineHeight: 1, fontFamily: MONO }}>
                                {((credits.monthly_units_used || 0) + (credits.addon_units_used || 0)).toLocaleString()} / {((credits.monthly_units_max || 0) + (credits.addon_units_max || 0)).toLocaleString()}
                            </Typography>
                        </Box>
                        <Box sx={{ textAlign: 'right' }}>
                            <Typography sx={{ fontSize: '13px', color: ACCENT, fontWeight: 600, fontFamily: MONO }}>
                                {credits.remaining_units.toLocaleString()} Available
                            </Typography>
                            <Typography sx={{ fontSize: '12px', color: TEXT_MUTED_L }}>
                                {monthlyRemaining.toLocaleString()} Plan + {addonRemaining.toLocaleString()} Bonus
                            </Typography>
                        </Box>
                    </Box>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                    <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography sx={{ fontSize: '14px', fontWeight: 500, color: INK }}>Monthly Plan Credits</Typography>
                            <Typography sx={{ fontSize: '14px', fontWeight: 500, color: INK, fontFamily: MONO }}>
                                {monthlyRemaining.toLocaleString()} / {credits.monthly_units_max.toLocaleString()}
                            </Typography>
                        </Box>
                        <LinearProgress variant="determinate" value={monthlyProgress}
                            sx={{ height: 6, borderRadius: 0, bgcolor: BORDER_L, '& .MuiLinearProgress-bar': { bgcolor: ACCENT, borderRadius: 0 } }}
                        />
                        <Typography sx={{ fontSize: '12px', color: TEXT_MUTED_L, mt: 0.5 }}>Resets monthly</Typography>
                    </Box>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                    <Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography sx={{ fontSize: '14px', fontWeight: 500, color: INK }}>Bonus Add-on Credits</Typography>
                            <Typography sx={{ fontSize: '14px', fontWeight: 500, color: INK, fontFamily: MONO }}>
                                {addonRemaining.toLocaleString()} / {credits.addon_units_max.toLocaleString()}
                            </Typography>
                        </Box>
                        <LinearProgress variant="determinate" value={addonProgress}
                            sx={{ height: 6, borderRadius: 0, bgcolor: BORDER_L, '& .MuiLinearProgress-bar': { bgcolor: GOOD, borderRadius: 0 } }}
                        />
                        <Typography sx={{ fontSize: '12px', color: TEXT_MUTED_L, mt: 0.5 }}>Never expires</Typography>
                    </Box>
                </Grid>

                <Grid size={12}>
                    <Box sx={{ p: 2, borderRadius: '18px', bgcolor: 'transparent', border: `1px solid ${BORDER_L}` }}>
                        <Typography sx={{ fontSize: '12px', color: TEXT_MUTED_L, mb: 0.5 }}>Overall Capacity (Used / Total)</Typography>
                        <Typography sx={{ fontSize: { xs: '24px', md: '28px' }, fontWeight: 600, color: INK, fontFamily: MONO }}>
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
                                sx={{ height: '48px', borderColor: isPendingCancellation ? ACCENT : BORDER_L, color: INK, textTransform: 'none', fontWeight: 500, borderRadius: '18px' }}
                            >
                                {isPendingCancellation ? 'Resume Subscription' : 'Manage'}
                            </Button>
                        </Grid>
                        <Grid size={{ xs: 12, md: 6 }}>
                            <Button fullWidth variant="contained"
                                onClick={onCancel}
                                disabled={!!processingItem || isPendingCancellation}
                                sx={{ height: '48px', textTransform: 'none', fontWeight: 500, borderRadius: '18px', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)', bgcolor: BAD, '&:hover': { bgcolor: BAD, filter: 'brightness(0.9)', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' } }}
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
