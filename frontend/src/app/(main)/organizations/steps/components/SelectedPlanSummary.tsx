"use client";

import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
interface Feature {
  name: string;
  hasInfo?: boolean;
}

interface PlanSummaryProps {
  id: string;
  name: string;
  price: number;
  description?: string;
  features: Feature[];
}

export function SelectedPlanSummary({
  id,
  name,
  price,
  description,
  features,
}: PlanSummaryProps) {
  return (
    <div className="w-full max-w-3xl">
      <div className="rounded-md border-2 border-gray-100 bg-white overflow-hidden">
        <div className="bg-gray-50 px-6 py-1 h-12">
          <div className="flex items-center justify-between">
            <h4 className="text-title font-semibold text-gray-900">{name}</h4>
            <div className="flex items-center gap-4">
              <div className="text-heading-h2 font-bold text-gray-900">
                ${price}/mth
              </div>
              <Button
                color="purpleSubtle"
                className="!text-purple-400 shadow-sm"
              >
                Selected
              </Button>
            </div>
          </div>
        </div>

        <div className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {features.map((f, idx) => (
              <div
                key={`${f.name}-${idx}`}
                className="flex items-start gap-2 text-sm text-gray-500"
              >
                <div className="w-6 h-6 rounded-full bg-purple-25 flex items-center justify-center">
                  <Check className="w-4 h-4 text-primary" />
                </div>
                <span>{f.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
