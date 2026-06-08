"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence, useInView } from "motion/react";
import { useRouter } from "next/navigation";

const PURPLE = "#0369A1";

const FORMATS = [
  { name: "Instagram Post", dims: "1080×1080", ratio: "1:1", w: 110, h: 110, color: "#e1306c" },
  { name: "Instagram Story", dims: "1080×1920", ratio: "9:16", w: 66, h: 118, color: "#833ab4" },
  { name: "LinkedIn Banner", dims: "1584×396", ratio: "4:1", w: 160, h: 40, color: "#0077b5" },
  { name: "YouTube Thumb", dims: "1280×720", ratio: "16:9", w: 160, h: 90, color: "#ff0000" },
  { name: "Twitter Card", dims: "1200×628", ratio: "2:1", w: 150, h: 78, color: "#1da1f2" },
  { name: "OOH Billboard", dims: "14400×4800", ratio: "3:1", w: 155, h: 52, color: "#f59e0b" },
  { name: "Display Ad", dims: "300×250", ratio: "6:5", w: 110, h: 92, color: "#10b981" },
  { name: "Pinterest Pin", dims: "1000×1500", ratio: "2:3", w: 90, h: 135, color: "#e60023" },
  { name: "Facebook Cover", dims: "851×315", ratio: "8:3", w: 156, h: 58, color: "#1877f2" },
];

function FormatCard({ fmt, index }: { fmt: typeof FORMATS[0]; index: number }) {
  const [hovered, setHovered] = useState(false);
  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, delay: index * 0.07, ease: [0.22, 1, 0.36, 1] }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ background: hovered ? "#f0ebff" : "white", border: `2px solid ${hovered ? PURPLE : "#e5e7eb"}`, borderRadius: 14, padding: "18px 16px", display: "flex", flexDirection: "column", alignItems: "center", gap: 12, cursor: "default", transition: "all 0.25s cubic-bezier(0.22,1,0.36,1)", boxShadow: hovered ? "0 12px 28px -8px rgba(3, 105, 161,0.2)" : "0 2px 8px rgba(0,0,0,0.04)", transform: hovered ? "translateY(-4px)" : "translateY(0)" }}>
      {/* Format preview */}
      <div style={{ position: "relative", width: 170, height: 140, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: fmt.w, height: fmt.h, borderRadius: 6, background: `linear-gradient(135deg, ${fmt.color}22, ${fmt.color}44)`, border: `2px solid ${fmt.color}66`, position: "relative", overflow: "hidden", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: "60%", height: "60%", borderRadius: 4, background: `${fmt.color}44` }} />
          {hovered && (
            <div style={{ position: "absolute", inset: 0, background: `${PURPLE}11`, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ fontSize: 18 }}>✓</span>
            </div>
          )}
        </div>
      </div>
      <div style={{ textAlign: "center" }}>
        <div style={{ fontSize: 12, fontWeight: 700, color: "#111827", marginBottom: 3 }}>{fmt.name}</div>
        <div style={{ fontSize: 11, color: "#9ca3af", marginBottom: 4 }}>{fmt.dims}</div>
        <div style={{ display: "inline-block", background: `${PURPLE}11`, border: `1px solid ${PURPLE}22`, borderRadius: 100, padding: "2px 8px", fontSize: 10, fontWeight: 700, color: PURPLE }}>{fmt.ratio}</div>
      </div>
    </motion.div>
  );
}

function Counter({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true });
  useEffect(() => {
    if (!inView) return;
    const start = Date.now();
    const dur = 1600;
    const tick = () => {
      const p = Math.min((Date.now() - start) / dur, 1);
      setVal(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, target]);
  return <div ref={ref} style={{ fontSize: 52, fontWeight: 800, color: PURPLE, letterSpacing: "-0.04em", lineHeight: 1 }}>{val.toLocaleString()}{suffix}</div>;
}

export default function Option2() {
  const router = useRouter();
  const [gens, setGens] = useState(2);
  const [phase, setPhase] = useState<"idle" | "uploading" | "done">("idle");
  const [isDragOver, setIsDragOver] = useState(false);

  const simulate = () => {
    if (gens === 0) { router.push("/pricing"); return; }
    setPhase("uploading");
    setTimeout(() => {
      setPhase("done");
      setGens((g) => Math.max(0, g - 1));
    }, 1800);
  };

  return (
    <div style={{ background: "#f9fafb", minHeight: "100vh", fontFamily: "'Inter', system-ui, sans-serif", color: "#111827" }}>
      <style>{`
        @keyframes dash { to { stroke-dashoffset: 0; } }
        @keyframes spin-ring { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes shimmer { from { background-position: -200% 0; } to { background-position: 200% 0; } }
        .skel { background: linear-gradient(90deg, #e5e7eb 25%, #f3f4f6 50%, #e5e7eb 75%); background-size: 200% 100%; animation: shimmer 1.4s infinite; border-radius: 8px; }
        .upload-zone:hover { border-color: ${PURPLE} !important; background: #f5f0ff !important; }
        .try-btn:hover { background: #5030a0 !important; transform: translateY(-2px); box-shadow: 0 10px 24px -6px rgba(3, 105, 161,0.4) !important; }
      `}</style>

      {/* Sticky Generation Bar */}
      <div style={{ position: "sticky", top: 0, zIndex: 200, background: gens === 0 ? "#fef3c7" : "#f0ebff", borderBottom: `2px solid ${gens === 0 ? "#f59e0b" : PURPLE}`, padding: "10px 24px", display: "flex", alignItems: "center", justifyContent: "center", gap: 16 }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: gens === 0 ? "#92400e" : PURPLE }}>
          {gens === 0 ? "🔒 You've used all free generations" : `🎁 Free Generations Remaining:`}
        </span>
        {gens > 0 && (
          <div style={{ display: "flex", gap: 6 }}>
            {[0, 1].map((i) => (
              <div key={i} style={{ width: 24, height: 24, borderRadius: "50%", background: i < gens ? PURPLE : "#d1d5db", border: `2px solid ${i < gens ? PURPLE : "#9ca3af"}`, transition: "all 0.3s" }} />
            ))}
          </div>
        )}
        {gens === 0 && (
          <button onClick={() => router.push("/pricing")} style={{ background: "#f59e0b", color: "white", border: "none", borderRadius: 8, padding: "6px 18px", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
            Unlock Unlimited →
          </button>
        )}
      </div>

      {/* Nav */}
      <nav style={{ background: "white", borderBottom: "1px solid #e5e7eb", padding: "0 40px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <img src="/Logo.svg" alt="" style={{ height: 26 }} onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <div>
            <div style={{ fontSize: 8, fontWeight: 600, color: "rgba(3, 105, 161,0.7)", letterSpacing: "0.08em", textTransform: "uppercase" }}>presents</div>
            <div style={{ fontSize: 15, fontWeight: 700, color: "#111827", letterSpacing: "-0.02em" }}>Visual Engine</div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <a onClick={() => router.push("/pricing")} style={{ fontSize: 13, color: "#6b7280", cursor: "pointer" }}>Pricing</a>
          <button onClick={() => router.push("/auth")} style={{ background: PURPLE, color: "white", border: "none", borderRadius: 9, padding: "9px 22px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>Sign In</button>
        </div>
      </nav>

      {/* Hero + Upload Zone */}
      <section style={{ padding: "80px 24px 60px", textAlign: "center" }}>
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }} style={{ maxWidth: 700, margin: "0 auto" }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: `${PURPLE}11`, border: `1px solid ${PURPLE}22`, borderRadius: 100, padding: "5px 14px", marginBottom: 24 }}>
            <span style={{ fontSize: 11, fontWeight: 700, color: PURPLE, letterSpacing: "0.08em" }}>AI-POWERED FORMAT ADAPTATION</span>
          </div>
          <h1 style={{ fontSize: "clamp(36px, 6vw, 64px)", fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1.05, marginBottom: 18 }}>
            Drop an Image.<br />
            <span style={{ color: PURPLE }}>Get Every Format.</span>
          </h1>
          <p style={{ fontSize: 17, color: "#6b7280", maxWidth: 520, margin: "0 auto 48px", lineHeight: 1.65 }}>
            No sign-up. No credit card. Upload your master image and download production-ready assets for every platform — in seconds.
          </p>
        </motion.div>

        {/* Upload Zone */}
        <motion.div initial={{ opacity: 0, y: 40, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.7, delay: 0.25 }}
          style={{ maxWidth: 680, margin: "0 auto" }}>
          <AnimatePresence mode="wait">
            {phase === "idle" && (
              <motion.div key="idle" exit={{ opacity: 0, scale: 0.95 }} transition={{ duration: 0.3 }}>
                <div
                  className="upload-zone"
                  onClick={simulate}
                  onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
                  onDragLeave={() => setIsDragOver(false)}
                  onDrop={(e) => { e.preventDefault(); setIsDragOver(false); simulate(); }}
                  style={{
                    border: `2px dashed ${isDragOver ? PURPLE : "#d1d5db"}`,
                    borderRadius: 24,
                    padding: "64px 40px",
                    background: isDragOver ? "#f0ebff" : "white",
                    cursor: "pointer",
                    transition: "all 0.25s",
                    position: "relative",
                    overflow: "hidden",
                  }}>
                  <div style={{ fontSize: 48, marginBottom: 16 }}>🖼️</div>
                  <div style={{ fontSize: 20, fontWeight: 700, color: "#111827", marginBottom: 8 }}>Drop your master image here</div>
                  <div style={{ fontSize: 14, color: "#9ca3af", marginBottom: 28 }}>or click to browse · PNG, JPG, WEBP up to 10MB</div>
                  <button className="try-btn" style={{ background: PURPLE, color: "white", border: "none", borderRadius: 10, padding: "14px 36px", fontSize: 15, fontWeight: 700, cursor: "pointer", transition: "all 0.2s", boxShadow: "0 6px 20px -4px rgba(3, 105, 161,0.4)" }}>
                    Try Now — {gens} Free Generation{gens !== 1 ? "s" : ""} Left
                  </button>
                  <div style={{ marginTop: 14, fontSize: 12, color: "#d1d5db" }}>No account required</div>
                </div>
              </motion.div>
            )}

            {phase === "uploading" && (
              <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: 24, padding: "48px 40px" }}>
                <div style={{ display: "flex", justifyContent: "center", marginBottom: 24 }}>
                  <div style={{ width: 60, height: 60, borderRadius: "50%", border: `4px solid ${PURPLE}22`, borderTopColor: PURPLE, animation: "spin-ring 0.8s linear infinite" }} />
                </div>
                <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8 }}>AI is adapting your image...</div>
                <div style={{ fontSize: 14, color: "#9ca3af", marginBottom: 32 }}>Analyzing composition · Extending backgrounds · Generating formats</div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                  {[140, 100, 160, 80, 120, 90].map((w, i) => (
                    <div key={i} className="skel" style={{ height: w }} />
                  ))}
                </div>
              </motion.div>
            )}

            {phase === "done" && (
              <motion.div key="done" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
                style={{ background: "white", border: `2px solid ${PURPLE}33`, borderRadius: 24, padding: "36px 32px" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24, flexWrap: "wrap", gap: 12 }}>
                  <div>
                    <div style={{ fontSize: 18, fontWeight: 700, color: "#111827" }}>✅ 9 Formats Generated</div>
                    <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>All formats ready to download · Generation took 3.8s</div>
                  </div>
                  <div style={{ display: "flex", gap: 10 }}>
                    <button style={{ background: "#f3f4f6", color: "#374151", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
                      Download All (ZIP)
                    </button>
                    {gens > 0 && (
                      <button className="try-btn" onClick={simulate} style={{ background: PURPLE, color: "white", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all 0.2s" }}>
                        Try Another ({gens} left)
                      </button>
                    )}
                    {gens === 0 && (
                      <button onClick={() => router.push("/pricing")} style={{ background: "#f59e0b", color: "white", border: "none", borderRadius: 8, padding: "10px 20px", fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                        Unlock Unlimited →
                      </button>
                    )}
                  </div>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
                  {FORMATS.map((fmt, i) => <FormatCard key={i} fmt={fmt} index={i} />)}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </section>

      {/* Speed benchmark */}
      <section style={{ background: "white", padding: "80px 24px", borderTop: "1px solid #f3f4f6" }}>
        <div style={{ maxWidth: 900, margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 56 }}>
            <h2 style={{ fontSize: "clamp(26px, 4vw, 40px)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 12 }}>Faster Than You Can Think of a Format</h2>
            <p style={{ fontSize: 16, color: "#6b7280" }}>Compare the old way vs the Visual Engine way.</p>
          </motion.div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
            {[
              { label: "Manual workflow", time: "3–4 hours", color: "#ef4444", pct: 100 },
              { label: "Visual Engine", time: "< 5 seconds", color: PURPLE, pct: 0.3 },
            ].map((item, i) => (
              <motion.div key={i} initial={{ opacity: 0, x: i === 0 ? -30 : 30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.6, delay: i * 0.2 }}
                style={{ background: "#f9fafb", border: "1px solid #e5e7eb", borderRadius: 16, padding: "28px 24px" }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#374151", marginBottom: 12 }}>{item.label}</div>
                <div style={{ fontSize: 32, fontWeight: 800, color: item.color, marginBottom: 20 }}>{item.time}</div>
                <div style={{ height: 8, background: "#e5e7eb", borderRadius: 4, overflow: "hidden" }}>
                  <motion.div initial={{ width: 0 }} whileInView={{ width: `${item.pct}%` }} viewport={{ once: true }} transition={{ duration: 1.2, delay: 0.3, ease: "easeOut" }}
                    style={{ height: "100%", background: item.color, borderRadius: 4, minWidth: item.pct < 1 ? 6 : 0 }} />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Social proof numbers */}
      <section style={{ padding: "80px 24px", background: "#f9fafb" }}>
        <motion.div variants={{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.15 } } }} initial="hidden" whileInView="visible" viewport={{ once: true }}
          style={{ maxWidth: 900, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 32, textAlign: "center" }}>
          {[{ target: 47, suffix: "+", label: "Supported Formats" }, { target: 98, suffix: "%", label: "Accuracy Rate" }, { target: 12, suffix: "K+", label: "Assets Generated" }].map((s, i) => (
            <motion.div key={i} variants={{ hidden: { opacity: 0, y: 30 }, visible: { opacity: 1, y: 0, transition: { duration: 0.6 } } }}>
              <Counter target={s.target} suffix={s.suffix} />
              <div style={{ fontSize: 14, color: "#6b7280", marginTop: 8, fontWeight: 500 }}>{s.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Paywall prompt */}
      {gens === 0 && (
        <motion.section initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}
          style={{ padding: "80px 24px", background: `linear-gradient(135deg, ${PURPLE}11, ${PURPLE}05)`, borderTop: `1px solid ${PURPLE}22` }}>
          <div style={{ maxWidth: 640, margin: "0 auto", textAlign: "center" }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>🚀</div>
            <h2 style={{ fontSize: 36, fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 16 }}>
              You've Seen What It Can Do.
            </h2>
            <p style={{ fontSize: 16, color: "#4b5563", maxWidth: 480, margin: "0 auto 36px", lineHeight: 1.65 }}>
              You've used your 2 free generations. Ready to adapt every creative, every campaign, every time?
            </p>
            <button onClick={() => router.push("/pricing")} style={{ background: PURPLE, color: "white", border: "none", borderRadius: 12, padding: "16px 44px", fontSize: 16, fontWeight: 700, cursor: "pointer", boxShadow: "0 8px 28px -6px rgba(3, 105, 161,0.4)" }}>
              See Pricing Plans →
            </button>
            <div style={{ marginTop: 16, fontSize: 13, color: "#9ca3af" }}>Starting at $29/month · Cancel anytime</div>
          </div>
        </motion.section>
      )}

      {/* Footer */}
      <footer style={{ borderTop: "1px solid #e5e7eb", padding: "32px 40px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16, background: "white" }}>
        <span style={{ fontSize: 12, color: "#9ca3af" }}>© 2026 Visual Engine. AI-Powered Creative Adaptation.</span>
        <div style={{ display: "flex", gap: 24 }}>
          {["Privacy Policy", "Terms of Service", "Contact"].map((l) => (
            <span key={l} style={{ fontSize: 12, color: "#9ca3af", cursor: "pointer" }}>{l}</span>
          ))}
        </div>
      </footer>
    </div>
  );
}
