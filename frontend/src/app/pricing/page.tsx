"use client";

import React from "react";
import { useRouter } from "next/navigation";
import Pricing from "@/app/components/pricing/Pricing";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

const P = "#0369A1";

export default function PricingPage() {
  const router = useRouter();

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc", fontFamily: "'Inter', system-ui, sans-serif" }}>
      {/* Nav */}
      <nav style={{ position: "sticky", top: 0, zIndex: 100, background: "rgba(255,255,255,0.92)", backdropFilter: "blur(20px)", borderBottom: "1px solid #f1f5f9", padding: "0 clamp(18px,4vw,52px)", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 34, height: 34, borderRadius: 10, background: "linear-gradient(135deg,#075985,#0369A1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <AutoAwesomeIcon sx={{ fontSize: 16, color: "white" }} />
          </div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: "#0f172a", letterSpacing: "-0.03em", lineHeight: 1.1 }}>GenFrame</div>
            <div style={{ fontSize: 9, color: "#94a3b8", letterSpacing: "0.04em" }}>AI Image Adaptation</div>
          </div>
        </div>
        <button
          onClick={() => router.push("/")}
          style={{ display: "flex", alignItems: "center", gap: 6, background: "transparent", border: `1.5px solid ${P}28`, borderRadius: 9, padding: "8px 14px", fontSize: 13, color: P, cursor: "pointer", fontFamily: "inherit" }}>
          <ArrowBackIcon sx={{ fontSize: 15 }} /> Back to Home
        </button>
      </nav>

      {/* Hero */}
      <div style={{ textAlign: "center", padding: "52px 20px 12px" }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "#F0F9FF", border: `1px solid ${P}28`, borderRadius: 100, padding: "5px 14px", marginBottom: 18 }}>
          <span style={{ fontSize: 10, fontWeight: 500, color: P, letterSpacing: "0.08em" }}>SIMPLE PRICING</span>
        </div>
        <h1 style={{ fontSize: "clamp(26px,5vw,48px)", fontWeight: 700, color: "#0f172a", letterSpacing: "-0.03em", lineHeight: 1.1, marginBottom: 14 }}>
          Plans & Pricing
        </h1>
        <p style={{ fontSize: 16, color: "#64748b", maxWidth: 480, margin: "0 auto", lineHeight: 1.65 }}>
          Start with 2 free generations. No credit card required. Upgrade when you need more.
        </p>
      </div>

      {/* Pricing component */}
      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "0 20px 80px" }}>
        <Pricing />
      </div>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid #f1f5f9", padding: "28px clamp(18px,4vw,52px)", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <span style={{ fontSize: 13, color: "#94a3b8" }}>GenFrame · AI Image Adaptation · 2026</span>
        <div style={{ display: "flex", gap: 20 }}>
          {["Privacy Policy", "Terms of Service", "Contact Sales"].map(l => (
            <span key={l} style={{ fontSize: 12, color: "#94a3b8", cursor: "pointer" }}>{l}</span>
          ))}
        </div>
      </footer>
    </div>
  );
}
