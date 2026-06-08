'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Auth from '../components/Auth';
import { useAuth } from '@/app/context/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';

function AuthPageContent() {
  const [mounted, setMounted] = useState(false);
  const { user, loading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const tab = searchParams.get('tab') as 'signup' | 'login' | null;
  const redirect = searchParams.get('redirect');

  useEffect(() => {
    if (!loading && user) {
      router.push(redirect || '/dashboard');
    }
  }, [user, loading, router, redirect]);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted || loading || user) {
    return null;
  }

  return <Auth initialTab={tab || 'login'} redirectTo={redirect || undefined} />;
}

export default function AuthPage() {
  return (
    <Suspense fallback={null}>
      <AuthPageContent />
    </Suspense>
  );
}
