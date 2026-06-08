"use client";

import React, { useRef } from "react";
import { motion, useInView } from "motion/react";
import { useRouter } from "next/navigation";

const PURPLE = "#0369A1";

const MARQUEE_ITEMS = [
  "Instagram Post", "Instagram Story", "LinkedIn Banner", "YouTube Thumbnail",
  "Twitter Card", "OOH Billboard", "Display Ad 300×250", "Facebook Cover",
  "Pinterest Pin", "Print A4", "App Splash Screen", "TV Display 4K",
  "Google Ads Banner", "Snap Ad", "TikTok Cover", "Email Header",
];

const FEATURES = [
  { icon: "⚡", title: "Instant Format Adaptation", desc: "Any dimension, any platform — generated in seconds" },
  { icon: "🎯", title: "Background-Aware AI", desc: "Intelligently extends backgrounds to fill new dimensions" },
  { icon: "🛡️", title: "Brand Integrity", desc: "Subjects, logos, and text always perfectly framed" },
  { icon: "📦", title: "Batch Download", desc: "All formats in one click — ZIP or individual files" },
  { icon: "📐", title: "47+ Presets", desc: "Every major ad standard and social platform covered" },
  { icon: "🔄", title: "Two Engines", desc: "Creation Engine and Transformation Engine — both included" },
];

const COMPARE_ROWS = [
  { label: "Time per format", manual: "30–60 min each", ve: "< 1 second" },
  { label: "Quality consistency", manual: "Varies by designer", ve: "Pixel-perfect, always" },
  { label: "Batch all formats", manual: "Multiple days", ve: "4 seconds total" },
  { label: "Subject preservation", manual: "Manual crop decisions", ve: "AI ensures perfect framing" },
  { label: "Brand compliance", manual: "Checklist required", ve: "Built-in by design" },
  { label: "Cost per format", manual: "$15–50 designer time", ve: "< $0.01" },
];

function ProductMockup({ label, subtitle, accentColor }: { label: string; subtitle: string; accentColor: string }) {
  return (
    <div style={{ background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 16, overflow: "hidden", boxShadow: "0 20px 60px -20px rgba(0,0,0,0.12)" }}>
      {/* Mock browser bar */}
      <div style={{ background: "white", borderBottom: "1px solid #e5e7eb", padding: "12px 16px", display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ display: "flex", gap: 5 }}>
          {["#ef4444", "#f59e0b", "#10b981"].map((c) => (
            <div key={c} style={{ width: 10, height: 10, borderRadius: "50%", background: c }} />
          ))}
        </div>
        <div style={{ flex: 1, height: 24, background: "#f3f4f6", borderRadius: 6, marginLeft: 8, display: "flex", alignItems: "center", paddingLeft: 10 }}>
          <span style={{ fontSize: 11, color: "#9ca3af" }}>visualengine.ai/{label.toLowerCase().replace(" ", "-")}</span>
        </div>
      </div>
      {/* Mock content */}
      <div style={{ padding: 24, background: `linear-gradient(135deg, ${accentColor}06, white)` }}>
        <div style={{ height: 16, background: "#e5e7eb", borderRadius: 8, width: "60%", marginBottom: 12 }} />
        <div style={{ height: 10, background: "#f3f4f6", borderRadius: 6, width: "90%", marginBottom: 8 }} />
        <div style={{ height: 10, background: "#f3f4f6", borderRadius: 6, width: "75%", marginBottom: 24 }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
          {[80, 50, 100, 60, 80, 50].map((h, i) => (
            <div key={i} style={{ height: h, background: `linear-gradient(135deg, ${accentColor}22, ${accentColor}0a)`, borderRadius: 8, border: `1px solid ${accentColor}22` }} />
          ))}
        </div>
        <div style={{ marginTop: 16, padding: "10px 16px", background: accentColor, borderRadius: 8, display: "inline-flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 12, color: "white", fontWeight: 600 }}>{subtitle}</span>
        </div>
      </div>
    </div>
  );
}

export default function Option4() {
  const router = useRouter();

  return (
    <div style={{ background: "white", minHeight: "100vh", fontFamily: "'Inter', system-ui, sans-serif", color: "#111827" }}>
      <style>{`
        @keyframes marquee-scroll { from { transform: translateX(0); } to { transform: translateX(-50%); } }
        @keyframes float-up { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-12px)} }
        .cta-primary:hover { background: #5030a0 !important; transform: translateY(-2px); box-shadow: 0 12px 32px -6px rgba(3, 105, 161,0.4) !important; }
        .cta-secondary:hover { border-color: ${PURPLE} !important; color: ${PURPLE} !important; }
        .feature-cell:hover { background: #f5f0ff !important; border-color: ${PURPLE}44 !important; transform: translateY(-3px); }
      `}</style>

      {/* Minimal Nav */}
      <nav style={{ position: "sticky", top: 0, zIndex: 100, background: "rgba(255,255,255,0.9)", backdropFilter: "blur(20px)", borderBottom: "1px solid #f3f4f6", padding: "0 48px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <img src="/Logo.svg" alt="" style={{ height: 24 }} onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <span style={{ fontSize: 16, fontWeight: 700, color: "#111827", letterSpacing: "-0.02em" }}>Visual Engine</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
          <a onClick={() => router.push("/pricing")} style={{ fontSize: 14, color: "#6b7280", cursor: "pointer", textDecoration: "none", fontWeight: 500 }}>Pricing</a>
          <a style={{ fontSize: 14, color: "#6b7280", cursor: "pointer", fontWeight: 500 }}>Features</a>
          <button className="cta-primary" onClick={() => router.push("/auth")} style={{ background: PURPLE, color: "white", border: "none", borderRadius: 8, padding: "9px 22px", fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all 0.2s" }}>
            Try Free
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section style={{ padding: "100px 48px 80px", maxWidth: 1200, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 80, alignItems: "center" }}>
        <motion.div initial={{ opacity: 0, x: -40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: `${PURPLE}0d`, border: `1px solid ${PURPLE}22`, borderRadius: 100, padding: "5px 14px", marginBottom: 28 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: PURPLE, display: "inline-block" }} />
            <span style={{ fontSize: 11, fontWeight: 700, color: PURPLE, letterSpacing: "0.08em" }}>AI-POWERED · NO CARD NEEDED</span>
          </div>
          <h1 style={{ fontSize: "clamp(38px, 5vw, 60px)", fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1.05, marginBottom: 20, color: "#111827" }}>
            Every format.<br />
            <span style={{ color: PURPLE }}>One upload.</span>
          </h1>
          <p style={{ fontSize: 17, color: "#6b7280", lineHeight: 1.7, marginBottom: 36, maxWidth: 440 }}>
            AI-native image adaptation for creative teams. Upload your master image and get production-ready assets in every format, in seconds.
          </p>
          <div style={{ display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <button className="cta-primary" onClick={() => router.push("/auth")}
              style={{ background: PURPLE, color: "white", border: "none", borderRadius: 10, padding: "14px 32px", fontSize: 14, fontWeight: 700, cursor: "pointer", transition: "all 0.2s", boxShadow: "0 6px 20px -4px rgba(3, 105, 161,0.35)" }}>
              Try Free — 2 Generations →
            </button>
            <button className="cta-secondary" onClick={() => router.push("/pricing")}
              style={{ background: "transparent", color: "#374151", border: "1px solid #e5e7eb", borderRadius: 10, padding: "14px 28px", fontSize: 14, fontWeight: 600, cursor: "pointer", transition: "all 0.2s" }}>
              See Pricing
            </button>
          </div>
          <div style={{ marginTop: 20, fontSize: 12, color: "#9ca3af" }}>
            No signup required for first 2 generations
          </div>
        </motion.div>

        {/* Floating mockup */}
        <motion.div initial={{ opacity: 0, x: 40 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          style={{ animation: "float-up 7s ease-in-out infinite" }}>
          <div style={{ position: "relative" }}>
            {/* Main mockup */}
            <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: 20, overflow: "hidden", boxShadow: "0 30px 80px -20px rgba(0,0,0,0.15)" }}>
              <div style={{ background: "#f9fafb", borderBottom: "1px solid #e5e7eb", padding: "14px 20px", display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ display: "flex", gap: 5 }}>
                  {["#ef4444", "#f59e0b", "#10b981"].map((c) => (
                    <div key={c} style={{ width: 10, height: 10, borderRadius: "50%", background: c }} />
                  ))}
                </div>
                <div style={{ flex: 1, height: 22, background: "#e5e7eb", borderRadius: 5, marginLeft: 8 }} />
              </div>
              <div style={{ padding: 28 }}>
                <div style={{ marginBottom: 20 }}>
                  <div style={{ height: 14, background: "#f3f4f6", borderRadius: 6, width: "50%", marginBottom: 10 }} />
                  <div style={{ height: 200, background: `linear-gradient(135deg, ${PURPLE}15, ${PURPLE}05)`, borderRadius: 12, border: `2px dashed ${PURPLE}22`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <div style={{ textAlign: "center" }}>
                      <div style={{ fontSize: 32, marginBottom: 8 }}>🖼️</div>
                      <div style={{ fontSize: 13, color: "#9ca3af" }}>Master image uploaded</div>
                    </div>
                  </div>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
                  {[[60, 60], [36, 64], [80, 45], [48, 64]].map(([w, h], i) => (
                    <div key={i} style={{ height: 72, background: `linear-gradient(135deg, ${PURPLE}22, ${PURPLE}0a)`, borderRadius: 8, border: `1px solid ${PURPLE}22`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <div style={{ width: `${w}%`, height: `${h}%`, background: `${PURPLE}33`, borderRadius: 3 }} />
                    </div>
                  ))}
                </div>
              </div>
            </div>
            {/* Floating badge */}
            <div style={{ position: "absolute", bottom: -16, right: -16, background: "white", border: `2px solid ${PURPLE}33`, borderRadius: 12, padding: "12px 16px", boxShadow: "0 8px 24px -8px rgba(3, 105, 161,0.2)", display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontSize: 16 }}>⚡</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 700, color: "#111827" }}>3.8s</div>
                <div style={{ fontSize: 10, color: "#6b7280" }}>generation time</div>
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Marquee strip */}
      <div style={{ background: "#f9fafb", borderTop: "1px solid #e5e7eb", borderBottom: "1px solid #e5e7eb", padding: "16px 0", overflow: "hidden" }}>
        <div style={{ display: "flex", animation: "marquee-scroll 25s linear infinite", width: "max-content" }}>
          {[...MARQUEE_ITEMS, ...MARQUEE_ITEMS].map((item, i) => (
            <span key={i} style={{ display: "inline-flex", alignItems: "center", gap: 16, padding: "0 28px", fontSize: 13, fontWeight: 600, color: "#6b7280", whiteSpace: "nowrap" }}>
              {item}
              <span style={{ width: 4, height: 4, borderRadius: "50%", background: PURPLE, display: "inline-block", opacity: 0.4 }} />
            </span>
          ))}
        </div>
      </div>

      {/* Product screenshots */}
      <section style={{ padding: "100px 48px", maxWidth: 1200, margin: "0 auto" }}>
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 64 }}>
          <h2 style={{ fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 12 }}>Built for Professional Teams</h2>
          <p style={{ fontSize: 16, color: "#6b7280", maxWidth: 480, margin: "0 auto" }}>Two powerful engines. One seamless workflow. Zero manual resizing.</p>
        </motion.div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: 32 }}>
          {[
            { label: "Transformation Engine", subtitle: "Adapt any image →", color: PURPLE },
            { label: "Creation Engine", subtitle: "Generate from scratch →", color: "#7c3aed" },
            { label: "Format Library", subtitle: "47+ presets ready →", color: "#0369A1" },
          ].map((item, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.65, delay: i * 0.15, ease: [0.22, 1, 0.36, 1] }}>
              <ProductMockup {...item} accentColor={item.color} />
            </motion.div>
          ))}
        </div>
      </section>

      {/* Feature grid */}
      <section style={{ padding: "60px 48px 100px", background: "#f9fafb", borderTop: "1px solid #e5e7eb" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 56 }}>
            <h2 style={{ fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.03em" }}>Everything You Need</h2>
          </motion.div>
          <motion.div
            variants={{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.08 } } }}
            initial="hidden" whileInView="visible" viewport={{ once: true }}
            style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
            {FEATURES.map((f, i) => (
              <motion.div key={i} variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }}
                className="feature-cell"
                style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: 14, padding: "24px 22px", display: "flex", gap: 16, alignItems: "flex-start", cursor: "default", transition: "all 0.25s cubic-bezier(0.22,1,0.36,1)" }}>
                <div style={{ fontSize: 22, flexShrink: 0 }}>{f.icon}</div>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "#111827", marginBottom: 5 }}>{f.title}</div>
                  <div style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.6 }}>{f.desc}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Comparison table */}
      <section style={{ padding: "80px 48px", maxWidth: 900, margin: "0 auto" }}>
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 48 }}>
          <h2 style={{ fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.03em" }}>Manual Workflow vs Visual Engine</h2>
        </motion.div>
        <div style={{ border: "1px solid #e5e7eb", borderRadius: 16, overflow: "hidden" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", background: "#f9fafb", padding: "14px 24px", borderBottom: "1px solid #e5e7eb" }}>
            <span style={{ fontSize: 12, fontWeight: 700, color: "#374151", letterSpacing: "0.06em", textTransform: "uppercase" }}>Metric</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: "#ef4444", letterSpacing: "0.06em", textTransform: "uppercase" }}>Manual</span>
            <span style={{ fontSize: 12, fontWeight: 700, color: PURPLE, letterSpacing: "0.06em", textTransform: "uppercase" }}>Visual Engine</span>
          </div>
          {COMPARE_ROWS.map((row, i) => (
            <motion.div key={i}
              initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.45, delay: i * 0.08 }}
              style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", padding: "16px 24px", borderBottom: i < COMPARE_ROWS.length - 1 ? "1px solid #f3f4f6" : "none", background: i % 2 === 0 ? "white" : "#fafafa", alignItems: "center" }}>
              <span style={{ fontSize: 13, fontWeight: 600, color: "#374151" }}>{row.label}</span>
              <span style={{ fontSize: 13, color: "#ef4444", fontWeight: 500 }}>✗ {row.manual}</span>
              <span style={{ fontSize: 13, color: "#10b981", fontWeight: 600 }}>✓ {row.ve}</span>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Clean CTA */}
      <section style={{ padding: "60px 48px 100px", textAlign: "center" }}>
        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.7 }} style={{ maxWidth: 560, margin: "0 auto" }}>
          <h2 style={{ fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: 16 }}>
            See it in under 10 seconds.
          </h2>
          <p style={{ fontSize: 16, color: "#6b7280", marginBottom: 36, lineHeight: 1.6 }}>
            Two free generations. No account. No card. Upload your image and watch the AI work.
          </p>
          <button className="cta-primary" onClick={() => router.push("/auth")}
            style={{ background: PURPLE, color: "white", border: "none", borderRadius: 12, padding: "16px 44px", fontSize: 16, fontWeight: 700, cursor: "pointer", transition: "all 0.2s", boxShadow: "0 8px 28px -6px rgba(3, 105, 161,0.4)", marginBottom: 16 }}>
            Start Free →
          </button>
          <div style={{ fontSize: 12, color: "#d1d5db" }}>Then from $29/month · Cancel anytime</div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid #e5e7eb", padding: "32px 48px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <img src="/Logo.svg" alt="" style={{ height: 20 }} onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <span style={{ fontSize: 13, color: "#9ca3af" }}>Visual Engine · AI Creative Adaptation · 2026</span>
        </div>
        <div style={{ display: "flex", gap: 24 }}>
          {["Privacy Policy", "Terms", "Contact"].map((l) => (
            <span key={l} style={{ fontSize: 12, color: "#9ca3af", cursor: "pointer" }}>{l}</span>
          ))}
        </div>
      </footer>
    </div>
  );
}
