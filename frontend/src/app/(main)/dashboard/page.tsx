"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  CircularProgress,
  Container,
  Paper,
  Stack,
  Grid,
  Button,
  Chip,
  Divider,
  Typography,
  Alert,
} from "@mui/material";
import { useUser } from "@/app/context/AuthContext";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import BoltIcon from "@mui/icons-material/Bolt";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import AddPhotoAlternateIcon from "@mui/icons-material/AddPhotoAlternate";
import BillingOverview from "@/app/components/billing/BillingOverview";
import UsageDisplay from "@/app/components/dashboard/UsageDisplay";
import CancelSubscriptionModal from "@/app/components/modals/CancelSubscriptionModal";
import {
  redirectToPortal,
  cancelSubscription,
  refreshSubscriptionStatus,
} from "@/lib/stripe";
import type { EngineType } from "@/types/billing";
import { getPlanLabel } from "@/types/billing";

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading, refreshUser } = useUser();
  const { setHeader, resetHeader } = usePageHeader();
  const [selectedEngine, setSelectedEngine] =
    useState<EngineType>("transformation");
  const [processingItem, setProcessingItem] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [cancelModalOpen, setCancelModalOpen] = useState(false);

  useEffect(() => {
    setHeader({ title: "Dashboard" });
    return () => resetHeader();
  }, [setHeader, resetHeader]);

  const handleManageSubscription = useCallback(async () => {
    setProcessingItem("portal");
    setError(null);
    setSuccess(null);
    try {
      await redirectToPortal();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to open billing portal",
      );
      setProcessingItem(null);
    }
  }, []);

  const handleCancelSubscription = useCallback(async () => {
    setProcessingItem("cancel");
    setError(null);
    setSuccess(null);
    setCancelModalOpen(false);
    try {
      const result = await cancelSubscription(true, selectedEngine);
      if (result.cancelled) {
        await refreshUser();
        setSuccess("Plan cancelled successfully.");
      } else {
        setError("Cancellation failed.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to cancel plan");
    } finally {
      setProcessingItem(null);
    }
  }, [selectedEngine, refreshUser]);

  if (loading || !user) {
    return (
      <Box
        sx={{
          minHeight: "60vh",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <CircularProgress size={32} sx={{ color: "rgba(3, 105, 161, 1)" }} />
      </Box>
    );
  }

  const engineInfo = user.engine_data?.[selectedEngine];
  const isPostpaid = Boolean(user.is_postpaid);
  const availableEngines =
    user.available_engines && user.available_engines.length > 0
      ? user.available_engines
      : ["transformation", "creation"];
  const perEngineUsage = availableEngines.map((etype) => {
    const credits = user.engine_data?.[etype as EngineType]?.credits || user.credits;
    return {
      engine: etype,
      used:
        (credits?.monthly_units_used || 0) + (credits?.addon_units_used || 0),
    };
  });
  const totalUsage = perEngineUsage.reduce((sum, item) => sum + item.used, 0);
  const isPendingCancellation = Boolean(
    engineInfo?.credits?.is_pending_cancellation,
  );
  const currentPlanRaw = engineInfo?.plan || "";
  const currentPlanLabel = getPlanLabel(currentPlanRaw);
  const selectedEngineLabel = selectedEngine === "creation" ? "Creation" : "Transformation";
  const currentCredits = engineInfo?.credits || user.credits;
  const totalCreditsUsed = ((currentCredits?.monthly_units_used || 0) + (currentCredits?.addon_units_used || 0));
  const totalCreditsMax = ((currentCredits?.monthly_units_max || 0) + (currentCredits?.addon_units_max || 0));
  const remainingCredits = Math.max(0, totalCreditsMax - totalCreditsUsed);
  const dashboardStats = [
    {
      label: "Total used",
      value: totalCreditsUsed.toLocaleString(),
      tone: "#0369A1",
      hint: isPostpaid ? "Usage billing" : "Combined credits",
      icon: <TrendingUpIcon sx={{ fontSize: 18 }} />,
    },
    {
      label: "Remaining",
      value: remainingCredits.toLocaleString(),
      tone: "#10b981",
      hint: isPostpaid ? "Keep creating" : "Before limit",
      icon: <BoltIcon sx={{ fontSize: 18 }} />,
    },
    {
      label: "Active engine",
      value: selectedEngineLabel,
      tone: "#111827",
      hint: currentPlanLabel,
      icon: <AutoFixHighIcon sx={{ fontSize: 18 }} />,
    },
  ];

  const engineCards = [
    {
      key: "transformation" as EngineType,
      title: "Transformation Engine",
      description: "Adapt existing creatives with smart composition, expansion, and cleanup for every output size.",
      accent: "#0369A1",
      icon: <AutoFixHighIcon sx={{ fontSize: 20 }} />,
      chips: ["AI resizing", "Background extension", "Subject-safe crops"],
    },
    {
      key: "creation" as EngineType,
      title: "Creation Engine",
      description: "Generate new channel-ready variants from your source image with cleaner layout and brand framing.",
      accent: "#0EA5E9",
      icon: <AddPhotoAlternateIcon sx={{ fontSize: 20 }} />,
      chips: ["Variant generation", "Brand layout", "Multi-format output"],
    },
  ];

  return (
    <Box
      sx={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at top left, rgba(3, 105, 161, 0.08), transparent 32%), linear-gradient(180deg, #f8fbfe 0%, #ffffff 40%, #f8fafc 100%)",
      }}
    >
      <Container maxWidth="xl" sx={{ py: { xs: 2.5, md: 4 } }}>
        {error && (
          <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}
        {success && (
          <Alert
            severity="success"
            sx={{ mb: 3 }}
            onClose={() => setSuccess(null)}
          >
            {success}
          </Alert>
        )}

        <Paper
          elevation={0}
          sx={{
            mb: 3,
            p: { xs: 2.5, md: 3.5 },
            borderRadius: "28px",
            border: "1px solid rgba(3, 105, 161, 0.12)",
            background:
              "linear-gradient(135deg, rgba(3, 105, 161, 0.10) 0%, rgba(14, 165, 233, 0.05) 55%, rgba(255, 255, 255, 0.96) 100%)",
            boxShadow: "0 16px 50px -28px rgba(3, 105, 161, 0.35)",
          }}
        >
          <Stack spacing={2.5}>
            <Stack
              direction={{ xs: "column", md: "row" }}
              alignItems={{ xs: "flex-start", md: "center" }}
              justifyContent="space-between"
              spacing={2}
            >
              <Box>
                <Chip
                  label={isPostpaid ? "Pay as you go" : currentPlanLabel}
                  sx={{
                    mb: 1.5,
                    bgcolor: "rgba(3, 105, 161, 0.10)",
                    color: "rgba(3, 105, 161, 1)",
                    fontWeight: 500,
                    fontSize: "12px",
                  }}
                />
                <Typography
                  sx={{
                    fontSize: { xs: "28px", md: "38px" },
                    lineHeight: 1.05,
                    fontWeight: 600,
                    letterSpacing: "-0.04em",
                    color: "#0f172a",
                    mb: 1,
                  }}
                >
                  Dashboard
                </Typography>
                <Typography
                  sx={{
                    maxWidth: "780px",
                    color: "#475569",
                    fontSize: { xs: "14px", md: "15px" },
                    lineHeight: 1.7,
                  }}
                >
                  Track usage, review billing state, and jump straight to the
                  active engine without the content collapsing into one dense card.
                </Typography>
              </Box>

              <Stack direction={{ xs: "column", sm: "row" }} spacing={1.25}>
                <Button
                  variant="outlined"
                  onClick={() => router.push("/pricing")}
                  sx={{
                    textTransform: "none",
                    borderRadius: "12px",
                    px: 2.2,
                    py: 1.05,
                    fontWeight: 500,
                  }}
                >
                  View pricing
                </Button>
                <Button
                  variant="contained"
                  onClick={() => router.push("/billing")}
                  sx={{
                    textTransform: "none",
                    borderRadius: "12px",
                    px: 2.4,
                    py: 1.05,
                    fontWeight: 500,
                    bgcolor: "rgba(3, 105, 161, 1)",
                    boxShadow: "0 10px 24px rgba(3, 105, 161, 0.22)",
                    '&:hover': { bgcolor: "rgba(3, 105, 161, 0.92)" },
                  }}
                >
                  Billing
                </Button>
              </Stack>
            </Stack>

            <Divider sx={{ borderColor: "rgba(3, 105, 161, 0.10)" }} />

            <Grid container spacing={2}>
              {dashboardStats.map((stat) => (
                <Grid key={stat.label} size={{ xs: 12, md: 4 }}>
                  <Paper
                    elevation={0}
                    sx={{
                      height: "100%",
                      p: 2.25,
                      borderRadius: "18px",
                      bgcolor: "rgba(255,255,255,0.96)",
                      border: "1px solid rgba(3, 105, 161, 0.12)",
                      boxShadow: "0 10px 28px -20px rgba(15, 23, 42, 0.35)",
                      position: "relative",
                      overflow: "hidden",
                    }}
                  >
                    <Box
                      sx={{
                        position: "absolute",
                        inset: 0,
                        background: `linear-gradient(135deg, ${stat.tone}1c, transparent 65%)`,
                        pointerEvents: "none",
                      }}
                    />
                    <Stack spacing={1} sx={{ position: "relative" }}>
                      <Box
                        sx={{
                          width: 32,
                          height: 32,
                          borderRadius: "10px",
                          bgcolor: `${stat.tone}14`,
                          color: stat.tone,
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                        }}
                      >
                        {stat.icon}
                      </Box>
                      <Typography sx={{ fontSize: 12, color: "#64748b", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                        {stat.label}
                      </Typography>
                      <Typography sx={{ fontSize: { xs: 24, md: 28 }, fontWeight: 600, color: stat.tone, lineHeight: 1.05 }}>
                        {stat.value}
                      </Typography>
                      <Typography sx={{ fontSize: 13, color: "#475569" }}>
                        {stat.hint}
                      </Typography>
                    </Stack>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Stack>
        </Paper>

        <Box sx={{ mb: 3 }}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1.5 }}>
            <Box>
              <Typography sx={{ fontSize: 14, fontWeight: 600, color: "#111827", letterSpacing: "-0.01em" }}>
                Engines
              </Typography>
              <Typography sx={{ fontSize: 13, color: "#6b7280" }}>
                Pick the engine you want to analyze or bill against.
              </Typography>
            </Box>
            <Button
              variant="outlined"
              onClick={() => router.push("/reports")}
              sx={{
                textTransform: "none",
                borderRadius: "999px",
                px: 2,
                fontWeight: 500,
              }}
            >
              Design Analytics
            </Button>
          </Stack>

          <Grid container spacing={2}>
            {engineCards.map((engine) => {
              const selected = selectedEngine === engine.key;
              return (
                <Grid key={engine.key} size={{ xs: 12, md: 6 }}>
                  <Paper
                    elevation={0}
                    onClick={() => setSelectedEngine(engine.key)}
                    sx={{
                      height: "100%",
                      p: 2.5,
                      borderRadius: "22px",
                      border: selected ? `1px solid ${engine.accent}44` : "1px solid rgba(3, 105, 161, 0.10)",
                      bgcolor: selected ? "rgba(255,255,255,0.98)" : "rgba(255,255,255,0.94)",
                      boxShadow: selected ? `0 24px 50px -28px ${engine.accent}80` : "0 14px 34px -28px rgba(15, 23, 42, 0.24)",
                      cursor: "pointer",
                      position: "relative",
                      overflow: "hidden",
                      transition: "all 0.22s ease",
                      transform: selected ? "translateY(-2px)" : "translateY(0)",
                      "&:hover": {
                        transform: "translateY(-3px)",
                        boxShadow: `0 28px 56px -30px ${engine.accent}80`,
                      },
                    }}
                  >
                    <Box
                      sx={{
                        position: "absolute",
                        inset: 0,
                        background: `radial-gradient(circle at top right, ${engine.accent}16, transparent 55%)`,
                        pointerEvents: "none",
                      }}
                    />
                    <Stack spacing={1.8} sx={{ position: "relative" }}>
                      <Stack direction="row" alignItems="flex-start" justifyContent="space-between" spacing={2}>
                        <Stack direction="row" spacing={1.5} alignItems="flex-start">
                          <Box
                            sx={{
                              width: 40,
                              height: 40,
                              borderRadius: "12px",
                              flexShrink: 0,
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              color: "#fff",
                              background: `linear-gradient(135deg, ${engine.accent}, ${engine.accent}cc)`,
                              boxShadow: `0 6px 16px -6px ${engine.accent}80`,
                            }}
                          >
                            {engine.icon}
                          </Box>
                          <Box>
                            <Typography sx={{ fontSize: 12, fontWeight: 500, color: engine.accent, textTransform: "uppercase", letterSpacing: "0.08em", mb: 0.75 }}>
                              {selected ? "Active engine" : "Available engine"}
                            </Typography>
                            <Typography sx={{ fontSize: 20, fontWeight: 600, color: "#111827", letterSpacing: "-0.03em" }}>
                              {engine.title}
                            </Typography>
                          </Box>
                        </Stack>
                        {selected && (
                          <Chip
                            label="Selected"
                            size="small"
                            sx={{ bgcolor: `${engine.accent}14`, color: engine.accent, fontWeight: 600 }}
                          />
                        )}
                      </Stack>

                      <Typography sx={{ fontSize: 14, color: "#475569", lineHeight: 1.7, maxWidth: 560 }}>
                        {engine.description}
                      </Typography>

                      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                        {engine.chips.map((chip) => (
                          <Chip
                            key={chip}
                            label={chip}
                            size="small"
                            sx={{
                              bgcolor: selected ? `${engine.accent}10` : "#f8fafc",
                              color: selected ? engine.accent : "#475569",
                              fontWeight: 500,
                              fontSize: 11,
                            }}
                          />
                        ))}
                      </Stack>

                      <Stack direction="row" alignItems="center" justifyContent="space-between" spacing={2}>
                        <Box>
                          <Typography sx={{ fontSize: 12, color: "#6b7280" }}>Plan</Typography>
                          <Typography sx={{ fontSize: 14, fontWeight: 600, color: "#111827" }}>{currentPlanLabel}</Typography>
                        </Box>
                        <Stack direction="row" spacing={1}>
                          <Button
                            variant={selected ? "contained" : "outlined"}
                            onClick={(event) => {
                              event.stopPropagation();
                              setSelectedEngine(engine.key);
                            }}
                            sx={{
                              textTransform: "none",
                              borderRadius: "999px",
                              px: 2.2,
                              fontWeight: 600,
                              bgcolor: selected ? engine.accent : "transparent",
                              borderColor: `${engine.accent}33`,
                              color: selected ? "white" : engine.accent,
                              "&:hover": {
                                bgcolor: selected ? engine.accent : `${engine.accent}10`,
                                borderColor: `${engine.accent}55`,
                              },
                            }}
                          >
                            {selected ? "Selected" : "Select engine"}
                          </Button>
                          <Button
                            variant="contained"
                            onClick={(event) => {
                              event.stopPropagation();
                              router.push(`/${engine.key}-engine`);
                            }}
                            sx={{
                              textTransform: "none",
                              borderRadius: "999px",
                              px: 2.2,
                              fontWeight: 600,
                              bgcolor: engine.accent,
                              color: "white",
                              boxShadow: `0 8px 18px -8px ${engine.accent}99`,
                              "&:hover": { bgcolor: engine.accent, opacity: 0.92 },
                            }}
                          >
                            Open engine
                          </Button>
                        </Stack>
                      </Stack>
                    </Stack>
                  </Paper>
                </Grid>
              );
            })}
          </Grid>
        </Box>

        {isPostpaid ? (
          <Box
            sx={{
              p: { xs: 2, md: 3 },
              borderRadius: "24px",
              border: "1px solid rgba(3, 105, 161, 0.10)",
              bgcolor: "rgba(255, 255, 255, 0.92)",
              boxShadow: "0 18px 40px -30px rgba(15, 23, 42, 0.35)",
            }}
          >
            <Stack spacing={2.5}>
              <Box>
                <Typography sx={{ fontSize: "18px", fontWeight: 600, color: "#111827", mb: 1 }}>
                  Pay-as-you-go Dashboard
                </Typography>
                <Typography sx={{ color: "#6b7280", fontSize: "14px" }}>
                  This account is billed by actual usage only. No subscription plan is required.
                </Typography>
              </Box>

              <Box
                sx={{
                  p: 2.5,
                  borderRadius: '16px',
                  background: 'linear-gradient(135deg, rgba(7,89,133,0.08), rgba(3,105,161,0.03))',
                  border: '1px solid rgba(3, 105, 161, 0.14)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                }}
              >
                <Box
                  sx={{
                    width: 44, height: 44, borderRadius: '12px', flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: 'linear-gradient(135deg, #075985, #0369A1)', color: '#fff',
                    boxShadow: '0 6px 16px -6px rgba(3, 105, 161, 0.5)',
                  }}
                >
                  <TrendingUpIcon sx={{ fontSize: 22 }} />
                </Box>
                <Box>
                  <Typography sx={{ fontSize: '12px', color: '#6b7280', mb: 0.25 }}>Total Credits Used</Typography>
                  <Typography sx={{ fontSize: { xs: '28px', md: '34px' }, fontWeight: 600, color: '#111827', lineHeight: 1 }}>
                    {totalUsage.toLocaleString()}
                  </Typography>
                </Box>
              </Box>

              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: availableEngines.length === 1 ? '1fr' : '1fr 1fr' }, gap: 1.5 }}>
              {perEngineUsage.map((item) => {
                const engineAccent = item.engine === 'creation' ? '#0EA5E9' : '#0369A1';
                return (
                  <Box key={item.engine} sx={{ p: 2, borderRadius: '12px', border: '1px solid rgba(3, 105, 161, 0.10)', bgcolor: '#fff', position: 'relative', overflow: 'hidden' }}>
                    <Box sx={{ position: 'absolute', inset: 0, background: `linear-gradient(135deg, ${engineAccent}10, transparent 65%)`, pointerEvents: 'none' }} />
                    <Typography sx={{ fontSize: '12px', color: '#6b7280', mb: 0.5, position: 'relative' }}>
                      {item.engine === 'creation' ? 'Creation' : 'Transformation'} Engine
                    </Typography>
                    <Typography sx={{ fontSize: '20px', fontWeight: 500, color: engineAccent, position: 'relative' }}>
                      {item.used.toLocaleString()} credits
                    </Typography>
                  </Box>
                );
              })}
              </Box>

              <UsageDisplay horizontal engineType={selectedEngine} />
            </Stack>
          </Box>
        ) : (
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, lg: 8 }}>
              <BillingOverview
                user={user}
                selectedEngine={selectedEngine}
                isPendingCancellation={isPendingCancellation}
                processingItem={processingItem}
                onManage={handleManageSubscription}
                onCancel={() => setCancelModalOpen(true)}
              />
            </Grid>
            <Grid size={{ xs: 12, lg: 4 }}>
              <Paper
                elevation={0}
                sx={{
                  p: 3,
                  borderRadius: "24px",
                  border: "1px solid rgba(3, 105, 161, 0.10)",
                  bgcolor: "rgba(255, 255, 255, 0.92)",
                  boxShadow: "0 18px 40px -30px rgba(15, 23, 42, 0.35)",
                  position: "sticky",
                  top: 88,
                }}
              >
                <Stack spacing={2}>
                  <Box>
                    <Typography sx={{ fontSize: 12, fontWeight: 500, color: "#0369A1", textTransform: "uppercase", letterSpacing: "0.08em", mb: 1 }}>
                      Next actions
                    </Typography>
                    <Typography sx={{ fontSize: 20, fontWeight: 600, color: "#111827", mb: 1 }}>
                      Keep the dashboard readable
                    </Typography>
                    <Typography sx={{ color: "#6b7280", fontSize: 14, lineHeight: 1.7 }}>
                      The page now uses a proper split layout, so billing, usage, and account actions no longer sit on top of each other.
                    </Typography>
                  </Box>

                  <Stack direction="column" spacing={1.2}>
                    <Button
                      variant="contained"
                      onClick={() => router.push("/pricing")}
                      sx={{
                        textTransform: "none",
                        borderRadius: "12px",
                        py: 1.1,
                        fontWeight: 500,
                        bgcolor: "rgba(3, 105, 161, 1)",
                        '&:hover': { bgcolor: "rgba(3, 105, 161, 0.92)" },
                      }}
                    >
                      Review plans
                    </Button>
                    <Button
                      variant="outlined"
                      onClick={() => router.push("/archive")}
                      sx={{
                        textTransform: "none",
                        borderRadius: "12px",
                        py: 1.1,
                        fontWeight: 500,
                      }}
                    >
                      Open archive
                    </Button>
                  </Stack>
                </Stack>
              </Paper>
            </Grid>
          </Grid>
        )}

        {!isPostpaid && (
          <CancelSubscriptionModal
            open={cancelModalOpen}
            onClose={() => setCancelModalOpen(false)}
            onConfirm={handleCancelSubscription}
            planName={currentPlanLabel}
            loading={processingItem === "cancel"}
          />
        )}
      </Container>
    </Box>
  );
}
