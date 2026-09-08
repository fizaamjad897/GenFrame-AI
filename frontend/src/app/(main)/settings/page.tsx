'use client';

import React from 'react';
import { Box, Container, Typography, Paper, Stack, Avatar, Divider, Button, Chip, Alert } from '@mui/material';
import { useUser } from '@/app/context/AuthContext';
import { usePageHeader } from '@/app/context/PageHeaderContext';
import { Person as PersonIcon, Email as EmailIcon, Badge as BadgeIcon, Security as SecurityIcon } from '@mui/icons-material';
import { getPlanLabel } from '@/types/billing';
import { cancelSubscription, redirectToPortal } from '@/lib/stripe';
import { CREAM, INK, ACCENT, TEXT_MUTED_L, BORDER_L, GOOD, MONO } from '@/app/theme/terminal';
import { PopIn } from '@/components/motion/Reveal';

const sectionSx = { p: 4, borderRadius: '18px', border: `1px solid ${BORDER_L}`, bgcolor: '#FFFFFF', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' };
const labelSx = { color: TEXT_MUTED_L, fontFamily: MONO, fontSize: 11, textTransform: 'uppercase' as const, letterSpacing: '0.06em', mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 };

export default function SettingsPage() {
    const { user, refreshUser } = useUser();
    const { setHeader, resetHeader } = usePageHeader();
    const [processing, setProcessing] = React.useState<'portal' | 'cancel' | null>(null);
    const [error, setError] = React.useState<string | null>(null);
    const [success, setSuccess] = React.useState<string | null>(null);

    React.useEffect(() => {
        setHeader({ title: 'Account Settings' });
        return () => resetHeader();
    }, [setHeader, resetHeader]);

    if (!user) return null;

    const hasSubscription = Boolean(user.stripeSubscriptionId);
    const isPostpaid = Boolean(user.is_postpaid);

    const handleOpenPortal = async () => {
        setProcessing('portal');
        setError(null);
        setSuccess(null);
        try {
            await redirectToPortal();
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Failed to open billing portal');
        } finally {
            setProcessing(null);
        }
    };

    const handleCancelNow = async () => {
        if (!user.stripeSubscriptionId) return;
        if (!window.confirm('Cancel your subscription immediately? You will lose included monthly credits.')) return;
        setProcessing('cancel');
        setError(null);
        setSuccess(null);
        try {
            await cancelSubscription(false);
            await refreshUser();
            setSuccess('Subscription cancelled successfully.');
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Failed to cancel subscription');
        } finally {
            setProcessing(null);
        }
    };

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

                <Stack spacing={4}>
                    {/* Profile Section */}
                    <PopIn>
                    <Paper elevation={0} sx={sectionSx}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 3, mb: 4 }}>
                            <Avatar
                                src={user.avatar}
                                sx={{ width: 80, height: 80, border: `2px solid ${ACCENT}33`, bgcolor: INK, color: CREAM, fontFamily: MONO }}
                            >
                                {user.fullName?.charAt(0)}
                            </Avatar>
                            <Box>
                                <Typography variant="h6" sx={{ fontWeight: 600, color: INK }}>{user.fullName}</Typography>
                                <Typography variant="body2" sx={{ color: TEXT_MUTED_L }}>{user.email}</Typography>
                            </Box>
                        </Box>

                        <Divider sx={{ mb: 4, borderColor: BORDER_L, borderStyle: 'solid' }} />

                        <Stack spacing={3}>
                            <Box>
                                <Typography variant="subtitle2" sx={labelSx}>
                                    <PersonIcon fontSize="small" /> Full Name
                                </Typography>
                                <Typography variant="body1" sx={{ fontWeight: 500, color: INK }}>{user.fullName}</Typography>
                            </Box>

                            <Box>
                                <Typography variant="subtitle2" sx={labelSx}>
                                    <EmailIcon fontSize="small" /> Email Address
                                </Typography>
                                <Typography variant="body1" sx={{ fontWeight: 500, color: INK }}>{user.email}</Typography>
                            </Box>

                            <Box>
                                <Typography variant="subtitle2" sx={labelSx}>
                                    <BadgeIcon fontSize="small" /> Account ID
                                </Typography>
                                <Typography variant="body1" sx={{ color: TEXT_MUTED_L, fontSize: '13px', fontFamily: MONO }}>{user.id}</Typography>
                            </Box>
                        </Stack>
                    </Paper>
                    </PopIn>

                    {/* Subscription Section */}
                    {!isPostpaid && (
                    <PopIn delay={0.06}>
                    <Paper elevation={0} sx={sectionSx}>
                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: INK }}>Subscription & Usage</Typography>

                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', p: 3, bgcolor: CREAM, borderRadius: '18px', border: `1px solid ${BORDER_L}` }}>
                            <Box>
                                <Typography sx={{ fontSize: '11px', fontFamily: MONO, textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 500, color: TEXT_MUTED_L, mb: 0.5 }}>Current Plan</Typography>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                                    <Typography variant="h5" sx={{ fontWeight: 600, color: ACCENT }}>
                                        {getPlanLabel(user.plan)}
                                    </Typography>
                                    <Chip
                                        label={hasSubscription ? "Active" : "Inactive"}
                                        size="small"
                                        sx={{
                                            borderRadius: '18px',
                                            bgcolor: 'transparent',
                                            border: `1px solid ${hasSubscription ? GOOD : BORDER_L}`,
                                            color: hasSubscription ? GOOD : TEXT_MUTED_L,
                                            fontWeight: 500,
                                            fontFamily: MONO,
                                            fontSize: '11px'
                                        }}
                                    />
                                </Box>
                            </Box>
                            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.25} sx={{ alignItems: { sm: 'center' } }}>
                                {hasSubscription && (
                                    <>
                                        <Button
                                            variant="outlined"
                                            onClick={handleOpenPortal}
                                            disabled={processing !== null}
                                            sx={{
                                                borderRadius: '18px',
                                                textTransform: 'none',
                                                borderColor: BORDER_L,
                                                color: INK,
                                                '&:hover': { borderColor: ACCENT, bgcolor: 'transparent' },
                                            }}
                                        >
                                            {processing === 'portal' ? 'Opening…' : 'Manage Billing'}
                                        </Button>
                                        <Button
                                            variant="outlined"
                                            onClick={handleCancelNow}
                                            disabled={processing !== null}
                                            sx={{
                                                borderRadius: '18px',
                                                textTransform: 'none',
                                                fontWeight: 600,
                                                borderColor: '#EF444455',
                                                color: '#EF4444',
                                                '&:hover': { borderColor: '#EF4444', bgcolor: 'transparent' },
                                            }}
                                        >
                                            {processing === 'cancel' ? 'Cancelling…' : 'Cancel Plan'}
                                        </Button>
                                    </>
                                )}
                            </Stack>
                        </Box>

                        <Box sx={{ mt: 3, display: 'flex', gap: 4 }}>
                            <Box>
                                <Typography variant="caption" sx={{ color: TEXT_MUTED_L, fontFamily: MONO, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Available Credits</Typography>
                                <Typography variant="h6" sx={{ fontWeight: 600, color: INK, fontFamily: MONO }}>{(user.maxUnits - user.units).toLocaleString()}</Typography>
                            </Box>
                            <Box>
                                <Typography variant="caption" sx={{ color: TEXT_MUTED_L, fontFamily: MONO, fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Total Capacity</Typography>
                                <Typography variant="h6" sx={{ fontWeight: 600, color: INK, fontFamily: MONO }}>{user.maxUnits.toLocaleString()}</Typography>
                            </Box>
                        </Box>
                    </Paper>
                    </PopIn>
                    )}

                    {/* Security Section (Placeholder) */}
                    <PopIn delay={0.12}>
                    <Paper elevation={0} sx={sectionSx}>
                        <Typography variant="h6" sx={{ fontWeight: 600, mb: 3, color: INK }}>Security</Typography>
                        <Button
                            startIcon={<SecurityIcon />}
                            variant="outlined"
                            disabled
                            sx={{
                                borderRadius: '18px',
                                textTransform: 'none',
                                borderColor: BORDER_L,
                                color: TEXT_MUTED_L,
                                boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)'
                            }}
                        >
                            Password Reset (Disabled in Demo)
                        </Button>
                    </Paper>
                    </PopIn>
                </Stack>
            </Container>
        </Box>
    );
}
