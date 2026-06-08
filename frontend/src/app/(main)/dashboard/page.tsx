"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  Box,
  CircularProgress,
  Container,
  Typography,
  ToggleButtonGroup,
  ToggleButton,
  Alert,
} from "@mui/material";
import { useUser } from "@/app/context/AuthContext";
import { usePageHeader } from "@/app/context/PageHeaderContext";
import BillingOverview from "@/app/components/billing/BillingOverview";
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

  return (
    <Box>
      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 } }}>
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

        {!isPostpaid && (
          <Box sx={{ mb: 3 }}>
            <Typography
              sx={{
                fontSize: "14px",
                fontWeight: 600,
                color: "#111827",
                mb: 1.5,
              }}
            >
              Select Engine Type
            </Typography>
            <ToggleButtonGroup
              value={selectedEngine}
              exclusive
              onChange={(_, value) => value && setSelectedEngine(value)}
              sx={{
                "& .MuiToggleButton-root": {
                  textTransform: "none",
                  fontWeight: 500,
                  px: 3,
                  py: 1,
                  "&.Mui-selected": {
                    bgcolor: "rgba(3, 105, 161, 1)",
                    color: "white",
                    "&:hover": { bgcolor: "rgba(3, 105, 161, 0.9)" },
                  },
                },
              }}
            >
              <ToggleButton value="transformation">Transformation</ToggleButton>
              <ToggleButton value="creation">Creation</ToggleButton>
            </ToggleButtonGroup>
          </Box>
        )}

        {isPostpaid ? (
          <Box
            sx={{
              p: 3,
              borderRadius: "16px",
              border: "1px solid #e5e7eb",
              bgcolor: "white",
            }}
          >
            <Typography sx={{ fontSize: "18px", fontWeight: 600, mb: 1 }}>
              Pay-as-you-go Dashboard
            </Typography>
            <Typography sx={{ color: "#6b7280", fontSize: "14px", mb: 2 }}>
              This account is billed by actual usage only. No subscription plan is required.
            </Typography>

            <Box sx={{ p: 2.5, borderRadius: '14px', bgcolor: 'rgba(3, 105, 161, 0.04)', border: '1px solid rgba(3, 105, 161, 0.12)', mb: 2 }}>
              <Typography sx={{ fontSize: '12px', color: '#6b7280', mb: 0.5 }}>Total Credits Used</Typography>
              <Typography sx={{ fontSize: '34px', fontWeight: 700, color: '#111827', lineHeight: 1 }}>
                {totalUsage.toLocaleString()}
              </Typography>
            </Box>

            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: availableEngines.length === 1 ? '1fr' : '1fr 1fr' }, gap: 1.5 }}>
              {perEngineUsage.map((item) => (
                <Box key={item.engine} sx={{ p: 2, borderRadius: '12px', border: '1px solid #e5e7eb', bgcolor: '#fff' }}>
                  <Typography sx={{ fontSize: '12px', color: '#6b7280', mb: 0.5 }}>
                    {item.engine === 'creation' ? 'Creation' : 'Transformation'} Engine
                  </Typography>
                  <Typography sx={{ fontSize: '20px', fontWeight: 600, color: '#111827' }}>
                    {item.used.toLocaleString()} credits
                  </Typography>
                </Box>
              ))}
            </Box>
          </Box>
        ) : (
          <BillingOverview
            user={user}
            selectedEngine={selectedEngine}
            isPendingCancellation={isPendingCancellation}
            processingItem={processingItem}
            onManage={handleManageSubscription}
            onCancel={() => setCancelModalOpen(true)}
          />
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
