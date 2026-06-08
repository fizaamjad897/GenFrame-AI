/**
 * Stripe-specific API functions
 */

import { authFetch } from './api';
import type {
    CheckoutRequest,
    CheckoutResponse,
    PortalResponse,
    Plan,
    BillingRecord,
    UsageStats,
    EngineType,
    OrderType,
} from '@/types/billing';
import { loadStripe } from '@stripe/stripe-js';

const NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || '';

// Initialize Stripe
export const getStripe = () => {
    if (!NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY) {
        console.warn('⚠️ STRIPE_PUBLISHABLE_KEY is missing!');
        return null;
    }
    return loadStripe(NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY);
};

// Log Stripe Mode on load
if (typeof window !== 'undefined') {
    const key = NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
    if (key) {
        const mode = key.startsWith('pk_live_') ? 'LIVE' : 'TEST';
        console.log(`💳 [STRIPE] Initialized in ${mode} mode.`);
        if (mode === 'TEST') {
            console.log('ℹ️  You are using test keys. Real payments will NOT be processed.');
        }
    } else {
        console.error('❌ [STRIPE] Publishable key is missing! Checkout will fail.');
    }
}

/**
 * Create a Stripe checkout session for subscription or addon
 */
export async function createCheckoutSession(
    planCode: string,
    engineType: EngineType,
    orderType: OrderType = 'subscription'
): Promise<string> {
    const body: CheckoutRequest = {
        plan_code: planCode,
        engine_type: engineType,
        order_type: orderType,
    };

    const response = await authFetch<CheckoutResponse>('/stripe/create-checkout', {
        method: 'POST',
        body: JSON.stringify(body),
    });

    return response.url;
}

/**
 * Create a Stripe billing portal session
 */
export async function createPortalSession(): Promise<string> {
    const response = await authFetch<PortalResponse>('/stripe/create-portal', {
        method: 'POST',
    });

    return response.url;
}

/**
 * Manually refresh subscription status from Stripe.
 * Useful if webhook is delayed or for recovery.
 */
export async function refreshSubscriptionStatus(): Promise<{
    message: string;
    subscription_id?: string;
    plan?: string;
    engine?: string;
}> {
    try {
        return await authFetch('/stripe/refresh-subscription', {
            method: 'POST',
        });
    } catch (error) {
        console.error('Failed to refresh subscription:', error);
        throw error;
    }
}

/**
 * Cancel the active subscription.
 * If atPeriodEnd is true, cancels at period end; otherwise cancels immediately.
 * If engineType is specified, only cancels that engine's subscription.
 */
export async function cancelSubscription(atPeriodEnd = false, engineType?: string): Promise<{
    cancelled: boolean;
    at_period_end: boolean;
    engine_type?: string;
}> {
    try {
        return await authFetch('/stripe/cancel-subscription', {
            method: 'POST',
            body: JSON.stringify({
                at_period_end: atPeriodEnd,
                ...(engineType && { engine_type: engineType })
            }),
        });
    } catch (error) {
        console.error('Failed to cancel subscription:', error);
        throw error;
    }
}

/**
 * Get all available pricing plans
 */
export async function getPlans(): Promise<Plan[]> {
    return authFetch<Plan[]>('/plans', {
        method: 'GET',
    });
}

/**
 * Get billing history for the current user
 */
export async function getBillingHistory(): Promise<BillingRecord[]> {
    return authFetch<BillingRecord[]>('/users/billing-history', {
        method: 'GET',
    });
}

/**
 * Get usage statistics for the current user
 */
export async function getUsageStats(): Promise<UsageStats> {
    return authFetch<UsageStats>('/users/usage', {
        method: 'GET',
    });
}

/**
 * Helper function to redirect to Stripe checkout
 */
export async function redirectToCheckout(
    planCode: string,
    engineType: EngineType,
    orderType: OrderType = 'subscription'
): Promise<void> {
    try {
        const url = await createCheckoutSession(planCode, engineType, orderType);
        window.location.href = url;
    } catch (error) {
        console.error('Failed to create checkout session:', error);
        throw error;
    }
}

/**
 * Helper function to start a special $1 test checkout
 * (for the configured tester account only).
 */
export async function redirectToTestCheckout(): Promise<void> {
    try {
        const response = await authFetch<{ url: string }>('/stripe/create-test-checkout', {
            method: 'POST',
        });
        window.location.href = response.url;
    } catch (error) {
        console.error('Failed to create test checkout session:', error);
        throw error;
    }
}

/**
 * Helper function to redirect to Stripe billing portal
 */
export async function redirectToPortal(): Promise<void> {
    try {
        const url = await createPortalSession();
        window.location.href = url;
    } catch (error) {
        console.error('Failed to create portal session:', error);
        throw error;
    }
}
