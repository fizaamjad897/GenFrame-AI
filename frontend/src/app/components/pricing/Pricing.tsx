"use client";

import {
    Box,
    Typography,
    Chip,
    Button,
    CircularProgress,
    Container,
    Grid,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    Stack,
} from "@mui/material";
import { useState } from "react";
import { usePricingPlans, Plan } from "@/hooks/usePricingPlans";
import { useUser } from "@/app/context/AuthContext";
import AuthModal from "../auth/AuthModal";
import { Check as CheckIcon } from "@mui/icons-material";
import type { EngineType } from "@/types/billing";
import {
    getEnginePlan,
    hasEngineActiveSubscription,
    isPlanActiveForEngine
} from "@/types/billing";
import { redirectToCheckout, redirectToPortal } from "@/lib/stripe";
import SwitchPlanModal from '@/app/components/modals/SwitchPlanModal';
import { CREAM, INK, ACCENT, TEXT_MUTED_L, BORDER_L, MONO } from "@/app/theme/terminal";

export default function PricingSection() {
    const { plans, loading } = usePricingPlans();
    const { user } = useUser();
    const [isAuthModalOpen, setAuthModalOpen] = useState(false);
    const [selectedEngine, setSelectedEngine] = useState<EngineType>('transformation');
    const [processingPlan, setProcessingPlan] = useState<string | null>(null);
    const [checkoutError, setCheckoutError] = useState<string | null>(null);
    const [switchPlanModal, setSwitchPlanModal] = useState<{ open: boolean, newPlan: string }>({ open: false, newPlan: '' });

    const handleCheckout = async (pricePlan: string) => {
        try {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                setAuthModalOpen(true);
                return;
            }

            if (isPlanActiveForEngine(user, pricePlan, selectedEngine)) {
                return;
            }

            if (hasEngineActiveSubscription(user, selectedEngine)) {
                setSwitchPlanModal({ open: true, newPlan: pricePlan });
                return;
            }

            setProcessingPlan(pricePlan);
            setCheckoutError(null);
            await redirectToCheckout(pricePlan, selectedEngine, 'subscription');
        } catch (error) {
            console.error("Checkout error:", error);
            setCheckoutError(error instanceof Error ? error.message : 'Failed to start checkout');
            setProcessingPlan(null);
        }
    };

    const handleOpenPortal = async () => {
        try {
            setCheckoutError(null);
            await redirectToPortal();
        } catch (e) {
            setCheckoutError(e instanceof Error ? e.message : 'Failed to open billing portal');
        }
    };

    const getPlanFeatures = (planName: string) => {
        const baseFeatures = [
            'AI-powered image processing',
            'Multiple aspect ratio presets',
            'Instant processing',
            'High-quality output',
        ];

        switch (planName.toLowerCase()) {
            case 'starter':
                return [...baseFeatures, 'Email support', 'Basic analytics'];
            case 'growth':
                return [...baseFeatures, 'Priority support', 'Advanced analytics', 'API access', 'Custom presets'];
            case 'scale':
                return [...baseFeatures, '24/7 Premium support', 'Advanced analytics', 'Full API access', 'Custom presets', 'Dedicated account manager', 'SLA guarantee'];
            default:
                return baseFeatures;
        }
    };

    return (
        <Box
            sx={{
                width: "100%",
                minHeight: "100vh",
                bgcolor: CREAM,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                pt: { xs: 8, md: 12 },
                px: { xs: 2, md: 4 },
                pb: { xs: 12, md: 20 },
            }}
        >

            <Container maxWidth="lg">
                {/* Header */}
                <Box sx={{ textAlign: 'center', mb: 8, maxWidth: '800px', mx: 'auto' }}>
                    <Typography
                        variant="h1"
                        sx={{
                            fontWeight: 600,
                            mb: 2.5,
                            color: INK,
                            letterSpacing: '-0.03em',
                            fontSize: { xs: '32px', md: '48px' },
                        }}
                    >
                        Infrastructure Scale
                    </Typography>
                    <Typography
                        variant="body1"
                        sx={{
                            color: TEXT_MUTED_L,
                            maxWidth: '580px',
                            mx: 'auto',
                            lineHeight: 1.6,
                            fontWeight: 500,
                            fontSize: '18px',
                            letterSpacing: '-0.01em'
                        }}
                    >
                        Enterprise-grade visual computing for modern teams.
                        Deploy at scale, process with zero latency.
                    </Typography>
                </Box>

                {/* Engine Type Selector */}
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 10 }}>
                    <Box
                        sx={{
                            bgcolor: 'transparent',
                            border: `1px solid ${BORDER_L}`,
                            borderRadius: '18px',
                            display: 'flex',
                        }}
                    >
                        <Button
                            disableRipple
                            onClick={() => setSelectedEngine('transformation')}
                            sx={{
                                width: '160px',
                                py: 1.2,
                                textTransform: 'none',
                                fontWeight: 500,
                                fontSize: '13px',
                                fontFamily: MONO,
                                borderRadius: 0,
                                color: selectedEngine === 'transformation' ? INK : TEXT_MUTED_L,
                                bgcolor: selectedEngine === 'transformation' ? '#FFFFFF' : 'transparent',
                                borderRight: `1px solid ${BORDER_L}`,
                                '&:hover': { bgcolor: selectedEngine === 'transformation' ? '#FFFFFF' : 'transparent', color: ACCENT }
                            }}
                        >
                            Transformation
                        </Button>
                        <Button
                            disableRipple
                            onClick={() => setSelectedEngine('creation')}
                            sx={{
                                width: '160px',
                                py: 1.2,
                                textTransform: 'none',
                                fontWeight: 500,
                                fontSize: '13px',
                                fontFamily: MONO,
                                borderRadius: 0,
                                color: selectedEngine === 'creation' ? INK : TEXT_MUTED_L,
                                bgcolor: selectedEngine === 'creation' ? '#FFFFFF' : 'transparent',
                                '&:hover': { bgcolor: selectedEngine === 'creation' ? '#FFFFFF' : 'transparent', color: ACCENT }
                            }}
                        >
                            Creation
                        </Button>
                    </Box>
                </Box>

                {/* Pricing Cards */}
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
                        <CircularProgress size={40} thickness={2} sx={{ color: ACCENT }} />
                    </Box>
                ) : (
                    <>
                        <SwitchPlanModal
                            open={switchPlanModal.open}
                            onClose={() => setSwitchPlanModal({ open: false, newPlan: '' })}
                            onCancel={async () => {
                                setSwitchPlanModal({ open: false, newPlan: '' });
                                await handleOpenPortal();
                            }}
                            currentPlan={getEnginePlan(user, selectedEngine) || 'Unknown'}
                            newPlan={switchPlanModal.newPlan}
                        />
                        {checkoutError && (
                            <Typography sx={{ textAlign: 'center', color: '#EF4444', fontSize: '13px', mb: 3 }}>
                                {checkoutError}
                            </Typography>
                        )}
                        <Grid container spacing={3} justifyContent="center" sx={{ alignItems: 'stretch' }}>
                            {plans.map((plan: Plan) => {
                                const features = getPlanFeatures(plan.name);
                                const isRecommended = plan.name.toLowerCase() === 'growth';

                                return (
                                    <Grid size={{ xs: 12, md: 4 }} key={plan._id}>
                                        <Card
                                            elevation={0}
                                            sx={{
                                                height: '100%',
                                                borderRadius: '18px',
                                                bgcolor: '#FFFFFF',
                                                border: isRecommended ? `1px solid ${ACCENT}` : `1px solid ${BORDER_L}`,
                                                boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                                                display: 'flex',
                                                flexDirection: 'column',
                                            }}
                                        >
                                            <CardContent sx={{ p: { xs: 3, md: 4 }, flex: 1, display: 'flex', flexDirection: 'column' }}>
                                                {/* Plan Name & Tagline */}
                                                <Box sx={{ mb: 3 }}>
                                                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                                                        <Typography
                                                            sx={{
                                                                fontSize: '11px',
                                                                color: isRecommended ? ACCENT : TEXT_MUTED_L,
                                                                fontWeight: 600,
                                                                letterSpacing: '0.12em',
                                                                textTransform: 'uppercase',
                                                                fontFamily: MONO,
                                                            }}
                                                        >
                                                            {plan.name}
                                                        </Typography>
                                                        {isRecommended && (
                                                            <Chip
                                                                label="Most Popular"
                                                                sx={{
                                                                    bgcolor: 'transparent',
                                                                    border: `1px solid ${ACCENT}`,
                                                                    color: ACCENT,
                                                                    fontWeight: 500,
                                                                    fontSize: '9px',
                                                                    height: '20px',
                                                                    px: 0.5,
                                                                    borderRadius: '18px',
                                                                }}
                                                            />
                                                        )}
                                                    </Stack>
                                                    <Typography
                                                        variant="h4"
                                                        sx={{
                                                            color: INK,
                                                            fontWeight: 500,
                                                            fontSize: '18px',
                                                            letterSpacing: '-0.01em',
                                                            lineHeight: 1.2
                                                        }}
                                                    >
                                                        {plan.bestFor}
                                                    </Typography>
                                                </Box>

                                                {/* Pricing Section */}
                                                <Box sx={{ mb: 5, pb: 3, borderBottom: `1px solid ${BORDER_L}` }}>
                                                    <Stack direction="row" alignItems="baseline" spacing={0.5}>
                                                        <Typography sx={{ fontSize: '40px', fontWeight: 600, color: INK, letterSpacing: '-0.02em', fontFamily: MONO }}>
                                                            ${plan.price}
                                                        </Typography>
                                                        <Typography sx={{ fontSize: '14px', color: TEXT_MUTED_L, fontWeight: 500 }}>
                                                            /mo
                                                        </Typography>
                                                    </Stack>
                                                    <Typography sx={{ fontSize: '14px', color: TEXT_MUTED_L, fontWeight: 500, mt: 1 }}>
                                                        {plan.volume} monthly credits
                                                    </Typography>
                                                </Box>

                                                {/* CTA Button */}
                                                <Button
                                                    fullWidth
                                                    variant="contained"
                                                    onClick={() => handleCheckout(plan.name)}
                                                    disabled={
                                                        !!processingPlan ||
                                                        isPlanActiveForEngine(user, plan.name, selectedEngine)
                                                    }
                                                    sx={{
                                                        py: 1.4,
                                                        borderRadius: '18px',
                                                        fontSize: '13px',
                                                        fontWeight: 500,
                                                        mb: 4,
                                                        textTransform: 'none',
                                                        boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                                                        bgcolor: isRecommended ? ACCENT : INK,
                                                        color: isRecommended ? INK : CREAM,
                                                        '&:hover': {
                                                            bgcolor: isRecommended ? ACCENT : INK,
                                                            filter: 'brightness(0.92)',
                                                            boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                                                        },
                                                        '&:disabled': {
                                                            bgcolor: '#FFFFFF',
                                                            color: '#9CA3AF'
                                                        }
                                                    }}
                                                >
                                                    {isPlanActiveForEngine(user, plan.name, selectedEngine)
                                                        ? 'Active Subscription'
                                                        : hasEngineActiveSubscription(user, selectedEngine)
                                                            ? 'Switch Plan'
                                                            : (processingPlan === plan.name ? 'Preparing...' : 'Get Started')}
                                                </Button>

                                                {/* Features List */}
                                                <Box sx={{ flex: 1 }}>
                                                    <Typography sx={{ color: INK, fontWeight: 600, fontSize: '12px', letterSpacing: '0.08em', textTransform: 'uppercase', fontFamily: MONO, mb: 2 }}>
                                                        Platform Capabilities
                                                    </Typography>
                                                    <List sx={{ p: 0 }}>
                                                        {features.map((feature, idx) => (
                                                            <ListItem key={idx} sx={{ px: 0, py: 0.8 }}>
                                                                <ListItemIcon sx={{ minWidth: 28 }}>
                                                                    <CheckIcon sx={{ fontSize: 15, color: isRecommended ? ACCENT : INK }} />
                                                                </ListItemIcon>
                                                                <ListItemText
                                                                    primary={feature}
                                                                    primaryTypographyProps={{
                                                                        sx: { fontSize: '13px', color: TEXT_MUTED_L, fontWeight: 450 }
                                                                    }}
                                                                />
                                                            </ListItem>
                                                        ))}
                                                    </List>
                                                </Box>
                                            </CardContent>
                                        </Card>
                                    </Grid>
                                );
                            })}
                        </Grid>
                    </>
                )}

                {/* Footnote Section */}
                <Box sx={{ mt: 12, textAlign: 'center', pb: 4, pt: 6, borderTop: `1px solid ${BORDER_L}` }}>
                    <Typography sx={{ color: TEXT_MUTED_L, fontSize: '14px', fontWeight: 500, mb: 4 }}>
                        Enterprise security provided as standard. ISO 27001 & SOC2 Type II redundant infrastructure.
                    </Typography>
                    <Stack
                        direction={{ xs: 'column', sm: 'row' }}
                        spacing={{ xs: 2, sm: 6 }}
                        justifyContent="center"
                        alignItems="center"
                    >
                        {['Infrastructure SLA', 'Security Whitepaper', 'API Integration'].map((link) => (
                            <Typography
                                key={link}
                                sx={{
                                    color: TEXT_MUTED_L,
                                    fontSize: '13px',
                                    fontWeight: 600,
                                    fontFamily: MONO,
                                    cursor: 'pointer',
                                    transition: 'color 0.2s',
                                    '&:hover': { color: ACCENT }

                                }}
                            >
                                {link}
                            </Typography>
                        ))}
                    </Stack>
                </Box>
            </Container>

            <AuthModal
                open={isAuthModalOpen}
                onClose={() => setAuthModalOpen(false)}
            />
        </Box>
    );
}
