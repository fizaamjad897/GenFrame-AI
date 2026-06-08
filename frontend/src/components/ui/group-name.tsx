"use client";

import React from "react";
import { clsx } from "clsx";

interface GroupNameProps {
  name: string;
  createdBy?: string;
  className?: string;
}

export function GroupName({ name, createdBy, className }: GroupNameProps) {
  return (
    <div className={clsx("flex flex-col", className)}>
      <div className="text-subhead text-gray-900 font-regular">{name}</div>
      {createdBy && (
        <div className="text-body font-medium text-gray-500 mt-1">By {createdBy}</div>
      )}
    </div>
  );
}

export default GroupName;
