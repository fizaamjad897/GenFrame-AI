"use client";

import { useState, useEffect } from "react";
import { MobilePlanView } from "./components/MobilePlanView";
import { DesktopPlanView } from "./components/DesktopPlanView";
import { useIsMobile, useIsTablet } from "@/hooks/useMediaQuery";
import { featuresData, plansData } from "@/utils/plansData";

interface PlanLicensesFormData {
  plan?: string;
}
interface PlanLicensesStepProps {
  formData: PlanLicensesFormData;
  onChange: (field: string, value: any) => void;
}

export function PlanLicensesStep({
  formData,
  onChange,
}: PlanLicensesStepProps) {
  const [selectedPlan, setSelectedPlan] = useState<string>(
    formData.plan || "business"
  );
  const [mounted, setMounted] = useState(false);

  const isMobile = useIsMobile();
  const isTablet = useIsTablet();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handlePlanSelect = (planId: string) => {
    setSelectedPlan(planId);
    onChange("plan", planId);
  };

  // Show desktop view during SSR and initial render to prevent layout shift
  if (!mounted) {
    return (
      <div className="w-full">
        <DesktopPlanView
          plans={plansData}
          features={featuresData}
          selectedPlan={selectedPlan}
          onSelectPlan={handlePlanSelect}
          isTablet={false}
        />
      </div>
    );
  }

  return (
    <div className="w-full">
      {isMobile ? (
        <MobilePlanView
          plans={plansData}
          features={featuresData}
          selectedPlan={selectedPlan}
          onSelectPlan={handlePlanSelect}
        />
      ) : (
        <DesktopPlanView
          plans={plansData}
          features={featuresData}
          selectedPlan={selectedPlan}
          onSelectPlan={handlePlanSelect}
          isTablet={isTablet}
        />
      )}
    </div>
  );
}
