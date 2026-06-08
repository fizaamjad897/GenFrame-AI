"use client";

import {
    Box,
    Typography,
    Chip,
    Button,
    CircularProgress,
    Alert,
    Container,
    Grid,
    Card,
    CardContent,
    List,
    ListItem,
    ListItemIcon,
    ListItemText,
    ToggleButtonGroup,
    ToggleButton,
    Stack,
} from "@mui/material";
import { useEffect, useState } from "react";
import { usePricingPlans, Plan } from "@/hooks/usePricingPlans";
import { useUser } from "@/app/context/AuthContext";
import AuthModal from "../auth/AuthModal";
import { useRouter } from "next/navigation";
import { Check as CheckIcon, Star as StarIcon } from "@mui/icons-material";
import { redirectToCheckout } from "@/lib/stripe";
import type { EngineType } from "@/types/billing";
import {
    hasActiveSubscription,
    getEnginePlan,
    hasEngineActiveSubscription,
    isPlanActiveForEngine
} from "@/types/billing";
import { redirectToPortal } from "@/lib/stripe";
import SwitchPlanModal from '@/app/components/modals/SwitchPlanModal';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export default function PricingSection() {
    const { plans, loading, error } = usePricingPlans();
    const { user } = useUser();
    const router = useRouter();
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

            // Check if this specific plan is already active for the selected engine
            if (isPlanActiveForEngine(user, pricePlan, selectedEngine)) {
                return;
            }

            // Check if the selected engine has any active subscription
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
                bgcolor: "#f9fafb",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                pt: { xs: 8, md: 12 },
                px: { xs: 2, md: 4 },
                pb: { xs: 12, md: 20 },
                position: 'relative',
                overflow: 'hidden'
            }}
        >

            <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1 }}>
                {/* Header */}
                <Box sx={{ textAlign: 'center', mb: 10, maxWidth: '800px', mx: 'auto' }}>
                    <Typography
                        variant="h1"
                        sx={{
                            fontWeight: 700,
                            mb: 2.5,
                            color: "#111827",
                            letterSpacing: '-0.03em',
                            fontSize: { xs: '32px', md: '48px' },
                            background: 'linear-gradient(135deg, #111827 0%, #4B5563 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                        }}
                    >
                        Infrastructure Scale
                    </Typography>
                    <Typography
                        variant="body1"
                        sx={{
                            color: 'rgba(17, 24, 39, 0.5)',
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

                {/* Engine Type Selector - Re-engineered Toggle */}
                <Box sx={{ display: 'flex', justifyContent: 'center', mb: 12 }}>
                    <Box
                        sx={{
                            p: 0.8,
                            bgcolor: 'rgba(255, 255, 255, 0.4)',
                            backdropFilter: 'blur(40px)',
                            WebkitBackdropFilter: 'blur(40px)',
                            borderRadius: '24px',
                            display: 'flex',
                            position: 'relative',
                            border: '1px solid rgba(3,105,161,0.1)',

                            boxShadow: '0 20px 40px -10px rgba(0, 0, 0, 0.05)',
                        }}
                    >
                        <Box
                            sx={{
                                position: 'absolute',
                                width: '160px',
                                height: 'calc(100% - 12.8px)',
                                bgcolor: 'white',
                                borderRadius: '18px',
                                transition: 'all 0.4s cubic-bezier(0.19, 1, 0.22, 1)',
                                transform: selectedEngine === 'transformation' ? 'translateX(0)' : 'translateX(160px)',
                                zIndex: 0,
                                boxShadow: '0 4px 12px -2px rgba(0, 0, 0, 0.08)'
                            }}
                        />
                        <Button
                            disableRipple
                            onClick={() => setSelectedEngine('transformation')}
                            sx={{
                                width: '160px',
                                py: 1.2,
                                textTransform: 'none',
                                fontWeight: 600,
                                fontSize: '14px',
                                color: selectedEngine === 'transformation' ? '#0369A1' : '#6b7280',
                                zIndex: 1,
                                transition: 'all 0.3s ease',
                                '&:hover': { bgcolor: 'transparent', color: '#0369A1' }

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
                                fontWeight: 600,
                                fontSize: '14px',
                                color: selectedEngine === 'creation' ? '#0369A1' : '#6b7280',
                                zIndex: 1,
                                transition: 'all 0.3s ease',
                                '&:hover': { bgcolor: 'transparent', color: '#0369A1' }

                            }}
                        >
                            Creation
                        </Button>
                    </Box>
                </Box>

                {/* Pricing Cards */}
                {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
                        <CircularProgress size={48} thickness={2} sx={{ color: '#0369A1' }} />
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
                        <Grid container spacing={4} justifyContent="center" sx={{ alignItems: 'stretch' }}>
                            {plans.map((plan: Plan) => {
                                const features = getPlanFeatures(plan.name);
                                const isRecommended = plan.name.toLowerCase() === 'growth';

                                return (
                                    <Grid size={{ xs: 12, md: 4 }} key={plan._id}>
                                        <Box
                                            sx={{
                                                height: '100%',
                                                position: 'relative',
                                                transition: 'transform 0.2s ease-in-out',
                                                '&:hover': {
                                                    transform: 'translateY(-8px)',
                                                }
                                            }}
                                        >
                                            <Card
                                                elevation={0}
                                                sx={{
                                                    height: '100%',
                                                    borderRadius: '20px',
                                                    bgcolor: 'white',
                                                    border: '1px solid rgba(3,105,161,0.3)',
                                                    position: 'relative',
                                                    display: 'flex',
                                                    flexDirection: 'column',
                                                    overflow: 'hidden',
                                                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                                                }}
                                            >
                                                <CardContent sx={{ p: { xs: 3, md: 4 }, flex: 1, display: 'flex', flexDirection: 'column' }}>
                                                    {/* Plan Name & Tagline */}
                                                    <Box sx={{ mb: 3 }}>
                                                        <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                                                            <Typography
                                                                sx={{
                                                                    fontSize: '11px',
                                                                    color: isRecommended ? '#0369A1' : '#9ca3af',
                                                                    fontWeight: 700,
                                                                    letterSpacing: '0.12em',
                                                                    textTransform: 'uppercase'
                                                                }}
                                                            >
                                                                {plan.name}
                                                            </Typography>
                                                            {isRecommended && (
                                                                <Chip
                                                                    label="Most Popular"
                                                                    sx={{
                                                                        bgcolor: '#0369A1',
                                                                        color: 'white',
                                                                        fontWeight: 600,
                                                                        fontSize: '9px',
                                                                        height: '20px',
                                                                        px: 0.5,
                                                                        borderRadius: '6px',
                                                                        boxShadow: '0 4px 10px rgba(3,105,161,0.15)'
                                                                    }}
                                                                />
                                                            )}
                                                        </Stack>
                                                        <Typography
                                                            variant="h4"
                                                            sx={{
                                                                color: '#111827',
                                                                fontWeight: 600,
                                                                fontSize: '18px',
                                                                letterSpacing: '-0.01em',
                                                                lineHeight: 1.2
                                                            }}
                                                        >
                                                            {plan.bestFor}
                                                        </Typography>
                                                    </Box>

                                                    {/* Pricing Section */}
                                                    <Box sx={{ mb: 6 }}>
                                                        <Stack direction="row" alignItems="baseline" spacing={0.5}>
                                                            <Typography sx={{ fontSize: '40px', fontWeight: 700, color: '#111827', letterSpacing: '-0.02em' }}>
                                                                ${plan.price}
                                                            </Typography>
                                                            <Typography sx={{ fontSize: '14px', color: '#9ca3af', fontWeight: 500 }}>
                                                                /mo
                                                            </Typography>
                                                        </Stack>
                                                        <Box sx={{ mt: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                                                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: isRecommended ? '#0369A1' : '#e5e7eb' }} />

                                                            <Typography sx={{ fontSize: '14px', color: '#6b7280', fontWeight: 500 }}>
                                                                {plan.volume} monthly credits
                                                            </Typography>
                                                        </Box>
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
                                                            borderRadius: '12px',
                                                            fontSize: '13px',
                                                            fontWeight: 600,
                                                            mb: 4,
                                                            textTransform: 'none',
                                                            transition: 'all 0.4s cubic-bezier(0.19, 1, 0.22, 1)',
                                                            bgcolor: isRecommended ? '#0369A1' : '#111827',
                                                            color: 'white',
                                                            boxShadow: isRecommended
                                                                ? '0 10px 15px -3px rgba(3,105,161,0.3)'
                                                                : '0 10px 20px -5px rgba(0, 0, 0, 0.1)',
                                                            '&:hover': {
                                                                bgcolor: isRecommended ? '#075985' : '#000000',
                                                                transform: 'translateY(-1px)',
                                                                boxShadow: isRecommended
                                                                    ? '0 20px 25px -5px rgba(3,105,161,0.35)'
                                                                    : '0 15px 30px -8px rgba(0, 0, 0, 0.2)',
                                                            },

                                                            '&:disabled': {
                                                                bgcolor: '#f3f4f6',
                                                                color: '#9ca3af'
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
                                                        <Typography sx={{ color: '#111827', fontWeight: 700, fontSize: '14px', mb: 3 }}>
                                                            Platform Capabilities
                                                        </Typography>
                                                        <List sx={{ p: 0 }}>
                                                            {features.map((feature, idx) => (
                                                                <ListItem key={idx} sx={{ px: 0, py: 1 }}>
                                                                    <ListItemIcon sx={{ minWidth: 32 }}>
                                                                        <Box sx={{
                                                                            width: 20,
                                                                            height: 20,
                                                                            borderRadius: '6px',
                                                                            bgcolor: isRecommended ? 'rgba(3,105,161,0.1)' : '#f3f4f6',
                                                                            display: 'flex',
                                                                            alignItems: 'center',
                                                                            justifyContent: 'center'
                                                                        }}>
                                                                            <CheckIcon sx={{ fontSize: 13, color: isRecommended ? '#0369A1' : '#111827' }} />

                                                                        </Box>
                                                                    </ListItemIcon>
                                                                    <ListItemText
                                                                        primary={feature}
                                                                        primaryTypographyProps={{
                                                                            sx: { fontSize: '13px', color: '#4b5563', fontWeight: 450 }
                                                                        }}
                                                                    />
                                                                </ListItem>
                                                            ))}
                                                        </List>
                                                    </Box>
                                                </CardContent>
                                            </Card>
                                        </Box>
                                    </Grid>
                                );
                            })}
                        </Grid>
                    </>
                )}

                {/* Footnote Section */}
                <Box sx={{ mt: 16, textAlign: 'center', pb: 4 }}>
                    <Typography sx={{ color: '#9ca3af', fontSize: '14px', fontWeight: 500, mb: 4 }}>
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
                                    color: '#6b7280',
                                    fontSize: '14px',
                                    fontWeight: 700,
                                    cursor: 'pointer',
                                    transition: 'color 0.2s',
                                    '&:hover': { color: '#0369A1' }

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
