"use client";

import React from "react";
import { useRouter } from "next/navigation";
import Pricing from "@/app/components/pricing/Pricing";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import GridMark from "@/app/theme/GridMark";
import { CREAM, INK, ACCENT, TEXT_MUTED_L, BORDER_L, MONO } from "@/app/theme/terminal";

export default function PricingPage() {
  const router = useRouter();

  return (
    <div style={{ minHeight: "100vh", background: CREAM, fontFamily: "'Inter', system-ui, sans-serif" }}>
      {/* Nav */}
      <nav style={{ position: "sticky", top: 0, zIndex: 100, background: CREAM, borderBottom: `1px solid ${BORDER_L}`, padding: "0 clamp(18px,4vw,52px)", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <GridMark size={34} />
          <div>
            <div style={{ fontSize: 16, fontWeight: 600, color: INK, letterSpacing: "-0.03em", lineHeight: 1.1 }}>Recreative AI</div>
            <div style={{ fontSize: 9, color: TEXT_MUTED_L, letterSpacing: "0.04em", fontFamily: MONO, textTransform: "uppercase" }}>AI Image Adaptation</div>
          </div>
        </div>
        <button
          onClick={() => router.push("/")}
          style={{ display: "flex", alignItems: "center", gap: 6, background: "transparent", border: `1px solid ${BORDER_L}`, borderRadius: 3, padding: "8px 14px", fontSize: 13, color: ACCENT, cursor: "pointer", fontFamily: "inherit", fontWeight: 500 }}>
          <ArrowBackIcon sx={{ fontSize: 15 }} /> Back to Home
        </button>
      </nav>

      {/* Hero */}
      <div style={{ textAlign: "center", padding: "52px 20px 12px" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "transparent", border: `1px solid ${ACCENT}`, borderRadius: 3, padding: "5px 14px", marginBottom: 18 }}>
          <span style={{ fontSize: 10, fontWeight: 500, color: ACCENT, letterSpacing: "0.08em", fontFamily: MONO }}>SIMPLE PRICING</span>
        </div>
        <h1 style={{ fontSize: "clamp(26px,5vw,48px)", fontWeight: 600, color: INK, letterSpacing: "-0.03em", lineHeight: 1.1, marginBottom: 14 }}>
          Plans &amp; Pricing
        </h1>
        <p style={{ fontSize: 16, color: TEXT_MUTED_L, maxWidth: 480, margin: "0 auto", lineHeight: 1.65 }}>
          Start with 2 free generations. No credit card required. Upgrade when you need more.
        </p>
      </div>

      {/* Pricing component */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 20px 80px" }}>
        <Pricing />
      </div>

      {/* Footer */}
      <footer style={{ borderTop: `1px solid ${BORDER_L}`, padding: "28px clamp(18px,4vw,52px)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <span style={{ fontSize: 13, color: TEXT_MUTED_L, fontFamily: MONO }}>Recreative AI · AI Image Adaptation · 2026</span>
        <div style={{ display: "flex", gap: 20 }}>
          {["Privacy Policy", "Terms of Service", "Contact Sales"].map(l => (
            <span key={l} style={{ fontSize: 12, color: TEXT_MUTED_L, cursor: "pointer" }}>{l}</span>
          ))}
        </div>
      </footer>
    </div>
  );
}
