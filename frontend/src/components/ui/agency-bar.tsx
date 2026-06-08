"use client";

import React from "react";
import clsx from "clsx";
import { UserAvatar } from "./user-avatar";
import { StatusBadge } from "./status-badge";
interface AgencyBarProps {
  name: string;
  email: string;
  status?: "Active" | "Inactive" | "Trial";
  creditsUsed?: number;
  creditsTotal?: number;
  usersActive?: number;
  usersTotal?: number;
  billingDate?: string;
  avatarSrc?: string;
  className?: string;
}

export function AgencyBar({
  name,
  email,
  status = "Active",
  creditsUsed = 0,
  creditsTotal = 0,
  usersActive = 0,
  usersTotal = 0,
  billingDate = "—",
  avatarSrc,
  className,
}: AgencyBarProps) {
  return (
    <div
      className={clsx(
        "bg-purple-25 p-3 rounded-lg w-full overflow-hidden",
        className,
      )}
    >
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex-shrink-0 w-full lg:w-auto ml-1">
          <UserAvatar name={name} email={email} avatar={avatarSrc} size="md" />
        </div>

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 xl:ml-auto ml-1">
          {/* Status */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="font-medium text-gray-500 text-sm">Status</span>
            <StatusBadge status={status} />
          </div>

          <div className="hidden sm:block h-6 w-px bg-gray-300 flex-shrink-0" />

          {/* Credits Used */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="font-medium text-gray-500 text-sm">
              Credits Used:
            </span>
            <span className="font-medium text-gray-800 text-sm">
              {creditsUsed}
            </span>
          </div>

          <div className="hidden sm:block h-6 w-px bg-gray-300 flex-shrink-0" />

          {/* <div className="hidden sm:block h-6 w-px bg-gray-300 flex-shrink-0" /> */}

          {/* Billing Date */}
          <div className="flex items-center gap-2 flex-shrink-0">
            <span className="font-medium text-gray-500 text-sm whitespace-nowrap">
              Billing Date:
            </span>
            <span className="font-semibold text-gray-800 text-sm whitespace-nowrap">
              {billingDate}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AgencyBar;
