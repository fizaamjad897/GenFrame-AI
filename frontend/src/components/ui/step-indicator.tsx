"use client";

import { Building2, Check } from "lucide-react";
import clsx from "clsx";

export type StepStatus = "not-started" | "in-progress" | "completed";

export interface Step {
  id: number;
  title: string;
  status: StepStatus;
}

interface StepIndicatorProps {
  steps: Step[];
  title: string;
  icon?: React.ReactNode;
}

export function StepIndicator({ steps, title, icon }: StepIndicatorProps) {
  return (
    <div
      className="w-full h-full px-2 py-4 lg:px-4 lg:py-8 flex flex-col rounded-lg "
      style={{
        background: "linear-gradient(192.32deg, #F3EFFE 1.56%, #DDD0FF 98.63%)",
      }}
    >
      {/* Header with icon and title */}
      <div className="flex items-center gap-1 mb-6 lg:mb-12">
        <div className="flex items-center justify-center w-10 h-10">
          {icon || <Building2 className="w-5 h-5 text-primary" />}
        </div>
        <h2 className="text-heading-h2 font-semibold text-gray-900">{title}</h2>
      </div>

      {/* Steps */}
      <div className="flex flex-col gap-0 px-1 lg:px-2.5">
        {steps.map((step, index) => {
          const isLast = index === steps.length - 1;
          const isCompleted = step.status === "completed";
          const isInProgress = step.status === "in-progress";
          const isNotStarted = step.status === "not-started";

          return (
            <div key={step.id} className="flex items-start gap-2 lg:gap-4">
              {/* Circle and connector line */}
              <div className="flex flex-col items-center">
                {/* Circle */}
                <div
                  className={clsx(
                    "flex items-center justify-center rounded-full transition-all",
                    "w-8 h-8 shrink-0",
                    {
                      // Completed state: filled with primary color, white tick
                      "bg-primary": isCompleted,
                      // In-progress state: white with primary border and small inner circle
                      "bg-white border-2 border-primary": isInProgress,
                      // Not started: gray border
                      "bg-white border-2 border-gray-300": isNotStarted,
                    }
                  )}
                >
                  {isCompleted ? (
                    <Check className="w-5 h-5 text-white" />
                  ) : isInProgress ? (
                    <div className="w-2.5 h-2.5 rounded-full bg-primary" />
                  ) : null}
                </div>

                {/* Connecting line */}
                {!isLast && (
                  <div
                    className={clsx("w-0.5 my-1 transition-all", {
                      // Line is darker if current step is completed
                      "bg-primary h-6 lg:h-8": isCompleted,
                      "bg-gray-300 h-6 lg:h-8": !isCompleted,
                    })}
                  />
                )}
              </div>

              {/* Step title */}
              <div className="pb-4 lg:pb-6">
                <p
                  className={clsx("text-xs font-regular", {
                    "text-gray-900": isCompleted,
                    "text-primary": isInProgress,
                    "text-gray-500": isNotStarted,
                  })}
                >
                  STEP {step.id}
                
                </p>
                <p className="text-subhead font-semibold text-gray-900" >
                     {step.title}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
