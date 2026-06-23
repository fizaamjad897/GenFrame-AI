/**
 * API client for Design Compliance Reports
 */
import { authFetch } from "./api";
import type { ComplianceReport, ComplianceSummary, ReportStatus } from "@/types/compliance";

export async function getComplianceReport(reportId: string): Promise<ComplianceReport> {
    return authFetch<ComplianceReport>(`/reports/${reportId}`);
}

export interface ComplianceHistoryParams {
    engineType?: string;
    status?: ReportStatus;
    limit?: number;
    skip?: number;
}

export async function getComplianceHistory(
    params: ComplianceHistoryParams = {},
): Promise<ComplianceReport[]> {
    const query = new URLSearchParams();
    if (params.engineType) query.set("engine_type", params.engineType);
    if (params.status) query.set("status", params.status);
    if (params.limit) query.set("limit", String(params.limit));
    if (params.skip) query.set("skip", String(params.skip));

    const qs = query.toString();
    const data = await authFetch<{ reports: ComplianceReport[] }>(
        `/reports/history${qs ? `?${qs}` : ""}`,
    );
    return data.reports || [];
}

export async function getComplianceSummary(): Promise<ComplianceSummary> {
    return authFetch<ComplianceSummary>("/reports/summary");
}
