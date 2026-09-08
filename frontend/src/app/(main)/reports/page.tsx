"use client";

import React, { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  CircularProgress,
  Button,
  Chip,
  Paper,
} from "@mui/material";
import { useRouter } from "next/navigation";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import { getComplianceHistory, getComplianceSummary } from "@/lib/complianceApi";
import type { ComplianceReport, ComplianceSummary, ComplianceStatus } from "@/types/compliance";
import ComplianceReportModal from "@/app/components/compliance/ComplianceReportModal";
import { ACCENT } from "@/app/theme/terminal";
import { FadeIn } from "@/components/motion/Reveal";

const STATUS_STYLES: Record<ComplianceStatus, { bg: string; color: string }> = {
  PASS: { bg: "#d1fae5", color: "#059669" },
  WARN: { bg: "#fef3c7", color: "#d97706" },
  FAIL: { bg: "#fee2e2", color: "#DC2626" },
};

function formatTimestamp(dateStr: string) {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + " " + date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return dateStr;
  }
}

export default function ReportsPage() {
  const router = useRouter();
  const { setHeader, resetHeader } = usePageHeader();
  const [reports, setReports] = useState<ComplianceReport[]>([]);
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedReport, setSelectedReport] = useState<ComplianceReport | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    setHeader({ title: "Compliance Reports" });
    return () => resetHeader();
  }, [setHeader, resetHeader]);

  useEffect(() => {
    const load = async () => {
      try {
        const [historyData, summaryData] = await Promise.all([
          getComplianceHistory({ limit: 60 }),
          getComplianceSummary(),
        ]);
        setReports(historyData);
        setSummary(summaryData);
      } catch (error) {
        console.error("Error fetching compliance reports:", error);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const openReport = (report: ComplianceReport) => {
    setSelectedReport(report);
    setModalOpen(true);
  };

  return (
    <Box>
      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 3 } }}>
        {loading ? (
          <Box sx={{ display: "flex", justifyContent: "center", py: 8 }}>
            <CircularProgress size={40} sx={{ color: "rgba(139, 92, 246, 1)" }} />
          </Box>
        ) : reports.length === 0 ? (
          <Paper
            elevation={0}
            sx={{
              p: 6,
              textAlign: "center",
              borderRadius: "18px",
              border: "1px solid #E5E7EB",
              bgcolor: "transparent",
              boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            }}
          >
            <Typography sx={{ color: "#6B7280", mb: 2, fontSize: "0.95rem" }}>
              No compliance reports yet — they&apos;re generated automatically each time you process an image.
            </Typography>
            <Button
              variant="contained"
              onClick={() => router.push("/dashboard")}
              sx={{ bgcolor: "rgba(139, 92, 246, 1)", color: "#FFFFFF", borderRadius: "18px", textTransform: "none", px: 3, boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)", fontWeight: 500, "&:hover": { bgcolor: "rgba(139, 92, 246, 1)", filter: "brightness(0.92)", boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)" } }}
            >
              Go to Dashboard
            </Button>
          </Paper>
        ) : (
          <>
            {summary && (
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "repeat(2, 1fr)", sm: "repeat(5, 1fr)" },
                  gap: 1.5,
                  mb: 3,
                }}
              >
                {[
                  { label: "Total Reports", value: summary.total, color: "#111827" },
                  { label: "Avg Score", value: summary.avg_score ?? "—", color: ACCENT },
                  { label: "Pass", value: summary.pass_count, color: "#059669" },
                  { label: "Warn", value: summary.warn_count, color: "#d97706" },
                  { label: "Fail", value: summary.fail_count, color: "#DC2626" },
                ].map((stat, i) => (
                  <FadeIn key={stat.label} delay={i * 0.04}>
                  <Paper
                    elevation={0}
                    sx={{ p: 1.75, borderRadius: "18px", border: "1px solid #E5E7EB", bgcolor: "#FFFFFF", boxShadow: "0 1px 2px 0 rgb(0 0 0 / 0.05)", textAlign: "center" }}
                  >
                    <Typography sx={{ fontSize: "22px", fontWeight: 600, color: stat.color, lineHeight: 1.2 }}>
                      {stat.value}
                    </Typography>
                    <Typography sx={{ fontSize: "11px", color: "#9CA3AF", fontWeight: 500, mt: 0.25 }}>
                      {stat.label}
                    </Typography>
                  </Paper>
                  </FadeIn>
                ))}
              </Box>
            )}

            <Box sx={{ display: "flex", flexDirection: "column", gap: 1 }}>
              {reports.map((report, i) => {
                const status = report.compliance?.overall_status;
                const style = status ? STATUS_STYLES[status] : null;
                return (
                  <FadeIn key={report.report_id} delay={Math.min(i, 10) * 0.02}>
                    <Paper
                      onClick={() => openReport(report)}
                      elevation={0}
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 2,
                        p: 1.25,
                        borderRadius: "12px",
                        border: "1px solid #E5E7EB",
                        cursor: "pointer",
                        transition: "border-color 0.18s",
                        "&:hover": { borderColor: ACCENT },
                      }}
                    >
                      <Box
                        component="img"
                        src={report.imageUrl}
                        alt="Generated content"
                        sx={{
                          width: 76,
                          height: 76,
                          flexShrink: 0,
                          borderRadius: "8px",
                          objectFit: "cover",
                          bgcolor: "#F3F4F6",
                        }}
                      />
                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Box sx={{ display: "flex", alignItems: "center", gap: 1, flexWrap: "wrap", mb: 0.5 }}>
                          <Chip
                            label={report.status === "pending" ? "Analyzing" : status || "—"}
                            size="small"
                            sx={{ bgcolor: style ? style.bg : "#F3F4F6", color: style ? style.color : "#6B7280", fontSize: "10px", fontWeight: 600, height: 20 }}
                          />
                          <Chip
                            label={report.aspectRatio}
                            size="small"
                            sx={{ bgcolor: "#F3F4F6", color: "#4b5563", fontSize: "10px", fontWeight: 500, height: 20 }}
                          />
                          {report.compliance && (
                            <Typography sx={{ fontSize: "13px", fontWeight: 600, color: "#111827" }}>
                              {report.compliance.overall_score}
                              <Typography component="span" sx={{ fontSize: "10px", color: "#9CA3AF" }}>/100</Typography>
                            </Typography>
                          )}
                        </Box>
                        <Typography sx={{ color: "#9CA3AF", fontSize: "11px" }}>
                          {formatTimestamp(report.createdAt)}
                        </Typography>
                      </Box>
                    </Paper>
                  </FadeIn>
                );
              })}
            </Box>
          </>
        )}
      </Container>

      <ComplianceReportModal open={modalOpen} onClose={() => setModalOpen(false)} report={selectedReport} />
    </Box>
  );
}
