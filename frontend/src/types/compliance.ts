/**
 * Type definitions for Design Compliance Reports
 */

export type ComplianceStatus = "PASS" | "WARN" | "FAIL";
export type ReportStatus = "pending" | "complete" | "failed";

export interface TechnicalCheck {
    status: ComplianceStatus;
    actual_dims: { width: number; height: number };
    target_dims: { width: number; height: number };
    dims_match: boolean;
    file_size_kb: number;
    format: string;
}

export interface VisualCheck {
    status: ComplianceStatus;
    safe_zone_clear: boolean;
    contrast_ratio: number;
    contrast_status: ComplianceStatus;
    clutter_score: number;
    avg_saturation: number;
    dominant_colors: string[];
}

export interface ContentCheck {
    status: ComplianceStatus;
    prompt_adherence_score: number | null;
    text_readable: boolean | null;
    text_readability_notes: string | null;
    focal_point_centered: boolean | null;
    clutter_assessment: string | null;
    ai_analysis: string | null;
}

export interface ComplianceBreakdown {
    overall_score: number;
    overall_status: ComplianceStatus;
    technical: TechnicalCheck;
    visual: VisualCheck;
    content: ContentCheck;
}

export interface ComplianceReport {
    _id: string;
    report_id: string;
    job_id: string | null;
    userId: string;
    engineType: string;
    imageUrl: string;
    prompt: string | null;
    aspectRatio: string;
    targetDims: { width: number; height: number };
    status: ReportStatus;
    compliance: ComplianceBreakdown | null;
    recommendations: string[];
    createdAt: string;
    completedAt: string | null;
    error: string | null;
}

export interface ComplianceSummary {
    total: number;
    avg_score: number | null;
    pass_count: number;
    warn_count: number;
    fail_count: number;
    pending_count: number;
}
