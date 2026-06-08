"use client";

import React from "react";
import { clsx } from "clsx";

interface UserAvatarProps {
  name: string;
  email?: string;
  avatar?: string | null;
  size?: "sm" | "md" | "lg";
  className?: string;
  showEmail?: boolean;
}

export function UserAvatar({
  name,
  email,
  avatar,
  size = "md",
  className,
  showEmail = true,
}: UserAvatarProps) {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-10 h-10",
    lg: "w-12 h-12",
  };

  const textSizeClasses = {
    sm: "text-xs",
    md: "text-sm",
    lg: "text-base",
  };

  return (
    <div className={clsx("flex items-center gap-3", className)}>
      <div
        className={clsx(
          "rounded-lg flex items-center justify-center flex-shrink-0",
          sizeClasses[size]
        )}
      >
        {avatar ? (
          <img
            src={avatar}
            alt={name}
            className={clsx("rounded-full object-cover", sizeClasses[size])}
          />
        ) : (
          <div className="w-full h-full rounded-full bg-gradient-to-br from-purple-400 to-purple-600 flex items-center justify-center">
            <span
              className={clsx(
                "text-white font-semibold",
                textSizeClasses[size]
              )}
            >
              {name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
      </div>
      <div className="min-w-0 flex-1">
        <div
          className={clsx(
            "text-subhead font-medium text-gray-900 truncate",
            textSizeClasses[size]
          )}
        >
          {name}
        </div>
        {showEmail && email && (
          <div
            className={clsx(
              "text-subhead text-gray-500 truncate",
              textSizeClasses[size]
            )}
          >
            {email}
          </div>
        )}
      </div>
    </div>
  );
}

export default UserAvatar;
