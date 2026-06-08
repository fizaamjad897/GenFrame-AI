'use client';

import React, { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Box, CircularProgress } from '@mui/material';
import Auth from '../components/Auth';

function ResetPasswordWrapper() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token') || '';
  
  // Render the original Auth layout but initialized in "reset" mode
  // The token is passed so it can be handled by the internal Auth state.
  return <Auth initialTab="reset" initialToken={token} />;
}

export default function ResetPasswordPage() {
  return (
    <Suspense 
      fallback={
        <Box sx={{ display: 'flex', minHeight: '100vh', justifyContent: 'center', alignItems: 'center' }}>
          <CircularProgress sx={{ color: 'rgba(3, 105, 161, 1)' }} />
        </Box>
      }
    >
      <ResetPasswordWrapper />
    </Suspense>
  );
}
