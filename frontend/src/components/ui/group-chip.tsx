"use client";

import React from "react";
import clsx from "clsx";

interface GroupChipProps {
  label: string;
  className?: string;
}

export function GroupChip({ label, className }: GroupChipProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center px-2 py-0.5 rounded-full text-sm font-medium",
        "bg-purple-25 text-purple-400",
        className
      )}
    >
      {label}
    </span>
  );
}

export default GroupChip;
