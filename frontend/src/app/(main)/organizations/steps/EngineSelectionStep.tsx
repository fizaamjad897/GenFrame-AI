"use client";

import { useState } from "react";
import { Check, AlertCircle } from "lucide-react";
import { Input } from "@/components/ui/input";
import { enginesData } from "@/utils/engineData";

interface EngineSelectionStepProps {
  formData: {
    selectedEngines: string[];
    transformationCreditsThreshold: number;
    transformationCreditPrice: number;
    creationCreditsThreshold: number;
    creationCreditPrice: number;
  };
  onChange: (field: string, value: any) => void;
}

export function EngineSelectionStep({
  formData,
  onChange,
}: EngineSelectionStepProps) {
  const isTransformationSelected =
    formData.selectedEngines?.includes("transformation");
  const isCreationSelected = formData.selectedEngines?.includes("creation");
  const isBothSelected = isTransformationSelected && isCreationSelected;

  const handleEngineSelect = (engineId: string) => {
    let newEngines: string[] = [];

    if (engineId === "both") {
      // Toggle both
      if (isBothSelected) {
        newEngines = [];
      } else {
        newEngines = ["transformation", "creation"];
        // Prefill values when selecting both
        onChange("transformationCreditsThreshold", 200);
        onChange("transformationCreditPrice", 1);
        onChange("creationCreditsThreshold", 200);
        onChange("creationCreditPrice", 1);
        return;
      }
    } else {
      // Toggle individual engine
      if (formData.selectedEngines?.includes(engineId)) {
        newEngines = formData.selectedEngines.filter((e) => e !== engineId);
      } else {
        newEngines = [...(formData.selectedEngines || []), engineId];
        // Prefill values when selecting an engine
        if (engineId === "transformation") {
          onChange("transformationCreditsThreshold", 200);
          onChange("transformationCreditPrice", 1);
        } else if (engineId === "creation") {
          onChange("creationCreditsThreshold", 200);
          onChange("creationCreditPrice", 1);
        }
      }
    }

    onChange("selectedEngines", newEngines);
  };

  const handleThresholdChange = (engine: string, value: string) => {
    if (value === "") {
      onChange(`${engine}CreditsThreshold`, undefined);
      return;
    }
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue)) {
      onChange(`${engine}CreditsThreshold`, numValue);
    }
  };

  const handlePriceChange = (engine: string, value: string) => {
    if (value === "") {
      onChange(`${engine}CreditPrice`, undefined);
      return;
    }
    const numValue = parseFloat(value);
    if (!isNaN(numValue)) {
      onChange(`${engine}CreditPrice`, numValue);
    }
  };

  const validateEngineConfig = () => {
    if (!formData.selectedEngines || formData.selectedEngines.length === 0) {
      return { valid: true };
    }

    const errors: { [key: string]: string } = {};

    if (isTransformationSelected) {
      if (
        formData.transformationCreditsThreshold < 200 ||
        formData.transformationCreditsThreshold > 100000
      ) {
        errors["transformationThreshold"] =
          "Threshold must be between 200 and 100,000 credits";
      }
      if (
        !formData.transformationCreditPrice ||
        formData.transformationCreditPrice < 1
      ) {
        errors["transformationPrice"] = "Minimum price is $1 per credit";
      }
    }

    if (isCreationSelected) {
      if (
        formData.creationCreditsThreshold < 200 ||
        formData.creationCreditsThreshold > 100000
      ) {
        errors["creationThreshold"] =
          "Threshold must be between 200 and 100,000 credits";
      }
      if (!formData.creationCreditPrice || formData.creationCreditPrice < 1) {
        errors["creationPrice"] = "Minimum price is $1 per credit";
      }
    }

    return {
      valid: Object.keys(errors).length === 0,
      errors,
    };
  };

  const validation = validateEngineConfig();

  return (
    <div className="space-y-8 pb-6">
      {/* Engine Selection Cards */}
      <div className="space-y-4">
        <label className="block text-sm font-medium text-gray-700">
          Select Engines
        </label>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Transformation Card */}
          <button
            type="button"
            onClick={() => handleEngineSelect("transformation")}
            className={`relative p-6 rounded-lg border-2 transition-all ${
              isTransformationSelected
                ? "border-purple-500 bg-purple-50"
                : "border-gray-200 bg-white hover:border-gray-300"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 text-left">
                <p className="font-semibold text-gray-900">
                  {enginesData[0].name}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  {enginesData[0].description}
                </p>
                <ul className="mt-3 space-y-1">
                  {enginesData[0].capabilities.map((cap) => (
                    <li
                      key={cap}
                      className="text-xs text-gray-700 flex items-center gap-2"
                    >
                      <span className="inline-block w-1 h-1 bg-purple-500 rounded-full" />
                      {cap}
                    </li>
                  ))}
                </ul>
              </div>
              {isTransformationSelected && (
                <div className="ml-4 flex-shrink-0">
                  <Check className="w-5 h-5 text-purple-500" />
                </div>
              )}
            </div>
          </button>

          {/* Creation Card */}
          <button
            type="button"
            onClick={() => handleEngineSelect("creation")}
            className={`relative p-6 rounded-lg border-2 transition-all ${
              isCreationSelected
                ? "border-purple-500 bg-purple-50"
                : "border-gray-200 bg-white hover:border-gray-300"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 text-left">
                <p className="font-semibold text-gray-900">
                  {enginesData[1].name}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  {enginesData[1].description}
                </p>
                <ul className="mt-3 space-y-1">
                  {enginesData[1].capabilities.map((cap) => (
                    <li
                      key={cap}
                      className="text-xs text-gray-700 flex items-center gap-2"
                    >
                      <span className="inline-block w-1 h-1 bg-purple-500 rounded-full" />
                      {cap}
                    </li>
                  ))}
                </ul>
              </div>
              {isCreationSelected && (
                <div className="ml-4 flex-shrink-0">
                  <Check className="w-5 h-5 text-purple-500" />
                </div>
              )}
            </div>
          </button>
        </div>
      </div>

      {/* Configuration Section - Show only if engines selected */}
      {formData.selectedEngines && formData.selectedEngines.length > 0 && (
        <div className="space-y-6">
          {isTransformationSelected && (
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-900">
                Transformation Engine
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Credits
                  </label>
                  <Input
                    type="number"
                    value={formData.transformationCreditsThreshold || ""}
                    onChange={(e) =>
                      handleThresholdChange("transformation", e.target.value)
                    }
                    placeholder="e.g., 200"
                    min={200}
                    max={100000}
                    className={
                      validation.errors?.["transformationThreshold"]
                        ? "border-red-500 text-red-600 focus:border-red-500 focus:ring-red-500"
                        : ""
                    }
                  />
                  {validation.errors?.["transformationThreshold"] && (
                    <div className="flex items-center gap-1 mt-2 text-red-600 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      <span>
                        {validation.errors["transformationThreshold"]}
                      </span>
                    </div>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    $ per Credit
                  </label>
                  <Input
                    type="number"
                    step="0.05"
                    value={formData.transformationCreditPrice || ""}
                    onChange={(e) =>
                      handlePriceChange("transformation", e.target.value)
                    }
                    placeholder="e.g., 1"
                    className={
                      validation.errors?.["transformationPrice"]
                        ? "border-red-500"
                        : ""
                    }
                  />
                  {validation.errors?.["transformationPrice"] && (
                    <div className="flex items-center gap-1 mt-2 text-red-600 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      <span>{validation.errors["transformationPrice"]}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {isCreationSelected && (
            <div className="space-y-4">
              <h4 className="text-sm font-medium text-gray-900">
                Creation Engine
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Credits
                  </label>
                  <Input
                    type="number"
                    value={formData.creationCreditsThreshold || ""}
                    onChange={(e) =>
                      handleThresholdChange("creation", e.target.value)
                    }
                    placeholder="e.g., 200"
                    min={200}
                    max={100000}
                    className={
                      validation.errors?.["creationThreshold"]
                        ? "border-red-500 text-red-600 focus:border-red-500 focus:ring-red-500"
                        : ""
                    }
                  />
                  {validation.errors?.["creationThreshold"] && (
                    <div className="flex items-center gap-1 mt-2 text-red-600 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      <span>{validation.errors["creationThreshold"]}</span>
                    </div>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    $ per Credit
                  </label>
                  <Input
                    type="number"
                    step="0.05"
                    value={formData.creationCreditPrice || ""}
                    onChange={(e) =>
                      handlePriceChange("creation", e.target.value)
                    }
                    placeholder="e.g., 1"
                    className={
                      validation.errors?.["creationPrice"]
                        ? "border-red-500"
                        : ""
                    }
                  />
                  {validation.errors?.["creationPrice"] && (
                    <div className="flex items-center gap-1 mt-2 text-red-600 text-sm">
                      <AlertCircle className="w-4 h-4" />
                      <span>{validation.errors["creationPrice"]}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
