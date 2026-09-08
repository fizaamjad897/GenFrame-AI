/**
 * SignageX theme — the shared visual system for Recreative AI, re-themed to
 * match SignageX (D:\SignageX\signageX-frontend): white surfaces, a violet
 * primary accent, rounded-lg/xl cards with soft shadows, Inter throughout.
 *
 * Import from here instead of redeclaring hex values so every surface that
 * adopts this system stays in sync by construction.
 */

export const CREAM = "#FFFFFF";
export const CREAM_DEEP = "#F9FAFB";
export const INK = "#111827";
export const PANEL = "#111827";
export const PANEL_LINE = "#374151";
export const TEXT_MUTED_L = "#6B7280";
export const TEXT_MUTED_D = "#9CA3AF";
export const BORDER_L = "#E5E7EB";
export const BORDER_D = "#374151";
export const ACCENT = "#8B5CF6";
export const ACCENT_SOFT = "#8B5CF61c";
export const GOOD = "#10B981";
export const BAD = "#EF4444";

export const DISPLAY = "var(--font-inter), system-ui, sans-serif";
export const BODY = "var(--font-inter), system-ui, sans-serif";
export const MONO = "var(--font-inter), system-ui, sans-serif";

export const RADIUS_SM = "10px";
export const RADIUS_MD = "18px";
export const RADIUS_LG = "26px";
export const SHADOW_SM = "0 1px 2px 0 rgb(0 0 0 / 0.05)";
export const SHADOW_MD = "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)";
export const SHADOW_LG = "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)";

export const ease: [number, number, number, number] = [0.16, 1, 0.3, 1];
