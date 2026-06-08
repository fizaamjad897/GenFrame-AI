"use client";

import { useState, useEffect } from "react";
import {
  Building2,
  ArrowRight,
  ArrowLeft,
  X,
  User,
  UserPlus,
} from "lucide-react";
import { SlideUpModal } from "@/components/ui/slide-up-modal";
import { StepIndicator, Step } from "@/components/ui/step-indicator";
import { Button } from "@/components/ui/button";

// Mock api removed
import { toast } from "react-toastify";
import { isValidPhoneNumber } from "libphonenumber-js";
import { DetailStep } from "./steps/DetailStep";
import PermissionStep from "./steps/PermissionStep";
import { ReviewStep } from "./steps/ReviewStep";
import { createUser, updateUser } from "@/lib/organisationApi";
import { extractApiErrorMessage } from "@/lib/errorMessage";

interface UserRow {
  id: string;
  name: string;
  email: string;
  avatar?: string | null;
  organization: string;
  orgId?: string;
  role: "Admin" | "Manager" | "User";
  status: "Active" | "Trial" | "Inactive" | "Offline";
  lastActive: string;
  permissions?: string[];
}
interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  refetch?: any;
  initialData?: UserRow | null;
  onSuccess?: () => void;
}

export function CreateUserModal({
  isOpen,
  onClose,
  initialData,
  refetch,
  onSuccess,
}: CreateUserModalProps) {
  const [createLoading, setCreateLoading] = useState(false);
  const [updateLoading, setUpdateLoading] = useState(false);

  const [currentStep, setCurrentStep] = useState(1);
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([]);

  const [formData, setFormData] = useState({
    ownerName: "",
    primaryEmail: "",
    password: "",
    role: "",
    phone: "",
  });

  useEffect(() => {
    if (!isOpen) {
      setCurrentStep(1);
      setFormData({
        ownerName: "",
        primaryEmail: "",
        password: "",
        phone: "",
        role: "",
      });
      setSelectedPermissions([]);
      return;
    }

    if (initialData) {
      setFormData({
        ownerName: initialData.name,
        primaryEmail: initialData.email,
        password: "",
        phone: "",
        role:
          initialData.role === "Admin" || initialData.role === "Manager"
            ? "admin"
            : "restricted_user",
      });
      if (initialData.permissions) {
        setSelectedPermissions(initialData.permissions);
      }
    }
  }, [isOpen, initialData]);

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
      title: "Permissions",
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

    try {
      toast.loading(initialData ? "Updating user..." : "Creating user...");
      const roleName = formData.role === "admin" ? "admin" : "restrictedUser";

      if (initialData?.id) {
        setUpdateLoading(true);
        const result = await updateUser({
          userId: initialData.id,
          username: formData.ownerName,
          email: formData.primaryEmail,
          phone: formData.phone,
          roleName,
          rightsNames: selectedPermissions,
          is_active: formData.role ? true : undefined,
        });
        toast.dismiss();
        toast.success(result.message || "User updated successfully");
      } else {
        setCreateLoading(true);
        const result = await createUser({
          username: formData.ownerName,
          email: formData.primaryEmail,
          password: formData.password,
          roleName,
          rightsNames: selectedPermissions,
        });
        toast.dismiss();
        toast.success(result.message || "User created successfully");
      }

      await refetch?.();
      onSuccess?.();
      onClose();
    } catch (error: any) {
      toast.dismiss();
      toast.error(extractApiErrorMessage(error, "Failed to process user operation"));
    } finally {
      setCreateLoading(false);
      setUpdateLoading(false);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
    }
  };

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
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
      const isPasswordValid = initialData
        ? true
        : formData.password.trim() !== "";
      return (
        formData.ownerName.trim() !== "" &&
        formData.primaryEmail.trim() !== "" &&
        validateEmail(formData.primaryEmail) &&
        formData.role.trim() !== "" &&
        isPasswordValid &&
        isPhoneValid
      );
    }
    return true;
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <DetailStep
            formData={formData}
            onChange={handleFieldChange}
            isEdit={!!initialData}
          />
        );
      case 2:
        return (
          <PermissionStep
            role={formData.role}
            onChange={setSelectedPermissions}
            selectedPermissions={selectedPermissions}
          />
        );
      case 3:
        return (
          <ReviewStep
            formData={formData}
            selectedPermissions={selectedPermissions}
          />
        );
      default:
        return null;
    }
  };

  return (
    <SlideUpModal isOpen={isOpen} onClose={onClose}>
      <div className="flex flex-col h-full min-h-0">
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

        <div className="flex flex-col lg:flex-row flex-1 min-h-0 overflow-y-auto lg:overflow-visible">
          <div className="lg:w-80 lg:flex-shrink-0 p-4">
            <StepIndicator
              steps={steps}
              title={initialData ? "Edit User" : "Create User"}
              icon={<UserPlus className="w-5 h-5 text-primary" />}
            />
          </div>

          <div className="flex-1 min-h-0 flex flex-col">
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

        <div className="border-t border-gray-300 bg-white px-6 py-3 lg:px-12 flex-shrink-0">
          <div className="flex items-center justify-center gap-4 w-full">
            {currentStep > 1 && (
              <Button
                type="button"
                color="purpleSubtle"
                onClick={handleBack}
                className="flex items-center gap-2 "
              >
                <ArrowLeft className="w-4 h-4 text-purple-300" />
                Back
              </Button>
            )}

            <Button
              type="button"
              color="purple"
              onClick={handleNext}
              disabled={!isStepValid() || createLoading || updateLoading}
              className="flex items-center gap-2"
            >
              {createLoading || updateLoading
                ? initialData
                  ? "Updating..."
                  : "Creating..."
                : currentStep === 3
                  ? initialData
                    ? "Update"
                    : "Create"
                  : initialData
                    ? "Review & Continue"
                    : "Next"}

              {currentStep < 3 && !createLoading && !updateLoading && (
                <ArrowRight className="w-4 h-4" />
              )}
            </Button>
          </div>
        </div>
      </div>
    </SlideUpModal>
  );
}
