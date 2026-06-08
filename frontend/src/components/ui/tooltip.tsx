"use client";

import React, { ReactNode } from "react";
import clsx from "clsx";

type Placement =
  | "top"
  | "bottom"
  | "left"
  | "right"
  | "top-left"
  | "top-right"
  | "bottom-left"
  | "bottom-right";

interface TooltipProps {
  content: ReactNode;
  children: ReactNode;
  className?: string;
  tooltipClassName?: string;
  placement?: Placement;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  className,
  tooltipClassName,
  placement = "top",
}) => {
  const placementClasses: Record<Placement, string> = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",

    // Speech bubble placements
    "top-left": "bottom-full left-0 mb-2",
    "top-right": "bottom-full right-0 mb-2",
    "bottom-left": "top-full left-0 mt-2",
    "bottom-right": "top-full right-0 mt-2",
  };

  const arrowClasses: Partial<Record<Placement, string>> = {
    "top-left":
      "top-full left-3 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-900",
    "top-right":
      "top-full right-3 border-l-4 border-r-4 border-t-4 border-l-transparent border-r-transparent border-t-gray-900",

    "bottom-left":
      "bottom-full left-3 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent border-b-gray-900",
    "bottom-right":
      "bottom-full right-3 border-l-4 border-r-4 border-b-4 border-l-transparent border-r-transparent border-b-gray-900",
  };

  const showArrow = placement in arrowClasses;

  return (
    <div className={clsx("relative inline-flex group", className)}>
      {children}

      <div
        className={clsx(
          "absolute z-999 hidden group-hover:block rounded-md bg-gray-900 px-3 py-1.5 text-xs text-white shadow-lg",
          "w-max max-w-xs whitespace-normal break-words",
          placementClasses[placement],
          tooltipClassName
        )}
      >
        {content}

        {showArrow && (
          <span className={clsx("absolute h-0 w-0", arrowClasses[placement])} />
        )}
      </div>
    </div>
  );
};
