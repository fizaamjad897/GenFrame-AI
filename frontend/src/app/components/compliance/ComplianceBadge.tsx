"use client";

import React, { useEffect, useRef, useState } from "react";
import { Chip, CircularProgress } from "@mui/material";
import VerifiedIcon from "@mui/icons-material/Verified";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import { getComplianceReport } from "@/lib/complianceApi";
import type { ComplianceReport } from "@/types/compliance";
import ComplianceReportModal from "./ComplianceReportModal";

const POLL_INTERVAL_MS = 2000;
const MAX_POLLS = 15; // ~30s

const STATUS_STYLES: Record<string, { bg: string; color: string; icon: React.ReactElement }> = {
    PASS: { bg: "#d1fae5", color: "#059669", icon: <VerifiedIcon sx={{ fontSize: 14 }} /> },
    WARN: { bg: "#fef3c7", color: "#d97706", icon: <WarningAmberIcon sx={{ fontSize: 14 }} /> },
    FAIL: { bg: "#fee2e2", color: "#dc2626", icon: <ErrorOutlineIcon sx={{ fontSize: 14 }} /> },
};

export default function ComplianceBadge({ reportId }: { reportId?: string }) {
    const [report, setReport] = useState<ComplianceReport | null>(null);
    const [modalOpen, setModalOpen] = useState(false);
    const pollCountRef = useRef(0);
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    useEffect(() => {
        if (!reportId) return;
        let cancelled = false;
        pollCountRef.current = 0;

        const fetchOnce = async () => {
            try {
                const data = await getComplianceReport(reportId);
                if (cancelled) return;
                setReport(data);

                if (data.status === "pending" && pollCountRef.current < MAX_POLLS) {
                    pollCountRef.current += 1;
                    timerRef.current = setTimeout(fetchOnce, POLL_INTERVAL_MS);
                }
            } catch {
                // Swallow — badge just won't render if the report can't be fetched yet.
            }
        };

        fetchOnce();

        return () => {
            cancelled = true;
            if (timerRef.current) clearTimeout(timerRef.current);
        };
    }, [reportId]);

    if (!reportId || !report) return null;

    const isPending = report.status === "pending";
    const isFailed = report.status === "failed";
    const overallStatus = report.compliance?.overall_status;
    const style = overallStatus ? STATUS_STYLES[overallStatus] : null;

    return (
        <>
            {isPending ? (
                <Chip
                    size="small"
                    icon={<CircularProgress size={10} thickness={6} sx={{ color: "#6b7280", ml: "6px" }} />}
                    label="Analyzing"
                    sx={{ bgcolor: "#f3f4f6", color: "#6b7280", fontSize: "10px", fontWeight: 600, height: 20 }}
                />
            ) : isFailed || !style ? (
                <Chip
                    size="small"
                    onClick={() => setModalOpen(true)}
                    label="Report unavailable"
                    sx={{ bgcolor: "#f3f4f6", color: "#9ca3af", fontSize: "10px", fontWeight: 600, height: 20, cursor: "pointer" }}
                />
            ) : (
                <Chip
                    size="small"
                    onClick={() => setModalOpen(true)}
                    icon={style.icon}
                    label={`${overallStatus} · ${report.compliance?.overall_score}`}
                    sx={{
                        bgcolor: style.bg,
                        color: style.color,
                        fontSize: "10px",
                        fontWeight: 600,
                        height: 20,
                        cursor: "pointer",
                        "& .MuiChip-icon": { color: style.color },
                    }}
                />
            )}
            <ComplianceReportModal open={modalOpen} onClose={() => setModalOpen(false)} report={report} />
        </>
    );
}
