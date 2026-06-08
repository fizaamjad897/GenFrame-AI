'use client';

import { useState, useEffect } from 'react';

export interface Plan {
    _id: string;
    name: string;
    price: number;
    volume: string;
    costPerUnit: string;
    bestFor: string;
    description: string;
    billingPeriod: 'weekly' | 'monthly' | 'yearly';
    features: string[];
    isActive: boolean;
    overageRate: number;
}

export function usePricingPlans() {
    const [plans, setPlans] = useState<Plan[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchPlans = async () => {
            try {
                const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api';
                const response = await fetch(`${API_BASE_URL}/plans`);
                if (!response.ok) {
                    throw new Error('Failed to fetch pricing plans');
                }
                const data = await response.json();

                // Map backend data to frontend Plan interface if needed
                const formattedPlans: Plan[] = data.map((plan: any) => ({
                    _id: plan._id,
                    name: plan.name,
                    price: plan.price,
                    volume: `${plan.includedUnits.toLocaleString()} Credits`,
                    costPerUnit: `$${plan.costPerUnit.toFixed(3)}`,
                    bestFor: plan.bestFor,
                    description: plan.bestFor,
                    billingPeriod: 'monthly',
                    features: plan.features,
                    isActive: plan.isActive,
                    overageRate: plan.overageRate || 0.19 // Fallback to standard rate
                }));

                setPlans(formattedPlans);
            } catch (err: any) {
                console.error('Error fetching plans:', err);
                setError(err.message || 'Failed to load pricing plans');
            } finally {
                setLoading(false);
            }
        };

        fetchPlans();
    }, []);

    return { plans, loading, error };
}
