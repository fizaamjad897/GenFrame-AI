"use client";

import React, { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Button,
    Grid,
    Card,
    CardContent,
    LinearProgress,
    Chip,
    ToggleButtonGroup,
    ToggleButton,
    Alert,
    CircularProgress,
} from '@mui/material';
import {
    CreditCard as CreditCardIcon,
    TrendingUp as TrendingUpIcon,
    ShoppingCart as ShoppingCartIcon,
    Settings as SettingsIcon,
} from '@mui/icons-material';
import { useUser } from '@/app/context/AuthContext';
import { useRouter } from 'next/navigation';
import { usePageHeader } from '@/app/context/PageHeaderContext';
import { redirectToCheckout, redirectToPortal, cancelSubscription, refreshSubscriptionStatus, redirectToTestCheckout } from '@/lib/stripe';
import { usePricingPlans } from '@/hooks/usePricingPlans';
import type { EngineType } from '@/types/billing';
import { getPlanLabel, hasActiveSubscription } from '@/types/billing';
import CancelSubscriptionModal from '@/app/components/modals/CancelSubscriptionModal';
import BillingOverview from '@/app/components/billing/BillingOverview';
import { FadeIn } from '@/components/motion/Reveal';

const BillingPage = () => {
    const { user, refreshUser } = useUser();
    const router = useRouter();
    const { setHeader, resetHeader } = usePageHeader();
    const [selectedEngine, setSelectedEngine] = useState<EngineType>('transformation');
    const [processingItem, setProcessingItem] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [cancelModalOpen, setCancelModalOpen] = useState(false);
    const [initialSyncDone, setInitialSyncDone] = useState(false);

    useEffect(() => {
        setHeader({ title: 'Billing & Usage' });
        return () => resetHeader();
    }, [setHeader, resetHeader]);

    const handleUpgrade = useCallback(async (planCode: string) => {
        setProcessingItem(planCode);
        setError(null);
        setSuccess(null);
        try {
            await redirectToCheckout(planCode, selectedEngine, 'subscription');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start checkout');
            setProcessingItem(null);
        }
    }, [selectedEngine]);

    const handleBuyAddon = useCallback(async (planCode: string) => {
        setProcessingItem(planCode);
        setError(null);
        setSuccess(null);
        try {
            await redirectToCheckout(planCode, selectedEngine, 'addon');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start checkout');
            setProcessingItem(null);
        }
    }, [selectedEngine]);

    const handleManageSubscription = useCallback(async () => {
        setProcessingItem('portal');
        setError(null);
        setSuccess(null);
        try {
            await redirectToPortal();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to open billing portal');
            setProcessingItem(null);
        }
    }, []);

    const handleCancelSubscription = useCallback(async () => {
        setProcessingItem('cancel');
        setError(null);
        setSuccess(null);
        setCancelModalOpen(false);
        try {
            const result = await cancelSubscription(true, selectedEngine);
            if (result.cancelled) {
                await new Promise(resolve => setTimeout(resolve, 500));
                await refreshUser();
                await new Promise(resolve => setTimeout(resolve, 300));
                await refreshUser();
                setSuccess('Plan cancelled successfully. Credits have been reset.');
                setTimeout(() => { window.location.reload(); }, 1500);
            } else {
                setError('Cancellation failed. Please try again.');
            }
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Failed to cancel plan';
            if (errorMsg.includes('not found') || errorMsg.includes('does not exist')) {
                setError('Plan not found. It may have already been cancelled.');
                setTimeout(() => refreshUser(), 1000);
            } else if (errorMsg.includes('No active subscription')) {
                setError('No active plan found. Refreshing your data...');
                setTimeout(() => refreshUser(), 1000);
            } else {
                setError(errorMsg);
            }
        } finally {
            setProcessingItem(null);
        }
    }, [selectedEngine, refreshUser]);

    const handleRefreshSubscription = useCallback(async () => {
        setProcessingItem('refresh');
        setError(null);
        try {
            const result = await refreshSubscriptionStatus();
            await refreshUser();
            if (result.subscription_id) {
                setSuccess(`Subscription synced! Plan: ${result.plan}, Engine: ${result.engine}`);
            } else {
                setSuccess(result.message);
            }
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Failed to refresh subscription';
            setError(`Refresh failed: ${errorMsg}`);
        } finally {
            setProcessingItem(null);
        }
    }, [refreshUser]);

    useEffect(() => {
        if (!initialSyncDone && user) {
            handleRefreshSubscription();
            setInitialSyncDone(true);
        }
    }, [user, initialSyncDone, handleRefreshSubscription]);

    const { plans: apiPlans, loading: plansLoading } = usePricingPlans();

    if (!user) {
        return null;
    }

    const isPostpaid = Boolean(user.is_postpaid);

    const engineInfo = user.engine_data?.[selectedEngine];
    const enginePlan = engineInfo?.plan || '';
    const hasEnginePlan = Boolean(enginePlan.trim());

    const currentPlanRaw = enginePlan;
    const effectiveSubId = engineInfo?.stripeSubscriptionId || (user.engineType === selectedEngine ? user.stripeSubscriptionId : null);
    const isPendingCancellation = Boolean(engineInfo?.credits?.is_pending_cancellation);
    const engineHasActivePlan = hasEnginePlan && Boolean(effectiveSubId) && !isPendingCancellation;
    const currentPlanLabel = (engineHasActivePlan || isPendingCancellation) ? getPlanLabel(currentPlanRaw) : 'No active plan';

    if (isPostpaid) {
        const availableEngines = (user.available_engines && user.available_engines.length > 0)
            ? user.available_engines
            : ['transformation', 'creation'];

        const perEngineUsage = availableEngines.map((etype) => {
            const credits = user.engine_data?.[etype as EngineType]?.credits || user.credits;
            const used = (credits?.monthly_units_used || 0) + (credits?.addon_units_used || 0);
            const rate = Number(credits?.overageRate || 0);
            return { engine: etype, used, rate };
        });

        // Per-engine estimated cost (each engine × its own rate)
        const perEngineEstimates = perEngineUsage.map((item) => ({
            ...item,
            estimatedCost: item.used * item.rate,
        }));
        const totalUsed = perEngineUsage.reduce((sum, item) => sum + item.used, 0);
        const totalEstimated = perEngineEstimates.reduce((sum, item) => sum + item.estimatedCost, 0);
        const now = new Date();
        const nextBilling = new Date(now.getFullYear(), now.getMonth() + 1, 1);

        const [simulateLoading, setSimulateLoading] = useState(false);
        const [simulateResult, setSimulateResult] = useState<string | null>(null);

        const handleSimulateMonthEnd = async () => {
            setSimulateLoading(true);
            setSimulateResult(null);
            try {
                const token = localStorage.getItem('auth_token');
                const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
                const res = await fetch(`${API_BASE}/admin/trigger-billing-rollover`, {
                    method: 'POST',
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (res.ok) {
                    const data = await res.json();
                    setSimulateResult(`Bill generated! Total: $${data.totalAmount?.toFixed(2) || '0.00'}`);
                    // Refresh user to see updated counters
                    await refreshUser();
                } else {
                    const err = await res.json().catch(() => ({}));
                    setSimulateResult(`Error: ${err.detail || res.statusText}`);
                }
            } catch (e: any) {
                setSimulateResult(`Error: ${e.message}`);
            } finally {
                setSimulateLoading(false);
            }
        };

        const handleDownloadPrevMonthBill = async () => {
            try {
                const token = localStorage.getItem('auth_token');
                const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
                const res = await fetch(`${API_BASE}/users/billing-history`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (res.ok) {
                    const bills = await res.json();
                    if (bills.length > 0) {
                        const bill = bills[0];
                        const breakdown = bill.engineBreakdown || {};
                        const lines = [
                            'SignageX - Previous Month Bill',
                            `Customer: ${user.fullName || user.email}`,
                            `Email: ${user.email}`,
                            `Billing Model: Pay as you go (PostPaid)`,
                            `Period: ${new Date(bill.billingPeriodStart).toLocaleDateString()} - ${new Date(bill.billingPeriodEnd).toLocaleDateString()}`,
                            ``,
                            `--- Transformation Engine ---`,
                            `Credits Used: ${breakdown.transformation?.unitsUsed || 0}`,
                            `Threshold: ${breakdown.transformation?.threshold || 0}`,
                            `Rate/Credit: $${breakdown.transformation?.ratePerCredit?.toFixed(2) || '0.00'}`,
                            `Overage Rate: $${breakdown.transformation?.overageRate?.toFixed(2) || '0.00'}`,
                            `Amount: $${breakdown.transformation?.amount?.toFixed(2) || '0.00'}`,
                            ``,
                            `--- Creation Engine ---`,
                            `Credits Used: ${breakdown.creation?.unitsUsed || 0}`,
                            `Threshold: ${breakdown.creation?.threshold || 0}`,
                            `Rate/Credit: $${breakdown.creation?.ratePerCredit?.toFixed(2) || '0.00'}`,
                            `Overage Rate: $${breakdown.creation?.overageRate?.toFixed(2) || '0.00'}`,
                            `Amount: $${breakdown.creation?.amount?.toFixed(2) || '0.00'}`,
                            ``,
                            `Total Amount: $${bill.totalAmount?.toFixed(2) || '0.00'}`,
                            `Generated At: ${bill.generatedAt}`,
                        ];
                        const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `bill-${new Date(bill.billingPeriodStart).toISOString().slice(0, 7)}.txt`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }
                }
            } catch (e) {
                console.error('Error downloading bill:', e);
            }
        };

        // Check if previous month bill exists (billing history)
        const [hasPrevBill, setHasPrevBill] = useState(false);
        useEffect(() => {
            const checkPrevBill = async () => {
                try {
                    const token = localStorage.getItem('auth_token');
                    const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
                    const res = await fetch(`${API_BASE}/users/billing-history`, {
                        headers: { Authorization: `Bearer ${token}` },
                    });
                    if (res.ok) {
                        const bills = await res.json();
                        setHasPrevBill(bills.length > 0);
                    }
                } catch { /* ignore */ }
            };
            checkPrevBill();
        }, [simulateResult]);

        return (
            <Box>
                <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 } }}>
                    <FadeIn>
                    <Paper elevation={0} sx={{ p: 4, borderRadius: '18px', border: '1px solid #E5E7EB', bgcolor: '#FFFFFF', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' }}>
                        <Typography variant="h5" sx={{ fontSize: '20px', fontWeight: 500, color: '#111827', mb: 2 }}>
                            Usage Billing Overview
                        </Typography>

                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' }, gap: 2 }}>
                            <Card elevation={0} sx={{ border: '1px solid #E5E7EB' }}>
                                <CardContent>
                                    <Typography sx={{ fontSize: '12px', color: '#6B7280', mb: 0.5 }}>Allocated Engines</Typography>
                                    <Typography sx={{ fontSize: '18px', fontWeight: 500 }}>{availableEngines.length}</Typography>
                                </CardContent>
                            </Card>
                            <Card elevation={0} sx={{ border: '1px solid #E5E7EB' }}>
                                <CardContent>
                                    <Typography sx={{ fontSize: '12px', color: '#6B7280', mb: 0.5 }}>Total Credits Used</Typography>
                                    <Typography sx={{ fontSize: '18px', fontWeight: 500 }}>{totalUsed.toLocaleString()}</Typography>
                                </CardContent>
                            </Card>
                            <Card elevation={0} sx={{ border: '1px solid #E5E7EB' }}>
                                <CardContent>
                                    <Typography sx={{ fontSize: '12px', color: '#6B7280', mb: 0.5 }}>Next Bill Date</Typography>
                                    <Typography sx={{ fontSize: '18px', fontWeight: 500 }}>
                                        {nextBilling.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Box>

                        {/* Per-engine breakdown with individual rates */}
                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: availableEngines.length === 1 ? '1fr' : '1fr 1fr' }, gap: 2, mt: 2 }}>
                            {perEngineEstimates.map((item) => (
                                <Card key={item.engine} elevation={0} sx={{ border: '1px solid #E5E7EB' }}>
                                    <CardContent>
                                        <Typography sx={{ fontSize: '14px', fontWeight: 500, color: '#111827', mb: 1 }}>
                                            {item.engine === 'creation' ? 'Creation' : 'Transformation'} Engine
                                        </Typography>
                                        <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                                            <Box>
                                                <Typography sx={{ fontSize: '11px', color: '#9CA3AF' }}>Credits Used</Typography>
                                                <Typography sx={{ fontSize: '16px', fontWeight: 500 }}>{item.used}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography sx={{ fontSize: '11px', color: '#9CA3AF' }}>Rate / Credit</Typography>
                                                <Typography sx={{ fontSize: '16px', fontWeight: 500 }}>${item.rate.toFixed(2)}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography sx={{ fontSize: '11px', color: '#9CA3AF' }}>Overage Rate (1.5×)</Typography>
                                                <Typography sx={{ fontSize: '16px', fontWeight: 500 }}>${(item.rate * 1.5).toFixed(2)}</Typography>
                                            </Box>
                                            <Box>
                                                <Typography sx={{ fontSize: '11px', color: '#9CA3AF' }}>Estimated Cost</Typography>
                                                <Typography sx={{ fontSize: '16px', fontWeight: 500, color: '#8B5CF6' }}>${item.estimatedCost.toFixed(2)}</Typography>
                                            </Box>
                                        </Box>
                                    </CardContent>
                                </Card>
                            ))}
                        </Box>

                        {/* Total estimated */}
                        <Box sx={{ mt: 2, p: 2, bgcolor: '#FFFFFF', borderRadius: '18px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography sx={{ fontSize: '14px', fontWeight: 500, color: '#111827' }}>
                                Total Estimated Amount
                            </Typography>
                            <Typography sx={{ fontSize: '20px', fontWeight: 600, color: '#8B5CF6' }}>
                                ${totalEstimated.toFixed(2)}
                            </Typography>
                        </Box>

                        <Box sx={{ mt: 3 }}>
                            <Typography sx={{ fontSize: '13px', color: '#6B7280' }}>
                                Charges are calculated from actual usage and billed on the 1st of every month.
                                Minimum commitment applies per engine threshold. Overage above threshold is billed at 1.5× the base rate.
                            </Typography>
                        </Box>

                        {simulateResult && (
                            <Alert severity={simulateResult.startsWith('Error') ? 'error' : 'success'} sx={{ mt: 2 }}>
                                {simulateResult}
                            </Alert>
                        )}

                        <Box sx={{ mt: 3, display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 1 }}>
                            <Box sx={{ display: 'flex', gap: 2 }}>
                                {/* {(user.role === 'admin' || user.email === 'muhammadhamzafaisal146@gmail.com') && (
                                    <Button
                                        variant="outlined"
                                        color="secondary"
                                        onClick={handleSimulateMonthEnd}
                                        disabled={simulateLoading}
                                        sx={{ textTransform: 'none', borderRadius: '10px', fontWeight: 500 }}
                                    >
                                        {simulateLoading ? 'Simulating...' : 'Simulate Month End (Admin)'}
                                    </Button>
                                )} */}
                                <Button
                                    variant="outlined"
                                    disabled={!hasPrevBill}
                                    onClick={handleDownloadPrevMonthBill}
                                    sx={{
                                        textTransform: 'none',
                                        borderRadius: '18px',
                                        fontWeight: 500,
                                        borderColor: hasPrevBill ? '#8B5CF6' : '#E5E7EB',
                                        color: hasPrevBill ? '#8B5CF6' : '#9CA3AF'
                                    }}
                                >
                                    Download Previous Month Bill
                                </Button>
                            </Box>
                            {!hasPrevBill && (
                                <Typography sx={{ fontSize: '12px', color: '#6B7280', mt: 0.5 }}>
                                    The bill for the current period will be available on the 1st of next month.
                                </Typography>
                            )}
                        </Box>
                    </Paper>
                    </FadeIn>
                </Container>
            </Box>
        );
    }

    return (
        <Box>
            <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 } }}>
                {error && (
                    <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                        {error}
                    </Alert>
                )}
                {success && (
                    <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess(null)}>
                        {success}
                    </Alert>
                )}

                {/* Tester-only $1 checkout helper */}
                {user.email === 'muhammadhamzafaisal146@gmail.com' && (
                    <Box sx={{ mb: 3 }}>
                        <Alert severity="info" sx={{ mb: 2, borderRadius: '18px' }}>
                            This section is visible only for the tester account to verify live Stripe payments with a $1 plan.
                        </Alert>
                        <Button
                            variant="contained"
                            color="primary"
                            onClick={async () => {
                                setProcessingItem('test-checkout');
                                setError(null);
                                setSuccess(null);
                                try {
                                    await redirectToTestCheckout();
                                } catch (err) {
                                    setError(err instanceof Error ? err.message : 'Failed to start test checkout');
                                } finally {
                                    setProcessingItem(null);
                                }
                            }}
                            disabled={!!processingItem}
                        >
                            Start $1 Tester Checkout
                        </Button>
                    </Box>
                )}

                <FadeIn>
                <BillingOverview
                    user={user}
                    selectedEngine={selectedEngine}
                    isPendingCancellation={isPendingCancellation}
                    processingItem={processingItem}
                    onManage={handleManageSubscription}
                    onCancel={() => setCancelModalOpen(true)}
                />
                </FadeIn>

                <CancelSubscriptionModal
                    open={cancelModalOpen}
                    onClose={() => setCancelModalOpen(false)}
                    onConfirm={handleCancelSubscription}
                    planName={currentPlanLabel}
                    loading={processingItem === 'cancel'}
                />

                {/* Engine Type Selector */}
                {/* <Box sx={{ mb: 3 }}>
                    <Typography sx={{ fontSize: '14px', fontWeight: 500, color: '#111827', mb: 1.5 }}>Select Engine Type</Typography>
                    <ToggleButtonGroup value={selectedEngine} exclusive
                        onChange={(_, value) => value && setSelectedEngine(value)}
                        sx={{
                            '& .MuiToggleButton-root': {
                                textTransform: 'none', fontWeight: 500, px: 3, py: 1,
                                '&.Mui-selected': { bgcolor: 'rgba(139, 92, 246, 1)', color: 'white', '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.9)' } },
                            },
                        }}
                    >
                        <ToggleButton value="transformation">Transformation</ToggleButton>
                        <ToggleButton value="creation">Creation</ToggleButton>
                    </ToggleButtonGroup>
                </Box> */}

                {/* Upgrade Plans */}
                {/* <Box sx={{ mb: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                        <TrendingUpIcon sx={{ fontSize: 28, color: 'rgba(139, 92, 246, 1)' }} />
                        <Typography variant="h5" sx={{ fontSize: '20px', fontWeight: 500, color: '#111827' }}>Upgrade Your Plan</Typography>
                    </Box>

                    <Grid container spacing={3}>
                        {plansLoading ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%', py: 4 }}>
                                <CircularProgress size={32} />
                            </Box>
                        ) : apiPlans.map((plan) => {
                            const planColor = plan.name.toLowerCase() === 'scale' ? '#8B5CF6' :
                                plan.name.toLowerCase() === 'growth' ? '#3b82f6' : '#10B981';
                            return (
                                <Grid size={{ xs: 12, md: 4 }} key={plan.name}>
                                    <Card elevation={0} sx={{
                                        height: '100%', borderRadius: '16px',
                                        border: (engineHasActivePlan && currentPlanRaw.toLowerCase() === plan.name.toLowerCase()) ? `2px solid ${planColor}` : '1px solid #E5E7EB',
                                        transition: 'all 0.2s ease', display: 'flex', flexDirection: 'column',
                                        '&:hover': { transform: 'translateY(-4px)', boxShadow: '0 8px 16px rgba(0,0,0,0.08)' },
                                    }}>
                                        <CardContent sx={{ p: 3, flex: 1, display: 'flex', flexDirection: 'column' }}>
                                            {engineHasActivePlan && currentPlanRaw.toLowerCase() !== plan.name.toLowerCase() && (
                                                <Alert severity="info" sx={{ mb: 2, fontSize: '12px', '& .MuiAlert-message': { padding: '4px 0' } }}>
                                                    Active plan detected. Cancel to switch.
                                                </Alert>
                                            )}
                                            <Typography sx={{ fontSize: '18px', fontWeight: 500, color: '#111827', mb: 1 }}>{plan.name}</Typography>
                                            <Typography sx={{ fontSize: '32px', fontWeight: 600, color: '#111827', mb: 0.5 }}>${plan.price}</Typography>
                                            <Typography sx={{ fontSize: '13px', color: '#6B7280', mb: 2 }}>{plan.volume}</Typography>
                                            <Box sx={{ mt: 'auto' }}>
                                                <Button fullWidth
                                                    variant={engineHasActivePlan && currentPlanRaw.toLowerCase() === plan.name.toLowerCase() ? 'outlined' : 'contained'}
                                                    onClick={() => handleUpgrade(plan.name)}
                                                    disabled={!!processingItem || (currentPlanRaw.toLowerCase() === plan.name.toLowerCase()) || (engineHasActivePlan && currentPlanRaw.toLowerCase() !== plan.name.toLowerCase())}
                                                    sx={{
                                                        textTransform: 'none', fontWeight: 500, py: 1.2, borderRadius: '10px',
                                                        ...(engineHasActivePlan && currentPlanRaw.toLowerCase() === plan.name.toLowerCase() ? { borderColor: planColor, color: planColor } : { bgcolor: 'rgba(139, 92, 246, 1)', '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.9)' } }),
                                                    }}
                                                >
                                                    {currentPlanRaw.toLowerCase() === plan.name.toLowerCase()
                                                        ? 'Current Plan'
                                                        : engineHasActivePlan ? 'Cancel to switch' : (processingItem === plan.name ? 'Processing...' : 'Upgrade')}
                                                </Button>
                                            </Box>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            );
                        })}
                    </Grid>
                </Box> */}

                {/* Buy Addon Credits */}
                <FadeIn delay={0.06}>
                <Paper elevation={0} sx={{ p: 4, borderRadius: '18px', border: '1px solid #E5E7EB', bgcolor: '#FFFFFF', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
                        <ShoppingCartIcon sx={{ fontSize: 28, color: '#10B981' }} />
                        <Typography variant="h5" sx={{ fontSize: '20px', fontWeight: 500, color: '#111827' }}>Buy Addon Credits</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
                        <Box>
                            <Typography sx={{ fontSize: '16px', fontWeight: 500, color: '#111827', mb: 0.5 }}>100 Additional Credits</Typography>
                            <Typography sx={{ fontSize: '14px', color: '#6B7280' }}>One-time purchase • Never expires • $20</Typography>
                        </Box>
                        <Button variant="contained"
                            startIcon={processingItem === 'ADDON_100' ? <CircularProgress size={16} color="inherit" /> : <ShoppingCartIcon />}
                            onClick={() => handleBuyAddon('ADDON_100')} disabled={!!processingItem}
                            sx={{ bgcolor: '#10B981', color: '#FFFFFF', textTransform: 'none', fontWeight: 500, px: 3, py: 1.2, borderRadius: '18px', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)', '&:hover': { bgcolor: '#10B981', filter: 'brightness(0.9)', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' } }}
                        >
                            {processingItem === 'ADDON_100' ? 'Processing...' : 'Buy Now'}
                        </Button>
                    </Box>
                </Paper>
                </FadeIn>
            </Container>
        </Box>
    );
};

export default BillingPage;
