import React, { useId } from "react";
import { ACCENT } from "./terminal";

/** The one brand mark — a focus-frame reticle on a rounded-square accent
 * field. Shared by every surface so the logo never drifts. */
export default function GridMark({ size = 28 }: { size?: number }) {
  const gradientId = `gridmark-fill-${useId()}`;
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" style={{ flexShrink: 0 }}>
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="32" y2="32">
          <stop offset="0%" stopColor="#A78BFA" />
          <stop offset="100%" stopColor={ACCENT} />
        </linearGradient>
      </defs>
      <rect width="32" height="32" rx="9" fill={`url(#${gradientId})`} />
      <circle cx="16" cy="16" r="7.5" fill="none" stroke="#FFFFFF" strokeWidth="2" />
      <path d="M16 8v5M16 19v5M8 16h5M19 16h5" stroke="#FFFFFF" strokeWidth="2" strokeLinecap="round" />
      <circle cx="16" cy="16" r="2" fill="#FFFFFF" />
    </svg>
  );
}
