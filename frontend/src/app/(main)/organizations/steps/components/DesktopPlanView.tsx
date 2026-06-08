"use client";

import { PlanCard } from "./DesktopPlanCard";
import { Check, Minus, HelpCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { LucideIcon } from "lucide-react";

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

interface DesktopPlanViewProps {
  plans: Plan[];
  features: Feature[];
  selectedPlan: string;
  onSelectPlan: (planId: string) => void;
  isTablet?: boolean;
}

export function DesktopPlanView({
  plans,
  features,
  selectedPlan,
  onSelectPlan,
  isTablet = false,
}: DesktopPlanViewProps) {
  // Find the index of the selected plan
  const selectedIndex = plans.findIndex((p) => p.id === selectedPlan);

  return (
    <div className="w-full overflow-x-auto pb-4">
      <div className="min-w-[900px]">
        {/* Header row: cards */}
        <div
          className={`grid ${
            isTablet
              ? "grid-cols-[1.5fr_1fr_1fr_1fr]"
              : "grid-cols-[2fr_1fr_1fr_1fr]"
          } w-full gap-0 items-start`}
        >
          <div />
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={` ${
                selectedPlan === plan.id
                  ? "border-t-2 border-l-2 border-r-2 border-purple-200 rounded-t-xl"
                  : ""
              }`}
            >
              <PlanCard
                {...plan}
                isSelected={selectedPlan === plan.id}
                onSelect={onSelectPlan}
              />
            </div>
          ))}
        </div>

        {/* Features grid: each row uses same columns so ticks align */}
        <div className="w-full">
          {features.map((feature, idx) => (
            <div
              key={feature.name + idx}
              className={`grid ${
                isTablet
                  ? "grid-cols-[1.5fr_1fr_1fr_1fr]"
                  : "grid-cols-[2fr_1fr_1fr_1fr]"
              } items-center ${idx % 2 === 0 ? "bg-gray-50" : "bg-white"}`}
            >
              <div
                className={`${
                  isTablet ? "p-3" : "p-4"
                } text-sm text-gray-900 font-medium flex items-center gap-2 h-16`}
              >
                <span className="text-sm">
                  {feature.name}
                </span>
                {feature.hasInfo && (
                  <HelpCircle className="w-4 h-4 text-gray-400 flex-shrink-0" />
                )}
              </div>

              {plans.map((plan) => {
                const value = feature[plan.id as keyof typeof feature];
                return (
                  <div
                    key={plan.id}
                    className={`flex justify-center items-center p-4 h-16 ${
                      selectedPlan === plan.id
                        ? "border-l-2 border-r-2 border-purple-200"
                        : ""
                    }`}
                  >
                    {value ? (
                      <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                        <Check className="w-4 h-4 text-green-600" />
                      </div>
                    ) : (
                      <Minus className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        {/* Footer row with Get Started buttons; bottom border closes selected column */}
        <div
          className={`grid ${
            isTablet
              ? "grid-cols-[1.5fr_1fr_1fr_1fr]"
              : "grid-cols-[2fr_1fr_1fr_1fr]"
          } w-full gap-0 items-center`}
        >
          <div />
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`p-6 flex items-center justify-center ${
                selectedPlan === plan.id
                  ? "border-l-2 border-r-2 border-b-2 border-purple-200 rounded-b-xl"
                  : ""
              }`}
            >
              <Button
                type="button"
                color="purple"
                onClick={() => onSelectPlan(plan.id)}
                className="w-full"
              >
                Get started
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
