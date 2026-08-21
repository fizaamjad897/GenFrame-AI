export interface EngineCredits {
  monthly_units_used?: number;
  monthly_units_max?: number;
  addon_units_used?: number;
  addon_units_max?: number;
  remaining_units?: number;
}

export interface User {
  id: string;
  email: string;
  fullName?: string | null;
  plan: string;
  engineType?: string | null;
  units: number;
  maxUnits: number;
  remainingUnits?: number | null;
  credits?: Record<string, EngineCredits> | null;
  engine_data?: Record<string, { credits?: EngineCredits }> | null;
  available_engines?: string[] | null;
  is_postpaid?: boolean;
  createdAt: string;
  org_context?: Record<string, unknown> | null;
}

export type EngineType = 'creation' | 'transformation';

export interface AspectRatioPreset {
  key: string;
  label: string;
  ratio: string; // e.g. "1:1"
}

export const ASPECT_RATIO_PRESETS: AspectRatioPreset[] = [
  { key: 'square', label: 'Square', ratio: '1:1' },
  { key: '9:16', label: 'Story', ratio: '9:16' },
  { key: '16:9', label: 'Landscape', ratio: '16:9' },
  { key: '3:4', label: 'Portrait', ratio: '3:4' },
  { key: '21:9', label: 'Ultrawide', ratio: '21:9' },
];

export interface ResizeResult {
  url: string;
  name: string;
  logId: string;
  reportId: string;
}

export interface HistoryItem {
  id: string;
  url: string;
  prompt?: string;
  aspectRatio: string;
  targetDims?: [number, number];
  timestamp: string;
  operation: string;
  feedback?: unknown;
}
