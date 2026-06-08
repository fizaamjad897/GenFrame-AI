"use client";

import { useState, useEffect } from "react";
import { Building2, ArrowRight, ArrowLeft, X } from "lucide-react";
import { SlideUpModal } from "@/components/ui/slide-up-modal";
import { StepIndicator, Step } from "@/components/ui/step-indicator";
import { Button } from "@/components/ui/button";
import { DetailStep } from "./steps/DetailStep";
import { EngineSelectionStep } from "./steps/EngineSelectionStep";
import { ReviewStep } from "./steps/ReviewStep";
import type { CreateOrganisationInput } from "@/types/organizationTypes";
import { toast } from "react-toastify";
import { isValidPhoneNumber } from "libphonenumber-js";
import { createOrganisation } from "@/lib/organisationApi";
import { validateEmail } from "@/lib/validationUtils";
import { extractApiErrorMessage } from "@/lib/errorMessage";
interface CreateOrganizationModalProps {
  isOpen: boolean;
  onClose: () => void;
  refetch?: any;
}

export function CreateOrganizationModal({
  isOpen,
  onClose,
  refetch,
}: CreateOrganizationModalProps) {
  const [createLoading, setCreateLoading] = useState(false);

  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState({
    // Step 1: Detail
    organizationName: "",
    primaryEmail: "",
    phone: "",
    region: "",
    timeZone: "",
    industry: "",
    // Step 2: Engine Selection
    selectedEngines: [] as string[],
    transformationCreditsThreshold: 0,
    transformationCreditPrice: 0,
    creationCreditsThreshold: 0,
    creationCreditPrice: 0,
    // Step 3: Review
  });

  // Pre-fill Time Zone and Region based on user's location
  useEffect(() => {
    if (!isOpen) return;

    // 1. Detect Time Zone String
    const offsetMinutes = new Date().getTimezoneOffset();
    const sign = offsetMinutes <= 0 ? "+" : "-";
    const absMinutes = Math.abs(offsetMinutes);
    const h = Math.floor(absMinutes / 60);
    const m = absMinutes % 60;
    const hStr = h.toString().padStart(2, "0");
    const mStr = m.toString().padStart(2, "0");
    const detectedTimeZone = `UTC${sign}${hStr}:${mStr}`;

    // 2. Detect Region based on IANA TimeZone
    const ianaTimeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    let detectedRegion = "";

    if (ianaTimeZone) {
      if (ianaTimeZone.startsWith("Europe/")) detectedRegion = "Europe";
      else if (
        ianaTimeZone.startsWith("Asia/") ||
        ianaTimeZone.startsWith("Australia/")
      )
        detectedRegion = "Asia-Pacific";
      else if (ianaTimeZone.startsWith("Africa/")) detectedRegion = "Africa";
      else if (ianaTimeZone.startsWith("America/")) {
        const saCities = [
          "Sao_Paulo",
          "Buenos_Aires",
          "Santiago",
          "Lima",
          "Bogota",
        ];
        if (saCities.some((city) => ianaTimeZone.includes(city))) {
          detectedRegion = "South America";
        } else {
          const offsetHours = offsetMinutes / 60;
          if (offsetHours >= 4 && offsetHours <= 6) detectedRegion = "US-East";
          else if (offsetHours >= 7) detectedRegion = "US-West";
          else detectedRegion = "US-East";
        }
      } else if (
        ianaTimeZone.includes("Dubai") ||
        ianaTimeZone.includes("Riyadh") ||
        ianaTimeZone.includes("Jerusalem")
      )
        detectedRegion = "Middle East";
    }

    setFormData((prev) => ({
      ...prev,
      timeZone: prev.timeZone || detectedTimeZone,
      region: prev.region || detectedRegion,
    }));
  }, [isOpen]);

  // Reset state on close
  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(1);
      setFormData({
        organizationName: "",
        primaryEmail: "",
        phone: "",
        region: "",
        timeZone: "",
        industry: "",
        selectedEngines: [],
        transformationCreditsThreshold: 0,
        transformationCreditPrice: 0,
        creationCreditsThreshold: 0,
        creationCreditPrice: 0,
      });
    }
  }, [isOpen]);

  const steps: Step[] = [
    {
      id: 1,
      title: "Detail",
      status:
        currentStep === 1
          ? "in-progress"
          : currentStep > 1
            ? "completed"
            : "not-started",
    },
    {
      id: 2,
      title: "Engine Selection",
      status:
        currentStep === 2
          ? "in-progress"
          : currentStep > 2
            ? "completed"
            : "not-started",
    },
    {
      id: 3,
      title: "Review",
      status:
        currentStep === 3
          ? "in-progress"
          : currentStep > 3
            ? "completed"
            : "not-started",
    },
  ];

  const handleFieldChange = (field: string, value: string | File | null) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = (error) => reject(error);
    });
  };

  const handleNext = async () => {
    if (currentStep < 3) {
      setCurrentStep((prev) => prev + 1);
      return;
    }

    // console.log({ formData });

    // ---- Convert logo file to Base64 if exists ----
    let base64Logo: string | undefined = undefined;

    const input: CreateOrganisationInput = {
      owner_name: formData.organizationName,
      org_name: formData.organizationName,
      email: formData.primaryEmail,
      phone: formData.phone,
      industry: formData.industry,
      region: formData.region,
      timeZone: formData.timeZone,
      logo: base64Logo || null,
      selectedEngines: formData.selectedEngines,
      transformationCreditsThreshold: formData.transformationCreditsThreshold,
      transformationCreditPrice: formData.transformationCreditPrice,
      creationCreditsThreshold: formData.creationCreditsThreshold,
      creationCreditPrice: formData.creationCreditPrice,
    };

    // console.log(input);

    try {
      setCreateLoading(true);
      const toastId = toast.loading("Creating organization...");
      const result = await createOrganisation({
        email: input.email,
        org_name: input.org_name,
        owner_name: input.owner_name,
        phone: input.phone,
        industry: input.industry,
        region: input.region,
        timeZone: input.timeZone,
        logo: input.logo,
        selectedEngines: input.selectedEngines,
        transformationCreditsThreshold: input.transformationCreditsThreshold,
        transformationCreditPrice: input.transformationCreditPrice,
        creationCreditsThreshold: input.creationCreditsThreshold,
        creationCreditPrice: input.creationCreditPrice,
      });

      if (result?.success !== false) {
        toast.update(toastId, {
          render: result.message || "Organization created successfully!",
          type: "success",
          isLoading: false,
          autoClose: 3000,
        });
        await refetch?.();
        onClose();
      } else {
        toast.update(toastId, {
          render: result.message || "Failed to create organization.",
          type: "error",
          isLoading: false,
          autoClose: 4500,
        });
      }
    } catch (err: any) {
      toast.dismiss();
      toast.error(
        extractApiErrorMessage(err, "Failed to create organization."),
      );
    } finally {
      setCreateLoading(false);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const isStepValid = () => {
    if (currentStep === 1) {
      const isPhoneValid =
        !formData.phone ||
        isValidPhoneNumber(
          formData.phone.startsWith("+")
            ? formData.phone
            : `+${formData.phone}`,
        );
      return (
        formData.organizationName.trim() !== "" &&
        formData.primaryEmail.trim() !== "" &&
        validateEmail(formData.primaryEmail) &&
        formData.region !== "" &&
        formData.timeZone !== "" &&
        isPhoneValid
      );
    }

    if (currentStep === 2) {
      // If engines are selected, validate their configuration
      if (formData.selectedEngines && formData.selectedEngines.length > 0) {
        const isTransformationSelected =
          formData.selectedEngines.includes("transformation");
        const isCreationSelected =
          formData.selectedEngines.includes("creation");

        if (isTransformationSelected) {
          if (
            !formData.transformationCreditsThreshold ||
            formData.transformationCreditsThreshold < 200 ||
            formData.transformationCreditsThreshold > 100000 ||
            !formData.transformationCreditPrice ||
            formData.transformationCreditPrice < 1
          ) {
            return false;
          }
        }

        if (isCreationSelected) {
          if (
            !formData.creationCreditsThreshold ||
            formData.creationCreditsThreshold < 200 ||
            formData.creationCreditsThreshold > 100000 ||
            !formData.creationCreditPrice ||
            formData.creationCreditPrice < 1
          ) {
            return false;
          }
        }
      }
      return true;
    }

    return true;
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <DetailStep formData={formData} onChange={handleFieldChange} />;
      case 2:
        return (
          <EngineSelectionStep
            formData={formData}
            onChange={handleFieldChange}
          />
        );
      case 3:
        return <ReviewStep formData={formData} />;
      default:
        return null;
    }
  };

  return (
    <SlideUpModal isOpen={isOpen} onClose={onClose}>
      <div className="flex flex-col h-full min-h-0">
        {/* Cross icon at top on small screens */}
        <div className="flex justify-end p-2 lg:hidden">
          <div className="rounded-md bg-white/70 backdrop-blur px-2">
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded-md bg-purple-25 text-gray-900 cursor-pointer"
              aria-label="Close modal"
            >
              <X className="h-6 w-6" />
            </button>
          </div>
        </div>

        {/* Main content area with sidebar and form */}
        <div className="flex flex-col lg:flex-row flex-1 min-h-0 overflow-y-auto lg:overflow-visible">
          {/* Left Sidebar - Step Indicator */}
          <div className="lg:w-80 lg:flex-shrink-0 p-4">
            <StepIndicator
              steps={steps}
              title="Create Organization"
              icon={<Building2 className="w-5 h-5 text-primary" />}
            />
          </div>

          {/* Right Content Area - Scrollable */}

          <div className="flex-1 min-h-0 flex flex-col">
            {/* small sticky header aligned to the right only (left remains as step indicator area) - hidden on small screens */}
            <div className="sticky top-0 z-20 bg-transparent hidden lg:block">
              <div className="flex justify-end px-6 py-3">
                <div className="rounded-md bg-white/70 backdrop-blur px-2 py-1">
                  <button
                    onClick={onClose}
                    className="w-8 h-8 flex items-center justify-center rounded-md bg-purple-25 text-gray-900 cursor-pointer"
                    aria-label="Close modal"
                  >
                    <X className="h-6 w-6" />
                  </button>
                </div>
              </div>
            </div>

            <div className="flex-1 lg:overflow-y-auto py-2 min-h-0">
              <div className="w-full pl-4 pr-8">{renderStepContent()}</div>
            </div>
          </div>
        </div>

        {/* Footer with Navigation Buttons - Full width border, spans entire bottom */}
        <div className="border-t border-gray-300 bg-white px-6 py-3 lg:px-12 flex-shrink-0">
          <div className="flex items-center justify-center gap-4 w-full">
            {/* Back Button */}
            {currentStep > 1 && (
              <Button
                type="button"
                color="purpleSubtle"
                onClick={handleBack}
                disabled={currentStep === 2 && createLoading}
                className="flex items-center gap-2 "
              >
                <ArrowLeft className="w-4 h-4 text-purple-300" />
                Back
              </Button>
            )}

            {/* Next/Submit Button */}
            {/* <Button
              type="button"
              color="purple"
              onClick={handleNext}
              disabled={!isStepValid()}
              className="flex items-center gap-2"
            >
              {currentStep === 3 ? "Create Organization" : "Next"}
              {currentStep < 3 && <ArrowRight className="w-4 h-4" />}
            </Button> */}

            <Button
              type="button"
              color="purple"
              onClick={handleNext}
              disabled={!isStepValid() || createLoading}
              className="flex items-center gap-2"
            >
              {createLoading
                ? "Creating..."
                : currentStep === 3
                  ? "Create Organization"
                  : "Next"}
              {currentStep < 3 && !createLoading && (
                <ArrowRight className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </SlideUpModal>
  );
}
