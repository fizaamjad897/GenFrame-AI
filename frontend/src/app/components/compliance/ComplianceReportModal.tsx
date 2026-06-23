"use client";

import React from "react";
import {
    Modal,
    Box,
    Typography,
    IconButton,
    Chip,
    Paper,
    Divider,
    CircularProgress,
    Stack,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";
import type { ComplianceReport, ComplianceStatus } from "@/types/compliance";

const STATUS_COLORS: Record<ComplianceStatus, { bg: string; color: string }> = {
    PASS: { bg: "#d1fae5", color: "#059669" },
    WARN: { bg: "#fef3c7", color: "#d97706" },
    FAIL: { bg: "#fee2e2", color: "#dc2626" },
};

function StatusChip({ status }: { status?: ComplianceStatus | null }) {
    if (!status) return null;
    const c = STATUS_COLORS[status];
    return (
        <Chip
            label={status}
            size="small"
            sx={{ bgcolor: c.bg, color: c.color, fontWeight: 700, fontSize: "11px", height: 22 }}
        />
    );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
    return (
        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", py: 0.6 }}>
            <Typography sx={{ fontSize: "12.5px", color: "#6b7280" }}>{label}</Typography>
            <Typography sx={{ fontSize: "12.5px", color: "#111827", fontWeight: 600, textAlign: "right" }}>
                {value}
            </Typography>
        </Box>
    );
}

function Section({ title, status, children }: { title: string; status?: ComplianceStatus | null; children: React.ReactNode }) {
    return (
        <Paper elevation={0} sx={{ border: "1px solid #e5e7eb", borderRadius: "12px", p: 2, flex: 1, minWidth: 220 }}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 1 }}>
                <Typography sx={{ fontSize: "13px", fontWeight: 700, color: "#111827" }}>{title}</Typography>
                <StatusChip status={status} />
            </Box>
            <Divider sx={{ mb: 1 }} />
            {children}
        </Paper>
    );
}

export default function ComplianceReportModal({
    open,
    onClose,
    report,
}: {
    open: boolean;
    onClose: () => void;
    report: ComplianceReport | null;
}) {
    if (!report) return null;
    const c = report.compliance;

    return (
        <Modal open={open} onClose={onClose} sx={{ display: "flex", alignItems: "center", justifyContent: "center", p: 2 }}>
            <Box
                sx={{
                    position: "relative",
                    width: "100%",
                    maxWidth: 760,
                    maxHeight: "90vh",
                    overflowY: "auto",
                    bgcolor: "white",
                    borderRadius: "16px",
                    p: { xs: 2.5, md: 3 },
                    outline: "none",
                    boxShadow: "0 18px 55px rgba(15,23,42,0.35)",
                }}
            >
                <IconButton
                    onClick={onClose}
                    sx={{ position: "absolute", right: 12, top: 12, bgcolor: "#f3f4f6", "&:hover": { bgcolor: "#e5e7eb" } }}
                >
                    <CloseIcon sx={{ fontSize: 20 }} />
                </IconButton>

                <Box sx={{ display: "flex", alignItems: "center", gap: 1.5, mb: 0.5 }}>
                    <Typography sx={{ fontSize: "18px", fontWeight: 700, color: "#111827" }}>
                        Design Compliance Report
                    </Typography>
                    {c && <StatusChip status={c.overall_status} />}
                </Box>
                <Typography sx={{ fontSize: "12px", color: "#9ca3af", mb: 3 }}>
                    {report.aspectRatio} · {report.targetDims.width}×{report.targetDims.height}
                    {report.completedAt ? ` · ${new Date(report.completedAt).toLocaleString()}` : ""}
                </Typography>

                {report.status === "pending" && (
                    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, py: 6 }}>
                        <CircularProgress size={32} sx={{ color: "rgba(3, 105, 161, 1)" }} />
                        <Typography sx={{ fontSize: "13px", color: "#6b7280" }}>
                            Generating compliance report...
                        </Typography>
                    </Box>
                )}

                {report.status === "failed" && (
                    <Box sx={{ py: 4, textAlign: "center" }}>
                        <Typography sx={{ fontSize: "13px", color: "#dc2626" }}>
                            {report.error || "Compliance analysis failed for this image."}
                        </Typography>
                    </Box>
                )}

                {report.status === "complete" && c && (
                    <>
                        <Box
                            sx={{
                                mb: 2.5,
                                p: 2,
                                borderRadius: "12px",
                                bgcolor: "rgba(3, 105, 161, 0.04)",
                                border: "1px solid rgba(3, 105, 161, 0.12)",
                                display: "flex",
                                alignItems: "center",
                                justifyContent: "space-between",
                            }}
                        >
                            <Typography sx={{ fontSize: "13px", color: "#6b7280" }}>Overall Score</Typography>
                            <Typography sx={{ fontSize: "28px", fontWeight: 700, color: "#111827" }}>
                                {c.overall_score}
                                <Typography component="span" sx={{ fontSize: "13px", color: "#9ca3af" }}>
                                    /100
                                </Typography>
                            </Typography>
                        </Box>

                        <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} sx={{ mb: 2.5 }}>
                            <Section title="Technical" status={c.technical.status}>
                                <Row label="Dimensions" value={`${c.technical.actual_dims.width}×${c.technical.actual_dims.height}`} />
                                <Row label="Target" value={`${c.technical.target_dims.width}×${c.technical.target_dims.height}`} />
                                <Row label="File size" value={`${c.technical.file_size_kb} KB`} />
                                <Row label="Format" value={c.technical.format} />
                            </Section>

                            <Section title="Visual" status={c.visual.status}>
                                <Row label="Contrast" value={`${c.visual.contrast_ratio}:1`} />
                                <Row label="Safe zone" value={c.visual.safe_zone_clear ? "Clear" : "Crowded edges"} />
                                <Row label="Clutter score" value={c.visual.clutter_score} />
                                <Row label="Saturation" value={`${c.visual.avg_saturation}%`} />
                                {c.visual.dominant_colors.length > 0 && (
                                    <Box sx={{ display: "flex", gap: 0.5, mt: 1 }}>
                                        {c.visual.dominant_colors.map((hex) => (
                                            <Box
                                                key={hex}
                                                title={hex}
                                                sx={{ width: 18, height: 18, borderRadius: "4px", bgcolor: hex, border: "1px solid #e5e7eb" }}
                                            />
                                        ))}
                                    </Box>
                                )}
                            </Section>

                            <Section title="Content" status={c.content.status}>
                                <Row
                                    label="Prompt adherence"
                                    value={c.content.prompt_adherence_score !== null ? `${c.content.prompt_adherence_score}/100` : "N/A"}
                                />
                                <Row label="Text readable" value={c.content.text_readable === null ? "N/A" : c.content.text_readable ? "Yes" : "No"} />
                                <Row
                                    label="Focal point"
                                    value={c.content.focal_point_centered === null ? "N/A" : c.content.focal_point_centered ? "Centered" : "Off-center"}
                                />
                            </Section>
                        </Stack>

                        {c.content.ai_analysis && (
                            <Box sx={{ mb: 2.5, p: 2, borderRadius: "12px", bgcolor: "#f9fafb", border: "1px solid #f3f4f6" }}>
                                <Typography sx={{ fontSize: "11px", fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", mb: 0.5 }}>
                                    AI Analysis
                                </Typography>
                                <Typography sx={{ fontSize: "13px", color: "#374151", lineHeight: 1.6 }}>
                                    {c.content.ai_analysis}
                                </Typography>
                            </Box>
                        )}

                        {report.recommendations.length > 0 && (
                            <Box>
                                <Typography sx={{ fontSize: "11px", fontWeight: 700, color: "#9ca3af", textTransform: "uppercase", mb: 1 }}>
                                    Recommendations
                                </Typography>
                                <Stack spacing={1}>
                                    {report.recommendations.map((rec, idx) => (
                                        <Box key={idx} sx={{ display: "flex", gap: 1, alignItems: "flex-start" }}>
                                            <Box sx={{ width: 5, height: 5, borderRadius: "50%", bgcolor: "rgba(3, 105, 161, 1)", mt: "7px", flexShrink: 0 }} />
                                            <Typography sx={{ fontSize: "12.5px", color: "#374151", lineHeight: 1.5 }}>{rec}</Typography>
                                        </Box>
                                    ))}
                                </Stack>
                            </Box>
                        )}
                    </>
                )}
            </Box>
        </Modal>
    );
}
