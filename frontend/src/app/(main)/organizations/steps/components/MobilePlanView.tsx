"use client";

import { LucideIcon } from "lucide-react";
import { MobilePlanCard } from "./MobilePlanCard";

interface Plan {
  id: string;
  name: string;
  price: number;
  description: string;
  icon: LucideIcon;
  iconColor?: string;
  iconBg?: string;
}

interface Feature {
  name: string;
  basic: boolean;
  business: boolean;
  enterprise: boolean;
  hasInfo?: boolean;
}

interface MobilePlanViewProps {
  plans: Plan[];
  features: Feature[];
  selectedPlan: string;
  onSelectPlan: (planId: string) => void;
}

export function MobilePlanView({
  plans,
  features,
  selectedPlan,
  onSelectPlan,
}: MobilePlanViewProps) {
  // Transform features for each plan
  const getPlanFeatures = (planId: string) => {
    return features.map((feature) => ({
      name: feature.name,
      hasInfo: feature.hasInfo,
      included: feature[planId as keyof Feature] as boolean,
    }));
  };

  return (
    <div className="space-y-4 pb-8">
      {plans.map((plan) => (
        <MobilePlanCard
          key={plan.id}
          {...plan}
          isSelected={selectedPlan === plan.id}
          onSelect={onSelectPlan}
          features={getPlanFeatures(plan.id)}
        />
      ))}
    </div>
  );
}
