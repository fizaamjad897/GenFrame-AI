"use client";

import React, { useEffect } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Button,
} from '@mui/material';
import {
    Cancel as CancelIcon,
} from '@mui/icons-material';
import { useRouter } from 'next/navigation';
import { usePageHeader } from '@/app/context/PageHeaderContext';
import { PopIn } from '@/components/motion/Reveal';

const BillingCancelPage = () => {
    const router = useRouter();
    const { setHeader, resetHeader } = usePageHeader();

    useEffect(() => {
        setHeader({ title: 'Payment Cancelled' });
        return () => resetHeader();
    }, [setHeader, resetHeader]);

    return (
        <Box>
            <Container maxWidth="md" sx={{ py: { xs: 6, md: 10 } }}>
                <PopIn>
                <Paper
                    elevation={0}
                    sx={{
                        p: { xs: 4, md: 6 },
                        borderRadius: '18px',
                        border: '1px solid #E5E7EB',
                        bgcolor: '#FFFFFF',
                        textAlign: 'center',
                        boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
                    }}
                >
                    <Box
                        sx={{
                            width: 80, height: 80, borderRadius: '18px',
                            border: '1px solid rgba(180, 72, 47, 0.4)',
                            bgcolor: 'transparent',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            mx: 'auto', mb: 3,
                        }}
                    >
                        <CancelIcon sx={{ fontSize: 48, color: '#EF4444' }} />
                    </Box>

                    <Typography variant="h4" sx={{ fontSize: { xs: '24px', md: '32px' }, fontWeight: 500, color: '#111827', mb: 2 }}>
                        Payment Cancelled
                    </Typography>

                    <Typography sx={{ fontSize: '16px', color: '#6B7280', mb: 4, maxWidth: '500px', mx: 'auto' }}>
                        Your payment was cancelled and no charges were made to your account. You can try again whenever you're ready.
                    </Typography>

                    <Box sx={{ p: 3, borderRadius: '18px', bgcolor: '#FFFFFF', border: '1px solid #8B5CF6', mb: 4 }}>
                        <Typography sx={{ fontSize: '14px', color: '#111827', fontWeight: 500 }}>
                            Your current plan and credits remain unchanged
                        </Typography>
                    </Box>

                    <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
                        <Button variant="contained" onClick={() => router.push('/billing')}
                            sx={{ bgcolor: 'rgba(139, 92, 246, 1)', color: '#FFFFFF', textTransform: 'none', fontWeight: 500, px: 4, py: 1.2, borderRadius: '18px', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)', '&:hover': { bgcolor: 'rgba(139, 92, 246, 1)', filter: 'brightness(0.92)', boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)' } }}
                        >
                            Back to Billing
                        </Button>
                        <Button variant="outlined" onClick={() => router.push('/dashboard')}
                            sx={{ borderColor: '#E5E7EB', borderStyle: 'solid', color: '#111827', textTransform: 'none', fontWeight: 500, px: 4, py: 1.2, borderRadius: '18px', '&:hover': { borderColor: 'rgba(139, 92, 246, 1)', bgcolor: 'rgba(139, 92, 246, 0.04)' } }}
                        >
                            Go to Dashboard
                        </Button>
                    </Box>
                </Paper>
                </PopIn>
            </Container>
        </Box>
    );
};

export default BillingCancelPage;
