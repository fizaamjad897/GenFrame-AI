"use client";

import { OrganizationDetails } from "./components/OrganizationDetails";
import { EngineSelectionSummary } from "./components/EngineSelectionSummary";

interface ReviewFormData {
  organizationName?: string;
  primaryEmail?: string;
  phone?: string;
  region?: string;
  timeZone?: string;
  industry?: string;
  selectedEngines?: string[];
  transformationCreditsThreshold?: number;
  transformationCreditPrice?: number;
  creationCreditsThreshold?: number;
  creationCreditPrice?: number;
}
interface ReviewStepProps {
  formData: ReviewFormData;
  update?: boolean;
}

export function ReviewStep({ formData, update }: ReviewStepProps) {
  return (
    <div className="space-y-6 pb-6">
      <OrganizationDetails
        organizationName={formData.organizationName}
        primaryEmail={formData.primaryEmail}
        phone={formData.phone}
        region={formData.region}
        timeZone={formData.timeZone}
        industry={formData.industry}
      />

      {/* Engine Selection Summary */}
      {formData.selectedEngines && formData.selectedEngines.length > 0 && (
        <EngineSelectionSummary
          selectedEngines={formData.selectedEngines}
          transformationCreditsThreshold={
            formData.transformationCreditsThreshold
          }
          transformationCreditPrice={formData.transformationCreditPrice}
          creationCreditsThreshold={formData.creationCreditsThreshold}
          creationCreditPrice={formData.creationCreditPrice}
        />
      )}
    </div>
  );
}
