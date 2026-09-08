"use client";

import React from 'react';
import { Box, Button, Container, Typography, Alert, CircularProgress, Paper } from '@mui/material';
import Header from '@/app/components/Header';
import { useUser } from '@/app/context/AuthContext';
import { redirectToTestCheckout } from '@/lib/stripe';

const TestCheckoutPage = () => {
  const { user } = useUser();
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  if (!user) {
    return (
      <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#FFFFFF' }}>
      <Header />
      <Container maxWidth="sm" sx={{ py: { xs: 4, md: 6 } }}>
        <Paper
          elevation={0}
          sx={{
            p: 4,
            borderRadius: '18px',
            border: '1px solid #E5E7EB',
            bgcolor: '#FFFFFF',
            boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
          }}
        >
          <Typography
            variant="h4"
            sx={{
              fontSize: { xs: '24px', md: '28px' },
              fontWeight: 600,
              color: '#111827',
              mb: 1,
            }}
          >
            $1 Tester Checkout
          </Typography>
          <Typography sx={{ fontSize: '14px', color: '#6B7280', mb: 3 }}>
            This private page lets you run a one-time $1 Stripe payment to confirm that live billing is configured
            correctly. It does not change your subscription or credits.
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Button
            fullWidth
            variant="contained"
            onClick={async () => {
              setLoading(true);
              setError(null);
              try {
                await redirectToTestCheckout();
              } catch (err) {
                setError(err instanceof Error ? err.message : 'Failed to start test checkout');
              } finally {
                setLoading(false);
              }
            }}
            disabled={loading}
            sx={{
              height: '48px',
              textTransform: 'none',
              fontWeight: 500,
              borderRadius: '18px',
              boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
              bgcolor: 'rgba(139, 92, 246, 1)',
              color: '#FFFFFF',
              '&:hover': {
                bgcolor: 'rgba(139, 92, 246, 1)',
                filter: 'brightness(0.92)',
                boxShadow: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
              },
            }}
          >
            {loading ? <CircularProgress size={20} color="inherit" /> : 'Start $1 Test Payment'}
          </Button>
        </Paper>
      </Container>
    </Box>
  );
};

export default TestCheckoutPage;

