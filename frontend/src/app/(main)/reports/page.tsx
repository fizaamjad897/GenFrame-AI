"use client";

import React, { useEffect, useState } from "react";
import {
  Box,
  Container,
  Typography,
  Card,
  CardMedia,
  CardContent,
  CircularProgress,
  Button,
  Chip,
  Paper,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import { useRouter } from "next/navigation";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import { getComplianceHistory, getComplianceSummary } from "@/lib/complianceApi";
import type { ComplianceReport, ComplianceSummary, ComplianceStatus } from "@/types/compliance";
import ComplianceReportModal from "@/app/components/compliance/ComplianceReportModal";

const STATUS_STYLES: Record<ComplianceStatus, { bg: string; color: string }> = {
  PASS: { bg: "#d1fae5", color: "#059669" },
  WARN: { bg: "#fef3c7", color: "#d97706" },
  FAIL: { bg: "#fee2e2", color: "#dc2626" },
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
            <CircularProgress size={40} sx={{ color: "rgba(3, 105, 161, 1)" }} />
          </Box>
        ) : reports.length === 0 ? (
          <Paper
            sx={{
              p: 6,
              textAlign: "center",
              borderRadius: "16px",
              border: "1px dashed #d1d5db",
              bgcolor: "transparent",
            }}
          >
            <Typography sx={{ color: "#6b7280", mb: 2, fontSize: "0.95rem" }}>
              No compliance reports yet — they&apos;re generated automatically each time you process an image.
            </Typography>
            <Button
              variant="contained"
              onClick={() => router.push("/dashboard")}
              sx={{ bgcolor: "rgba(3, 105, 161, 1)", borderRadius: "8px", textTransform: "none", px: 3 }}
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
                  { label: "Avg Score", value: summary.avg_score ?? "—", color: "rgba(3, 105, 161, 1)" },
                  { label: "Pass", value: summary.pass_count, color: "#059669" },
                  { label: "Warn", value: summary.warn_count, color: "#d97706" },
                  { label: "Fail", value: summary.fail_count, color: "#dc2626" },
                ].map((stat) => (
                  <Paper
                    key={stat.label}
                    elevation={0}
                    sx={{ p: 1.75, borderRadius: "12px", border: "1px solid #e5e7eb", textAlign: "center" }}
                  >
                    <Typography sx={{ fontSize: "22px", fontWeight: 700, color: stat.color, lineHeight: 1.2 }}>
                      {stat.value}
                    </Typography>
                    <Typography sx={{ fontSize: "11px", color: "#9ca3af", fontWeight: 600, mt: 0.25 }}>
                      {stat.label}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}

            <Grid container spacing={2}>
              {reports.map((report) => {
                const status = report.compliance?.overall_status;
                const style = status ? STATUS_STYLES[status] : null;
                return (
                  <Grid key={report.report_id} size={{ xs: 12, sm: 6, md: 4, lg: 3 }}>
                    <Card
                      onClick={() => openReport(report)}
                      sx={{
                        borderRadius: "12px",
                        overflow: "hidden",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                        cursor: "pointer",
                        transition: "transform 0.2s",
                        "&:hover": { transform: "translateY(-2px)", boxShadow: "0 4px 12px rgba(0,0,0,0.12)" },
                        height: "100%",
                        display: "flex",
                        flexDirection: "column",
                      }}
                    >
                      <Box
                        sx={{
                          position: "relative",
                          width: "100%",
                          bgcolor: "#f3f4f6",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          aspectRatio: "16 / 9",
                        }}
                      >
                        <CardMedia
                          component="img"
                          image={report.imageUrl}
                          alt="Generated content"
                          sx={{ width: "100%", height: "100%", objectFit: "contain" }}
                        />
                        <Chip
                          label={report.status === "pending" ? "Analyzing" : status || "—"}
                          size="small"
                          sx={{
                            position: "absolute",
                            top: 8,
                            right: 8,
                            bgcolor: style ? style.bg : "#f3f4f6",
                            color: style ? style.color : "#6b7280",
                            fontSize: "10px",
                            fontWeight: 700,
                            height: 20,
                          }}
                        />
                      </Box>
                      <CardContent sx={{ p: 1, flexGrow: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
                        <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <Chip
                            label={report.aspectRatio}
                            size="small"
                            sx={{ bgcolor: "#f3f4f6", color: "#4b5563", fontSize: "9px", fontWeight: 600, height: 18 }}
                          />
                          {report.compliance && (
                            <Typography sx={{ fontSize: "13px", fontWeight: 700, color: "#111827" }}>
                              {report.compliance.overall_score}
                              <Typography component="span" sx={{ fontSize: "10px", color: "#9ca3af" }}>
                                /100
                              </Typography>
                            </Typography>
                          )}
                        </Box>
                        <Typography variant="caption" sx={{ color: "#9ca3af", fontSize: "10px", mt: 0.5, display: "block" }}>
                          {formatTimestamp(report.createdAt)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </>
        )}
      </Container>

      <ComplianceReportModal open={modalOpen} onClose={() => setModalOpen(false)} report={selectedReport} />
    </Box>
  );
}
