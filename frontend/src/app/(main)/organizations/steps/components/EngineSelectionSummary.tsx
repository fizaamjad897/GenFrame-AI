"use client";

interface EngineSelectionSummaryProps {
  selectedEngines?: string[];
  transformationCreditsThreshold?: number;
  transformationCreditPrice?: number;
  creationCreditsThreshold?: number;
  creationCreditPrice?: number;
}

export function EngineSelectionSummary({
  selectedEngines = [],
  transformationCreditsThreshold,
  transformationCreditPrice,
  creationCreditsThreshold,
  creationCreditPrice,
}: EngineSelectionSummaryProps) {
  if (!selectedEngines || selectedEngines.length === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-3xl mt-6">
      <div className="rounded-md border-2 border-gray-100 bg-white">
        <div className="bg-gray-50 px-6 py-3 rounded-t-md border-b border-gray-100 h-12">
          <h4 className="text-title font-semibold text-gray-900">
            Engine Configuration
          </h4>
        </div>

        <div className="p-4 space-y-8">
          {selectedEngines.includes("transformation") && (
            <div className="pb-6 border-b border-gray-200">
              <h5 className="text-sm font-semibold text-gray-900 mb-4">
                Transformation Engine
              </h5>
              <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-x-32 gap-y-2 font-medium text-subhead text-gray-700">
                <div>Minimum Credits:</div>
                <div className="text-gray-900 font-regular">
                  {transformationCreditsThreshold || "-"}
                </div>

                <div>Price per Credit:</div>
                <div className="text-gray-900 font-regular">
                  ${transformationCreditPrice?.toFixed(2) || "-"}
                </div>
              </div>
            </div>
          )}

          {selectedEngines.includes("creation") && (
            <div className="pt-2">
              <h5 className="text-sm font-semibold text-gray-900 mb-4">
                Creation Engine
              </h5>
              <div className="grid grid-cols-1 md:grid-cols-[auto_1fr] gap-x-32 gap-y-2 font-medium text-subhead text-gray-700">
                <div>Minimum Credits:</div>
                <div className="text-gray-900 font-regular">
                  {creationCreditsThreshold || "-"}
                </div>

                <div>Price per Credit:</div>
                <div className="text-gray-900 font-regular">
                  ${creationCreditPrice?.toFixed(2) || "-"}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
