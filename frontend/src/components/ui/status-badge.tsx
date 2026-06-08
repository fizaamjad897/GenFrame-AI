"use client";

import React from "react";
import { clsx } from "clsx";

interface StatusBadgeProps {
  status: "Active" | "Trial" | "Inactive" | string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <div className="flex justify-center">
      <span
        className={clsx(
          "inline-flex items-center px-2.5 py-0.5 rounded-full text-body font-medium",
          status === "Active"
            ? "bg-green-50 text-green-800"
            : status === "Trial"
            ? "bg-yellow-50 text-warning-500"
            : "bg-gray-50 text-gray-500",
          className
        )}
      >
        <div
          className={clsx(
            "w-1.5 h-1.5 rounded-full mr-1.5",
            status === "Active"
              ? "bg-success-500"
              : status === "Trial"
              ? "bg-warning-500"
              : "bg-gray-500"
          )}
        />
        {status}
      </span>
    </div>
  );
}

export default StatusBadge;