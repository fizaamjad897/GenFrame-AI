"use client";

import { useState, useEffect } from "react";
import { Building2, ArrowRight, ArrowLeft, X } from "lucide-react";
import { SlideUpModal } from "@/components/ui/slide-up-modal";
import { StepIndicator, Step } from "@/components/ui/step-indicator";
import { Button } from "@/components/ui/button";
import { DetailStep } from "./steps/DetailStep";
import { ReviewStep } from "./steps/ReviewStep";
// Mocked GraphQL imports removed as requested.
import { toast } from "react-toastify";
import { isValidPhoneNumber } from "libphonenumber-js";
import { updateOrganisationWithUser } from "@/lib/organisationApi";
import { extractApiErrorMessage } from "@/lib/errorMessage";

interface UpdateOrganizationModalProps {
  isOpen: boolean;
  onClose: () => void;
  refetch?: () => void;
  selectedOrg?: any;
}

export function UpdateOrganizationModal({
  isOpen,
  onClose,
  refetch,
  selectedOrg,
}: UpdateOrganizationModalProps) {
  const [updateLoading, setUpdateLoading] = useState(false);

  // console.log({ selectedOrg });
  const [currentStep, setCurrentStep] = useState(1);

  const initialForm = {
    organizationName: "",
    primaryEmail: "",
    phone: "",
    region: "",
    timeZone: "",
    maxMembers: 0,
    industry: "",
    logo: null as File | string | null,
    plan: "",
    licenses: 0,
    selectedEngines: [] as string[],
    transformationCreditsThreshold: 0,
    transformationCreditPrice: 0,
    creationCreditsThreshold: 0,
    creationCreditPrice: 0,
  };

  const [formData, setFormData] = useState(initialForm);

  // Step definitions
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
      title: "Review",
      status:
        currentStep === 2
          ? "in-progress"
          : currentStep > 2
            ? "completed"
            : "not-started",
    },
  ];

  // Handlers
  const handleFieldChange = (field: string, value: string | File | null) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
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
    if (currentStep < 2) {
      setCurrentStep(2);
      return;
    }

    let logoValue: string | null = null;

    if (formData.logo instanceof File) {
      // New file uploaded - convert to base64
      logoValue = await fileToBase64(formData.logo);
    } else if (typeof formData.logo === "string" && formData.logo) {
      // Existing logo URL - preserve it
      logoValue = formData.logo;
    }

    try {
      setUpdateLoading(true);
      const toastId = toast.loading("Updating organization...");

      // Update organization and user using unified endpoint
      await updateOrganisationWithUser({
        orgId: selectedOrg.id,
        org_name: formData.organizationName,
        logo: logoValue,
        industry: formData.industry || undefined,
        region: formData.region || undefined,
        timeZone: formData.timeZone || undefined,
        username: formData.organizationName,
        phone: formData.phone || undefined,
        country: formData.region || undefined,
      });

      toast.update(toastId, {
        render: "Organization updated successfully!",
        type: "success",
        isLoading: false,
        autoClose: 3000,
      });
      if (refetch) {
        refetch();
      }
      handleCloseReset();
    } catch (error: any) {
      toast.dismiss();
      toast.error(extractApiErrorMessage(error, "Failed to update organization"));
      console.error(error);
    } finally {
      setUpdateLoading(false);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) setCurrentStep(1);
  };

  const handleCloseReset = () => {
    setCurrentStep(1);
    setFormData(initialForm);
    onClose();
  };

  const validateEmail = (email: string) =>
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const isStepValid = () => {
    if (currentStep === 1) {
      return (
        formData.organizationName.trim() !== "" &&
        formData.primaryEmail.trim() !== "" &&
        validateEmail(formData.primaryEmail) &&
        formData.region !== "" &&
        formData.timeZone !== "" &&
        (!formData.phone ||
          isValidPhoneNumber(
            formData.phone.startsWith("+")
              ? formData.phone
              : `+${formData.phone}`,
          ))
      );
    }
    return true;
  };

  // --- Render Step Content ---
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <DetailStep
            formData={formData}
            onChange={handleFieldChange}
            isEdit={true}
          />
        );
      case 2:
        return <ReviewStep formData={formData} update={true} />;
      default:
        return null;
    }
  };

  // console.log({ selectedOrg });
  // --- Populate form when selectedOrg changes ---
  useEffect(() => {
    if (selectedOrg) {
      setFormData({
        organizationName: selectedOrg.name || "",
        primaryEmail: selectedOrg.users?.[0]?.email || "",
        phone: selectedOrg?.users?.[0]?.phone || "",
        region: selectedOrg.region || "",
        timeZone: selectedOrg.time_zone || "",
        maxMembers: selectedOrg.max_members ?? 0,
        industry: selectedOrg.industry || "",
        logo: selectedOrg.logo || null,
        plan: selectedOrg.org_typeid || "",
        licenses: selectedOrg.setup_members ?? 0,
        selectedEngines: selectedOrg.selectedEngines || [],
        transformationCreditsThreshold:
          selectedOrg.transformationCreditsThreshold || 0,
        transformationCreditPrice: selectedOrg.transformationCreditPrice || 0,
        creationCreditsThreshold: selectedOrg.creationCreditsThreshold || 0,
        creationCreditPrice: selectedOrg.creationCreditPrice || 0,
      });
    }
  }, [selectedOrg]);

  // --- Reset on modal close (if user closes manually) ---
  useEffect(() => {
    if (!isOpen) {
      setTimeout(() => {
        setCurrentStep(1);
        setFormData(initialForm);
      }, 300); // small delay to not flicker during animation
    }
  }, [isOpen]);

  return (
    <SlideUpModal isOpen={isOpen} onClose={handleCloseReset}>
      <div className="flex flex-col h-full min-h-0">
        {/* Header Close (mobile) */}
        <div className="flex justify-end p-2 lg:hidden">
          <button
            onClick={handleCloseReset}
            className="w-8 h-8 flex items-center justify-center rounded-md bg-purple-25 text-gray-900"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Main content */}
        <div className="flex flex-col lg:flex-row flex-1 min-h-0 overflow-y-auto lg:overflow-visible">
          {/* Sidebar steps */}
          <div className="lg:w-80 lg:flex-shrink-0 p-4">
            <StepIndicator
              steps={steps}
              title="Edit Organization"
              icon={<Building2 className="w-5 h-5 text-primary" />}
            />
          </div>

          {/* Form */}
          <div className="flex-1 min-h-0 flex flex-col">
            {/* Top-right close (desktop) */}
            <div className="sticky top-0 z-20 bg-transparent hidden lg:block">
              <div className="flex justify-end px-6 py-3">
                <button
                  onClick={handleCloseReset}
                  className="w-8 h-8 flex items-center justify-center rounded-md bg-purple-25 text-gray-900 cursor-pointer"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>

            <div className="flex-1 lg:overflow-y-auto py-2 min-h-0">
              <div className="w-full pl-4 pr-8">{renderStepContent()}</div>
            </div>
          </div>
        </div>

        {/* Footer buttons */}
        <div className="border-t border-gray-300 bg-white px-6 py-3 lg:px-12 flex-shrink-0">
          <div className="flex items-center justify-center gap-4 w-full">
            {currentStep > 1 && (
              <Button
                type="button"
                color="purpleSubtle"
                onClick={handleBack}
                className="flex items-center gap-2"
              >
                <ArrowLeft className="w-4 h-4 text-purple-300" />
                Back
              </Button>
            )}

            <Button
              type="button"
              color="purple"
              onClick={handleNext}
              disabled={!isStepValid() || updateLoading}
              className="flex items-center gap-2"
            >
              {updateLoading
                ? "Saving..."
                : currentStep === 1
                  ? "Review & Continue"
                  : "Update Organization"}
              {!updateLoading && currentStep === 1 && (
                <ArrowRight className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </SlideUpModal>
  );
}
