/**
 * Type definitions for billing and Stripe integration
 */

export interface Credits {
    monthly_units_used: number;
    monthly_units_max: number;
    addon_units_used: number;
    addon_units_max: number;
    remaining_units: number;
    overageRate?: number;
    is_pending_cancellation?: boolean;
}

export interface EngineInfo {
    plan: string;
    credits: Credits;
    is_pending_cancellation?: boolean;
    stripeSubscriptionId?: string;
    updatedAt?: string;
}

export interface User {
    id: string;
    email: string;
    fullName: string;
    avatar?: string;
    plan: string;
    engineType: EngineType;
    units: number;
    maxUnits: number;
    remainingUnits?: number;
    credits: Credits;
    engine_data?: {
        [key in EngineType]?: EngineInfo;
    };
    available_engines?: string[];
    stripeCustomerId?: string;
    stripeSubscriptionId?: string;
    is_postpaid?: boolean;
    role?: string;
    createdAt: string;
}

export function getPlanLabel(plan?: string): string {
    const normalized = (plan || '').trim();
    return normalized.length > 0 ? normalized : 'No active subscription';
}

export function hasActiveSubscription(user?: User | null): boolean {
    // Priority 1: Check if user has top-level plan or stripeSubscriptionId
    if (user?.stripeSubscriptionId || (user?.plan || '').trim()) return true;

    // Priority 2: Check any engine for active plan or subscription ID
    const engines = user?.engine_data || {};
    for (const engine of Object.values(engines)) {
        if ((engine?.plan && engine.plan.trim().length > 0) || engine?.stripeSubscriptionId) {
            return true;
        }
    }

    // Priority 3: Lenient check - if user has credits/remaining units, treat as active for UI purposes
    if ((user?.remainingUnits || 0) > 0) return true;
    if (user?.credits && (user.credits.remaining_units > 0)) return true;

    return false;
}

/**
 * Check if a specific engine has an active subscription
 */
export function hasEngineActiveSubscription(user: User | null | undefined, engineType: EngineType): boolean {
    if (!user) return false;

    // 1. Check for engine-specific credits first (most accurate)
    const engineInfo = user.engine_data?.[engineType];
    const engineCredits = engineInfo?.credits;
    const remainingInEngine = engineCredits?.remaining_units ?? -1;

    // 2. Check top-level credits if this is the active engine
    const isMainEngine = user.engineType === engineType;
    const topRemaining = user.remainingUnits ?? -1;

    // 3. Priority logic: If ANY explicit credits are found > 0, they are active
    if (remainingInEngine > 0) return true;
    if (isMainEngine && topRemaining > 0) return true;

    // 4. Fallback to plan/sub ID based checks (for unlimited or new plans)
    const hasSubId = Boolean(engineInfo?.stripeSubscriptionId) || Boolean(user.stripeSubscriptionId);
    const hasPlan = Boolean(engineInfo?.plan) || (isMainEngine && Boolean(user.plan));
    const isPending = Boolean(engineInfo?.is_pending_cancellation) || Boolean(engineCredits?.is_pending_cancellation);

    if (hasPlan && (hasSubId || hasPlan)) {
        return !isPending;
    }

    return false;
}

/**
 * Get the plan for a specific engine
 */
export function getEnginePlan(user: User | null | undefined, engineType: EngineType): string {
    if (!user) return '';

    // Check engine-specific plan first
    const engineInfo = user.engine_data?.[engineType];
    if (engineInfo?.plan && engineInfo.plan.trim().length > 0) {
        return engineInfo.plan;
    }

    // Fallback: if user's engineType matches, use top-level plan
    if (user.engineType === engineType && user.plan && user.plan.trim().length > 0) {
        return user.plan;
    }

    return '';
}

/**
 * Check if a specific plan is active for a specific engine
 */
export function isPlanActiveForEngine(user: User | null | undefined, planName: string, engineType: EngineType): boolean {
    const enginePlan = getEnginePlan(user, engineType);
    return enginePlan.toLowerCase() === planName.toLowerCase() && hasEngineActiveSubscription(user, engineType);
}

export interface Plan {
    _id: string;
    name: string;
    price: number;
    includedUnits: number;
    costPerUnit: number;
    bestFor: string;
    features: string[];
    isActive: boolean;
    volume?: string; // e.g., "1,000 units/mo"
}

export interface CheckoutRequest {
    plan_code: string;
    engine_type: 'creation' | 'transformation';
    order_type: 'subscription' | 'addon';
}

export interface CheckoutResponse {
    url: string;
}

export interface PortalResponse {
    url: string;
}

export interface BillingRecord {
    _id: string;
    userId: string;
    billingPeriodStart: string;
    billingPeriodEnd: string;
    plan: string;
    basePrice: number;
    includedUnits: number;
    unitsUsed: number;
    overageUnits: number;
    overageCharge: number;
    totalAmount: number;
    generatedAt: string;
    status: 'pending' | 'paid' | 'overdue';
}

export interface UsageStats {
    userId: string;
    plan: string;
    unitsUsed: number;
    maxUnits: number;
    remainingUnits: number;
    overageUnits: number;
    currentMonthOperations: number;
}

export type EngineType = 'creation' | 'transformation';
export type OrderType = 'subscription' | 'addon';

export const ADDON_PLANS = {
    ADDON_50: { units: 50, price: 10 },
    ADDON_100: { units: 100, price: 20 },
    ADDON_200: { units: 200, price: 35 },
} as const;
