"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence, useInView } from "motion/react";
import { useRouter } from "next/navigation";

const PURPLE = "#0369A1";

const VALUE_PROPS = ["4 Seconds Flat", "47+ Formats", "Zero Manual Work", "AI-Perfect Quality", "Brand-Safe Always"];

const SOCIAL_STATS = [
  { val: "10,000+", label: "Assets Generated" },
  { val: "< 5s", label: "Per Generation" },
  { val: "47+", label: "Format Presets" },
  { val: "98%", label: "Quality Rating" },
];

const PLANS = [
  {
    name: "Starter",
    price: "$29",
    period: "/month",
    desc: "For solo creators",
    features: ["200 generations/month", "All 47 formats", "Both engines", "Standard support"],
    popular: false,
    accent: "#6b7280",
  },
  {
    name: "Pro",
    price: "$79",
    period: "/month",
    desc: "For growing teams",
    features: ["Unlimited generations", "All 47 formats", "Both engines", "Priority support", "Bulk download"],
    popular: true,
    accent: PURPLE,
  },
  {
    name: "Agency",
    price: "$199",
    period: "/month",
    desc: "For creative agencies",
    features: ["Unlimited generations", "All 47 formats", "Both engines", "Dedicated support", "Custom presets", "Team seats included"],
    popular: false,
    accent: "#374151",
  },
];

function CountUp({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  useEffect(() => {
    if (!inView) return;
    const start = Date.now();
    const dur = 1800;
    const tick = () => {
      const p = Math.min((Date.now() - start) / dur, 1);
      setVal(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, target]);
  return <span ref={ref}>{val.toLocaleString()}{suffix}</span>;
}

export default function Option5() {
  const router = useRouter();
  const [propIdx, setPropIdx] = useState(0);
  const [gens, setGens] = useState(2);
  const [uploadPhase, setUploadPhase] = useState<"idle" | "loading" | "done">("idle");

  useEffect(() => {
    const t = setInterval(() => setPropIdx((i) => (i + 1) % VALUE_PROPS.length), 2200);
    return () => clearInterval(t);
  }, []);

  const tryGen = () => {
    if (gens === 0) { router.push("/pricing"); return; }
    setUploadPhase("loading");
    setTimeout(() => { setUploadPhase("done"); setGens((g) => Math.max(0, g - 1)); }, 1600);
  };

  return (
    <div style={{ background: "#06040f", minHeight: "100vh", color: "white", fontFamily: "'Inter', system-ui, sans-serif", overflowX: "hidden" }}>
      <style>{`
        @keyframes pulse-ring { 0%{transform:scale(1);opacity:0.7} 100%{transform:scale(1.6);opacity:0} }
        @keyframes glow-btn { 0%,100%{box-shadow:0 0 20px rgba(3, 105, 161,0.3)} 50%{box-shadow:0 0 40px rgba(3, 105, 161,0.6)} }
        @keyframes spin { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        @keyframes slide-up { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
        @keyframes hero-orb1 { 0%,100%{transform:translate(0,0) scale(1)} 50%{transform:translate(60px,-40px) scale(1.15)} }
        @keyframes hero-orb2 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-50px,60px)} }
        .main-cta:hover { background: linear-gradient(135deg, #7c5dc4, #9333ea) !important; transform: translateY(-3px); }
        .plan-card:hover { transform: translateY(-6px) !important; }
        .popular-plan { transform: scale(1.04) !important; }
        .popular-plan:hover { transform: scale(1.04) translateY(-6px) !important; }
      `}</style>

      {/* Animated hero background orbs */}
      <div style={{ position: "fixed", inset: 0, overflow: "hidden", pointerEvents: "none", zIndex: 0 }}>
        <div style={{ position: "absolute", width: 900, height: 900, borderRadius: "50%", background: "radial-gradient(circle, rgba(3, 105, 161,0.22) 0%, transparent 65%)", top: "-300px", left: "-200px", filter: "blur(80px)", animation: "hero-orb1 14s ease-in-out infinite" }} />
        <div style={{ position: "absolute", width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, rgba(147,51,234,0.18) 0%, transparent 65%)", bottom: "5%", right: "-100px", filter: "blur(70px)", animation: "hero-orb2 11s ease-in-out infinite" }} />
        <div style={{ position: "absolute", width: 300, height: 300, borderRadius: "50%", background: "radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 65%)", top: "35%", left: "55%", filter: "blur(60px)" }} />
      </div>

      {/* Nav */}
      <nav style={{ position: "sticky", top: 0, zIndex: 100, background: "rgba(6,4,15,0.85)", backdropFilter: "blur(24px)", borderBottom: "1px solid rgba(3, 105, 161,0.12)", padding: "0 40px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <img src="/Logo.svg" alt="" style={{ height: 26 }} onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <span style={{ fontSize: 15, fontWeight: 700, color: "white" }}>Visual Engine</span>
        </div>
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          <a onClick={() => router.push("/pricing")} style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", cursor: "pointer" }}>Pricing</a>
          <button onClick={() => router.push("/auth")} style={{ background: PURPLE, color: "white", border: "none", borderRadius: 8, padding: "9px 20px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>Sign In</button>
        </div>
      </nav>

      <div style={{ position: "relative", zIndex: 1 }}>
        {/* HERO — Big, aggressive, conversion-focused */}
        <section style={{ padding: "80px 24px 100px", textAlign: "center", position: "relative" }}>
          {/* Pulsing FREE badge */}
          <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.6, delay: 0.1 }}
            style={{ display: "inline-flex", position: "relative", marginBottom: 36 }}>
            <div style={{ position: "absolute", inset: 0, borderRadius: 100, background: "rgba(3, 105, 161,0.5)", animation: "pulse-ring 2s ease-out infinite" }} />
            <div style={{ position: "absolute", inset: 0, borderRadius: 100, background: "rgba(3, 105, 161,0.3)", animation: "pulse-ring 2s ease-out infinite 0.5s" }} />
            <div style={{ position: "relative", background: "linear-gradient(135deg, rgba(3, 105, 161,0.3), rgba(124,58,237,0.2))", border: "1px solid rgba(3, 105, 161,0.5)", borderRadius: 100, padding: "10px 28px", display: "flex", alignItems: "center", gap: 10, backdropFilter: "blur(10px)" }}>
              <span style={{ fontSize: 16 }}>🎁</span>
              <span style={{ fontSize: 14, fontWeight: 800, color: "#c4b5fd", letterSpacing: "0.04em" }}>2 FREE GENERATIONS — NO CARD</span>
              <span style={{ fontSize: 16 }}>🎁</span>
            </div>
          </motion.div>

          <motion.h1 initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.75, delay: 0.25 }}
            style={{ fontSize: "clamp(42px, 8vw, 88px)", fontWeight: 900, letterSpacing: "-0.05em", lineHeight: 0.95, marginBottom: 24, maxWidth: 900, margin: "0 auto 24px" }}>
            One Image.<br />
            <span style={{ background: "linear-gradient(135deg, #a78bfa, #0369A1)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>
              Every Format.
            </span>
          </motion.h1>

          {/* Rotating value prop */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.5 }} style={{ marginBottom: 40, height: 36, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <AnimatePresence mode="wait">
              <motion.span key={propIdx}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}
                transition={{ duration: 0.35 }}
                style={{ fontSize: 22, fontWeight: 700, color: "#c4b5fd", display: "block" }}>
                {VALUE_PROPS[propIdx]}
              </motion.span>
            </AnimatePresence>
          </motion.div>

          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }}
            style={{ fontSize: 17, color: "rgba(255,255,255,0.5)", maxWidth: 520, margin: "0 auto 52px", lineHeight: 1.65 }}>
            Upload your master creative. Visual Engine AI generates every format, for every platform, in under 5 seconds.
          </motion.p>

          {/* Upload zone in hero */}
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7, duration: 0.7 }}
            style={{ maxWidth: 580, margin: "0 auto" }}>
            <AnimatePresence mode="wait">
              {uploadPhase === "idle" && (
                <motion.div key="idle" exit={{ opacity: 0, scale: 0.97 }} transition={{ duration: 0.25 }}
                  onClick={tryGen}
                  style={{ background: "rgba(3, 105, 161,0.08)", border: "2px dashed rgba(3, 105, 161,0.4)", borderRadius: 20, padding: "44px 32px", cursor: "pointer", transition: "all 0.25s" }}
                  onMouseEnter={e => { (e.currentTarget as HTMLDivElement).style.background = "rgba(3, 105, 161,0.15)"; (e.currentTarget as HTMLDivElement).style.borderColor = "rgba(3, 105, 161,0.7)"; }}
                  onMouseLeave={e => { (e.currentTarget as HTMLDivElement).style.background = "rgba(3, 105, 161,0.08)"; (e.currentTarget as HTMLDivElement).style.borderColor = "rgba(3, 105, 161,0.4)"; }}>
                  <div style={{ fontSize: 40, marginBottom: 12 }}>⬆️</div>
                  <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>Drop image or click to upload</div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", marginBottom: 24 }}>PNG, JPG, WEBP · Max 10MB</div>
                  <button className="main-cta" style={{ background: `linear-gradient(135deg, ${PURPLE}, #7c3aed)`, color: "white", border: "none", borderRadius: 12, padding: "15px 40px", fontSize: 16, fontWeight: 700, cursor: "pointer", animation: "glow-btn 3s ease-in-out infinite", transition: "all 0.25s" }}>
                    Try Free Now — {gens} Generation{gens !== 1 ? "s" : ""} Left
                  </button>
                  <div style={{ marginTop: 14, fontSize: 12, color: "rgba(255,255,255,0.25)" }}>No signup · No card · Instant results</div>
                </motion.div>
              )}
              {uploadPhase === "loading" && (
                <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                  style={{ background: "rgba(3, 105, 161,0.08)", border: "1px solid rgba(3, 105, 161,0.3)", borderRadius: 20, padding: "52px 32px" }}>
                  <div style={{ display: "flex", justifyContent: "center", marginBottom: 20 }}>
                    <div style={{ width: 52, height: 52, borderRadius: "50%", border: `3px solid rgba(3, 105, 161,0.2)`, borderTopColor: PURPLE, animation: "spin 0.75s linear infinite" }} />
                  </div>
                  <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 6 }}>Generating your formats...</div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)" }}>AI is extending backgrounds and adapting composition</div>
                </motion.div>
              )}
              {uploadPhase === "done" && (
                <motion.div key="done" initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}
                  style={{ background: "rgba(16,185,129,0.06)", border: "2px solid rgba(16,185,129,0.3)", borderRadius: 20, padding: "36px 32px" }}>
                  <div style={{ fontSize: 32, marginBottom: 12 }}>🎉</div>
                  <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 6, color: "#34d399" }}>47 Formats Generated!</div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.5)", marginBottom: 24 }}>Generation time: 3.8s · All formats ready to download</div>
                  <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
                    <button style={{ background: "rgba(16,185,129,0.2)", color: "#34d399", border: "1px solid rgba(16,185,129,0.4)", borderRadius: 10, padding: "11px 24px", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
                      Download All (ZIP)
                    </button>
                    {gens > 0 ? (
                      <button className="main-cta" onClick={tryGen} style={{ background: `linear-gradient(135deg, ${PURPLE}, #7c3aed)`, color: "white", border: "none", borderRadius: 10, padding: "11px 24px", fontSize: 14, fontWeight: 700, cursor: "pointer", transition: "all 0.2s" }}>
                        Try Again ({gens} left)
                      </button>
                    ) : (
                      <button onClick={() => router.push("/pricing")} style={{ background: "#f59e0b", color: "white", border: "none", borderRadius: 10, padding: "11px 24px", fontSize: 14, fontWeight: 700, cursor: "pointer" }}>
                        Unlock Unlimited →
                      </button>
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </section>

        {/* Social proof bar */}
        <div style={{ background: "rgba(255,255,255,0.02)", borderTop: "1px solid rgba(255,255,255,0.05)", borderBottom: "1px solid rgba(255,255,255,0.05)", padding: "32px 24px" }}>
          <motion.div variants={{ hidden: { opacity: 0 }, visible: { opacity: 1, transition: { staggerChildren: 0.1 } } }} initial="hidden" whileInView="visible" viewport={{ once: true }}
            style={{ maxWidth: 900, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, textAlign: "center" }}>
            {SOCIAL_STATS.map((s, i) => (
              <motion.div key={i} variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5 } } }}>
                <div style={{ fontSize: 28, fontWeight: 800, color: "#c4b5fd", letterSpacing: "-0.03em" }}>{s.val}</div>
                <div style={{ fontSize: 12, color: "rgba(255,255,255,0.4)", marginTop: 5, fontWeight: 500 }}>{s.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </div>

        {/* What you get free */}
        <section style={{ padding: "80px 24px" }}>
          <div style={{ maxWidth: 900, margin: "0 auto" }}>
            <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 52 }}>
              <h2 style={{ fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 12 }}>
                What You Get <span style={{ color: "#f59e0b" }}>For Free</span>
              </h2>
              <p style={{ fontSize: 16, color: "rgba(255,255,255,0.5)" }}>Two full generations. Real AI. Real results. No hidden limits.</p>
            </motion.div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: 16 }}>
              {[
                { icon: "🖼️", title: "Full Format Library", desc: "Access all 47 presets — Instagram, LinkedIn, Billboard, App, and more" },
                { icon: "🤖", title: "Real AI Processing", desc: "The exact same AI engine paying customers use — no watermarks, no downgrades" },
                { icon: "📦", title: "Instant Download", desc: "ZIP download or individual files at full resolution, production-ready" },
                { icon: "⚡", title: "Both Engines", desc: "Creation Engine and Transformation Engine — both available on your free trial" },
              ].map((item, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1, duration: 0.55 }}
                  style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", borderRadius: 16, padding: "24px 22px" }}>
                  <div style={{ fontSize: 26, marginBottom: 12 }}>{item.icon}</div>
                  <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 8, color: "#e2e8f0" }}>{item.title}</div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.45)", lineHeight: 1.65 }}>{item.desc}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing section */}
        <section style={{ padding: "40px 24px 80px" }}>
          <div style={{ maxWidth: 1000, margin: "0 auto" }}>
            <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 52 }}>
              <h2 style={{ fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 12 }}>
                Unlock Unlimited Access
              </h2>
              <p style={{ fontSize: 16, color: "rgba(255,255,255,0.45)" }}>Used your free generations? Here's what comes next.</p>
            </motion.div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 20, alignItems: "stretch" }}>
              {PLANS.map((plan, i) => (
                <motion.div key={i}
                  initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.15, duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                  className={`plan-card ${plan.popular ? "popular-plan" : ""}`}
                  style={{
                    background: plan.popular ? `linear-gradient(135deg, ${PURPLE}22, rgba(124,58,237,0.12))` : "rgba(255,255,255,0.03)",
                    border: plan.popular ? `2px solid ${PURPLE}66` : "1px solid rgba(255,255,255,0.07)",
                    borderRadius: 20, padding: "32px 28px",
                    transition: "transform 0.3s cubic-bezier(0.22,1,0.36,1)",
                    position: "relative", cursor: "default",
                  }}>
                  {plan.popular && (
                    <div style={{ position: "absolute", top: -14, left: "50%", transform: "translateX(-50%)", background: `linear-gradient(135deg, ${PURPLE}, #7c3aed)`, borderRadius: 100, padding: "5px 18px", fontSize: 11, fontWeight: 800, color: "white", letterSpacing: "0.06em", whiteSpace: "nowrap" }}>
                      🔥 MOST POPULAR
                    </div>
                  )}
                  <div style={{ marginBottom: 6 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "rgba(255,255,255,0.5)", letterSpacing: "0.08em", textTransform: "uppercase" }}>{plan.name}</div>
                  </div>
                  <div style={{ display: "flex", alignItems: "baseline", gap: 4, marginBottom: 6 }}>
                    <span style={{ fontSize: 44, fontWeight: 800, color: plan.popular ? "#c4b5fd" : "white", letterSpacing: "-0.04em" }}>{plan.price}</span>
                    <span style={{ fontSize: 14, color: "rgba(255,255,255,0.4)" }}>{plan.period}</span>
                  </div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", marginBottom: 24, paddingBottom: 24, borderBottom: "1px solid rgba(255,255,255,0.06)" }}>{plan.desc}</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 28 }}>
                    {plan.features.map((f, j) => (
                      <div key={j} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <span style={{ color: plan.popular ? "#a78bfa" : "#10b981", fontSize: 13 }}>✓</span>
                        <span style={{ fontSize: 13, color: "rgba(255,255,255,0.65)" }}>{f}</span>
                      </div>
                    ))}
                  </div>
                  <button onClick={() => router.push("/auth")}
                    style={{ width: "100%", padding: "13px", borderRadius: 10, background: plan.popular ? `linear-gradient(135deg, ${PURPLE}, #7c3aed)` : "rgba(255,255,255,0.06)", color: plan.popular ? "white" : "rgba(255,255,255,0.7)", border: plan.popular ? "none" : "1px solid rgba(255,255,255,0.1)", fontSize: 14, fontWeight: 700, cursor: "pointer", transition: "all 0.2s", boxShadow: plan.popular ? "0 6px 20px -4px rgba(3, 105, 161,0.5)" : "none" }}>
                    Get Started →
                  </button>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Final urgency CTA */}
        <section style={{ padding: "40px 24px 100px", textAlign: "center" }}>
          <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }}
            style={{ maxWidth: 700, margin: "0 auto" }}>
            <div style={{ background: "linear-gradient(135deg, rgba(3, 105, 161,0.2), rgba(124,58,237,0.1))", border: "1px solid rgba(3, 105, 161,0.35)", borderRadius: 28, padding: "64px 40px" }}>
              <div style={{ fontSize: 52, marginBottom: 20 }}>🚀</div>
              <h2 style={{ fontSize: "clamp(28px, 4vw, 48px)", fontWeight: 800, letterSpacing: "-0.04em", marginBottom: 16, lineHeight: 1.1 }}>
                Don't Waste Your<br /><span style={{ color: "#c4b5fd" }}>Free Generations</span>
              </h2>
              <p style={{ fontSize: 16, color: "rgba(255,255,255,0.5)", maxWidth: 440, margin: "0 auto 40px", lineHeight: 1.65 }}>
                You have {gens} free generation{gens !== 1 ? "s" : ""} waiting. Upload a real image right now and see the AI adapt it for every format instantly.
              </p>
              <button className="main-cta" onClick={() => router.push(gens > 0 ? "/" : "/pricing")}
                style={{ background: `linear-gradient(135deg, ${PURPLE}, #7c3aed)`, color: "white", border: "none", borderRadius: 14, padding: "18px 48px", fontSize: 17, fontWeight: 800, cursor: "pointer", animation: "glow-btn 3s ease-in-out infinite", transition: "all 0.25s", letterSpacing: "-0.01em" }}>
                {gens > 0 ? `Use My ${gens} Free Generation${gens !== 1 ? "s" : ""} →` : "Unlock Unlimited →"}
              </button>
              <div style={{ marginTop: 20, fontSize: 12, color: "rgba(255,255,255,0.25)" }}>
                {gens > 0 ? "No account required · No credit card · Instant results" : "Starting at $29/month · Cancel anytime"}
              </div>
            </div>
          </motion.div>
        </section>

        {/* Footer */}
        <footer style={{ borderTop: "1px solid rgba(3, 105, 161,0.1)", padding: "32px 40px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
          <span style={{ fontSize: 12, color: "rgba(255,255,255,0.25)" }}>© 2026 Visual Engine. AI-Powered Creative Adaptation.</span>
          <div style={{ display: "flex", gap: 24 }}>
            {["Privacy Policy", "Terms of Service", "Contact"].map((l) => (
              <span key={l} style={{ fontSize: 12, color: "rgba(255,255,255,0.25)", cursor: "pointer" }}>{l}</span>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}
