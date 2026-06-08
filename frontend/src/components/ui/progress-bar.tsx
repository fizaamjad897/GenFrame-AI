"use client";

import React from "react";
import { clsx } from "clsx";

interface ProgressBarProps {
  current: number;
  total: number;
  showNumbers?: boolean;
  textAlign?: "left" | "right";
  className?: string;
  barClassName?: string;
  trackClassName?: string;
  textClassName?: string;
}

export function ProgressBar({
  current,
  total,
  showNumbers = true,
  textAlign = "right",
  className,
  barClassName,
  trackClassName,
  textClassName,
}: ProgressBarProps) {
  const percentage = total > 0 ? Math.round((current / total) * 100) : 0;

  return (
    <div className={clsx("flex flex-col gap-1", className)}>
      {showNumbers && (
        <div
          className={clsx(
            "text-body text-gray-900 font-medium",
            textAlign === "left" ? "text-left" : "text-right",
            textClassName,
          )}
        >
          {current}/{total}
        </div>
      )}
      <div
        className={clsx(
          "h-2 rounded-full overflow-hidden",
          trackClassName ?? "bg-gray-100",
        )}
      >
        <div
          className={clsx(
            "h-2 bg-gray-700 rounded-full transition-all duration-300",
            barClassName,
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default ProgressBar;
