"use client";

// import { FeatureRow } from "./FeatureRow";
import { HelpCircle, Check } from "lucide-react";

interface Plan {
  id: string;
  name: string;
}

interface Feature {
  name: string;
  basic: boolean;
  business: boolean;
  enterprise: boolean;
  hasInfo?: boolean;
}

interface PlanComparisonTableProps {
  plans: Plan[];
  features: Feature[];
  selectedPlan: string;
}

export function PlanComparisonTable({
  plans,
  features,
  selectedPlan,
}: PlanComparisonTableProps) {
  return (
    <div className="w-full">
      {features.map((feature, index) => (
        <div
          key={feature.name}
          className={`grid grid-cols-[2fr_1fr_1fr_1fr] items-center ${
            index % 2 === 0 ? "bg-gray-50/50" : "bg-white"
          }`}
        >
          {/* Feature Name */}
          <div className="p-4 text-sm text-gray-700 flex items-center">
            {feature.name}
            {feature.hasInfo && (
              <HelpCircle className="ml-2 w-4 h-4 text-gray-400 flex-shrink-0" />
            )}
          </div>

          {/* Plan Columns */}
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`flex justify-center p-4 ${
                selectedPlan === plan.id
                  ? "border-2 border-purple-200 border-t-0"
                  : ""
              }`}
            >
              {feature[plan.id as keyof Feature] ? (
                <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                  <Check className="w-4 h-4 text-success-500" />
                </div>
              ) : (
                "—"
              )}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
