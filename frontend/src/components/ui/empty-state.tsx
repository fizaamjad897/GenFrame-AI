"use client";

import React from "react";
import { clsx } from "clsx";
import { Button } from "./button";

interface EmptyStateProps {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
  illustration?: React.ReactNode;
  className?: string;
  buttonClassName?: string;
}

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
  illustration,
  className,
  buttonClassName,
}: EmptyStateProps) {
  return (
    <div
      className={clsx(
        "flex flex-col items-center justify-center text-center rounded-lg h-full",
        className
      )}
    >
      {/* Illustration */}
      {illustration && <div className="mb-8">{illustration}</div>}

      <div className="max-w-md">
        <h1 className="text-heading-h1 font-semibold text-gray-900 mb-2">
          {title}
        </h1>
        <p className="text-base text-[#3F3F3F] mb-8">{description}</p>

        {/* Action Button */}
        {actionLabel && onAction && (
          <Button
            onClick={onAction}
            className={clsx(
              "min-w-btn-base h-btn-base px-btn-base-px py-btn-base-py",
              buttonClassName ||
              (actionLabel === "Add Trigger" ? "w-52" : undefined)
            )}
            color="purple"
          >
            {actionLabel}
          </Button>
        )}
      </div>
    </div>
  );
}

export function NoOrganizationsIllustration({
  className,
}: {
  className?: string;
}) {
  return (
    <div
      className={clsx(
        "w-40 h-40 flex items-center justify-center",
        className
      )}
    >
      <img src="/asking-question-2.svg" alt="Illustration" />
    </div>
  );
}
