"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, useInView } from "motion/react";
import { useRouter } from "next/navigation";

const PURPLE = "#0369A1";
const DARK = "#070711";

function Counter({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  useEffect(() => {
    if (!inView) return;
    const start = Date.now();
    const dur = 1800;
    const tick = () => {
      const p = Math.min((Date.now() - start) / dur, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, target]);
  return <span ref={ref}>{val.toLocaleString()}{suffix}</span>;
}

function BeforeAfterSlider() {
  const [pos, setPos] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const move = (clientX: number) => {
    if (!dragging.current || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    setPos(Math.max(5, Math.min(95, ((clientX - rect.left) / rect.width) * 100)));
  };

  return (
    <div
      ref={containerRef}
      style={{ position: "relative", width: "100%", height: 380, borderRadius: 20, overflow: "hidden", cursor: "ew-resize", userSelect: "none", border: "1px solid rgba(3, 105, 161,0.3)" }}
      onPointerDown={() => { dragging.current = true; }}
      onPointerUp={() => { dragging.current = false; }}
      onPointerLeave={() => { dragging.current = false; }}
      onPointerMove={(e) => move(e.clientX)}
    >
      {/* AFTER side — full container (good result) */}
      <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, #0d0a22 0%, #1a0e3a 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center", pointerEvents: "none" }}>
          <div style={{ display: "flex", gap: 12, justifyContent: "center", marginBottom: 24 }}>
            {[{ w: 120, h: 120, label: "1:1" }, { w: 68, h: 120, label: "9:16" }, { w: 160, h: 90, label: "16:9" }].map((f, i) => (
              <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
                <div style={{ width: f.w, height: f.h, borderRadius: 8, background: "linear-gradient(135deg, #0369A144, #a78bfa22)", border: "2px solid #0369A188", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <div style={{ width: "70%", height: "70%", background: "linear-gradient(135deg, #0369A166, #7c3aed44)", borderRadius: 4 }} />
                </div>
                <span style={{ fontSize: 10, color: "#a78bfa", fontWeight: 600 }}>{f.label}</span>
              </div>
            ))}
          </div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "rgba(16,185,129,0.15)", border: "1px solid rgba(16,185,129,0.4)", borderRadius: 100, padding: "5px 14px" }}>
            <span style={{ fontSize: 14 }}>✓</span>
            <span style={{ fontSize: 12, color: "#10b981", fontWeight: 600 }}>AI Perfectly Adapted</span>
          </div>
        </div>
      </div>

      {/* BEFORE side — overlay (bad result), covers left portion */}
      <div style={{ position: "absolute", inset: 0, clipPath: `inset(0 ${100 - pos}% 0 0)`, background: "linear-gradient(135deg, #1a0505 0%, #2d0a0a 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center", pointerEvents: "none" }}>
          <div style={{ position: "relative", width: 200, height: 200, margin: "0 auto 24px", borderRadius: 8, background: "linear-gradient(135deg, #3d1515, #5a1f1f)", border: "2px solid rgba(239,68,68,0.6)", overflow: "hidden" }}>
            <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, #ef444422, transparent)" }} />
            <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", background: "#2a0a0a", padding: "6px 12px", borderRadius: 6, whiteSpace: "nowrap" }}>
              <span style={{ fontSize: 11, color: "#ef4444", fontWeight: 700 }}>⚠ FORCED CROP</span>
            </div>
            <div style={{ position: "absolute", top: 8, left: 8, background: "rgba(239,68,68,0.2)", border: "1px solid rgba(239,68,68,0.5)", borderRadius: 4, padding: "2px 6px" }}>
              <span style={{ fontSize: 10, color: "#ef4444" }}>Subject Cut Off</span>
            </div>
          </div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 100, padding: "5px 14px" }}>
            <span style={{ fontSize: 12, color: "#ef4444", fontWeight: 600 }}>✗ Manual Resize Fail</span>
          </div>
        </div>
      </div>

      {/* Divider handle */}
      <div style={{ position: "absolute", top: 0, bottom: 0, left: `${pos}%`, width: 3, background: "white", transform: "translateX(-50%)", zIndex: 10, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ width: 40, height: 40, borderRadius: "50%", background: "white", boxShadow: "0 4px 20px rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", gap: 4 }}>
          <span style={{ color: "#374151", fontSize: 14, fontWeight: 700 }}>‹›</span>
        </div>
      </div>

      {/* Labels */}
      <div style={{ position: "absolute", top: 16, left: 16, background: "rgba(239,68,68,0.9)", borderRadius: 6, padding: "4px 10px", fontSize: 11, fontWeight: 700, color: "white", zIndex: 5 }}>BEFORE</div>
      <div style={{ position: "absolute", top: 16, right: 16, background: "rgba(3, 105, 161,0.9)", borderRadius: 6, padding: "4px 10px", fontSize: 11, fontWeight: 700, color: "white", zIndex: 5 }}>AFTER</div>
    </div>
  );
}

const stagger = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.12 } },
};
const fadeUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] } },
};
const fadeLeft = {
  hidden: { opacity: 0, x: -60 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] } },
};
const fadeRight = {
  hidden: { opacity: 0, x: 60 },
  visible: { opacity: 1, x: 0, transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] } },
};

export default function Option1() {
  const router = useRouter();

  return (
    <div style={{ background: DARK, minHeight: "100vh", color: "white", fontFamily: "'Inter', system-ui, sans-serif", overflowX: "hidden" }}>
      <style>{`
        @keyframes orb1 { 0%,100%{transform:translate(0,0) scale(1)} 50%{transform:translate(40px,-40px) scale(1.1)} }
        @keyframes orb2 { 0%,100%{transform:translate(0,0) scale(1)} 50%{transform:translate(-30px,50px) scale(0.95)} }
        @keyframes orb3 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(20px,-60px)} }
        @keyframes drawLine { from{width:0} to{width:100%} }
        @keyframes badge-float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-6px)} }
        .opt1-btn:hover { background: #7c5dc4 !important; transform: translateY(-2px); box-shadow: 0 12px 28px -6px rgba(3, 105, 161,0.5) !important; }
        .problem-card:hover { border-color: rgba(239,68,68,0.5) !important; transform: translateY(-4px); box-shadow: 0 16px 32px -10px rgba(239,68,68,0.2) !important; }
        .solution-card:hover { border-color: rgba(3, 105, 161,0.6) !important; transform: translateY(-4px); box-shadow: 0 16px 32px -10px rgba(3, 105, 161,0.35) !important; }
      `}</style>

      {/* Animated background orbs */}
      <div style={{ position: "fixed", inset: 0, overflow: "hidden", pointerEvents: "none", zIndex: 0 }}>
        <div style={{ position: "absolute", width: 700, height: 700, borderRadius: "50%", background: "radial-gradient(circle, rgba(3, 105, 161,0.18) 0%, transparent 70%)", top: "-200px", left: "-150px", filter: "blur(60px)", animation: "orb1 12s ease-in-out infinite" }} />
        <div style={{ position: "absolute", width: 500, height: 500, borderRadius: "50%", background: "radial-gradient(circle, rgba(124,58,237,0.15) 0%, transparent 70%)", bottom: "10%", right: "-100px", filter: "blur(60px)", animation: "orb2 10s ease-in-out infinite" }} />
        <div style={{ position: "absolute", width: 400, height: 400, borderRadius: "50%", background: "radial-gradient(circle, rgba(167,139,250,0.1) 0%, transparent 70%)", top: "40%", left: "40%", filter: "blur(80px)", animation: "orb3 14s ease-in-out infinite" }} />
      </div>

      {/* Nav */}
      <nav style={{ position: "sticky", top: 0, zIndex: 100, background: "rgba(7,7,17,0.75)", backdropFilter: "blur(24px)", borderBottom: "1px solid rgba(3, 105, 161,0.15)", padding: "0 40px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <img src="/Logo.svg" alt="" style={{ height: 26 }} onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <div>
            <div style={{ fontSize: 8, fontWeight: 600, color: "rgba(167,139,250,0.7)", letterSpacing: "0.08em", textTransform: "uppercase" }}>presents</div>
            <div style={{ fontSize: 15, fontWeight: 700, color: "#fff", letterSpacing: "-0.02em" }}>Visual Engine</div>
          </div>
        </div>
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <a onClick={() => router.push("/pricing")} style={{ fontSize: 13, color: "rgba(255,255,255,0.55)", cursor: "pointer", textDecoration: "none" }}>Pricing</a>
          <button className="opt1-btn" onClick={() => router.push("/auth")} style={{ background: PURPLE, color: "white", border: "none", borderRadius: 9, padding: "9px 22px", fontSize: 13, fontWeight: 600, cursor: "pointer", transition: "all 0.2s", boxShadow: "0 4px 16px -4px rgba(3, 105, 161,0.4)" }}>
            Sign In
          </button>
        </div>
      </nav>

      <div style={{ position: "relative", zIndex: 1 }}>
        {/* Hero */}
        <section style={{ minHeight: "92vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", textAlign: "center", padding: "80px 24px 60px" }}>
          {/* Floating badge */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}
            style={{ animation: "badge-float 5s ease-in-out infinite", display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(3, 105, 161,0.12)", border: "1px solid rgba(3, 105, 161,0.4)", borderRadius: 100, padding: "8px 20px", marginBottom: 36 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: "#a78bfa", display: "inline-block", boxShadow: "0 0 8px #a78bfa" }} />
            <span style={{ fontSize: 12, fontWeight: 700, color: "#a78bfa", letterSpacing: "0.06em" }}>2 FREE GENERATIONS · NO CARD NEEDED</span>
          </motion.div>

          <motion.div variants={stagger} initial="hidden" animate="visible" style={{ maxWidth: 820 }}>
            {["One Image.", "Every Format.", "Instantly."].map((word, i) => (
              <motion.div key={i} variants={fadeUp}>
                <span style={{ display: "block", fontSize: "clamp(40px, 7vw, 80px)", fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.04em", color: i === 2 ? PURPLE : "white" }}>
                  {word}
                </span>
              </motion.div>
            ))}
          </motion.div>

          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7, delay: 0.8 }}
            style={{ fontSize: 17, color: "rgba(255,255,255,0.5)", maxWidth: 560, margin: "28px auto 44px", lineHeight: 1.65 }}>
            Upload one master image — Visual Engine AI generates production-ready assets for every platform, format, and dimension in seconds.
          </motion.p>

          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.6, delay: 1 }}
            style={{ display: "flex", gap: 14, flexWrap: "wrap", justifyContent: "center" }}>
            <button className="opt1-btn" onClick={() => router.push("/auth")}
              style={{ background: PURPLE, color: "white", border: "none", borderRadius: 12, padding: "16px 36px", fontSize: 15, fontWeight: 700, cursor: "pointer", transition: "all 0.2s", boxShadow: "0 8px 24px -6px rgba(3, 105, 161,0.5)" }}>
              Try Free — 2 Generations →
            </button>
            <button onClick={() => router.push("/pricing")}
              style={{ background: "transparent", color: "rgba(255,255,255,0.7)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 12, padding: "16px 32px", fontSize: 15, fontWeight: 600, cursor: "pointer" }}>
              See Pricing
            </button>
          </motion.div>
        </section>

        {/* Stats bar */}
        <section style={{ padding: "0 24px 80px" }}>
          <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true }}
            style={{ maxWidth: 900, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 1, background: "rgba(3, 105, 161,0.15)", borderRadius: 20, overflow: "hidden", border: "1px solid rgba(3, 105, 161,0.2)" }}>
            {[
              { val: 47, suffix: "+", label: "Supported Formats" },
              { val: 4, suffix: "s", label: "Avg Generation Time" },
              { val: 10000, suffix: "+", label: "Assets Generated" },
            ].map((s, i) => (
              <motion.div key={i} variants={fadeUp} style={{ padding: "36px 24px", textAlign: "center", background: "rgba(7,7,17,0.8)" }}>
                <div style={{ fontSize: 44, fontWeight: 800, color: "#a78bfa", letterSpacing: "-0.04em", lineHeight: 1 }}>
                  <Counter target={s.val} suffix={s.suffix} />
                </div>
                <div style={{ fontSize: 13, color: "rgba(255,255,255,0.4)", marginTop: 8, fontWeight: 500 }}>{s.label}</div>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* Problems */}
        <section style={{ padding: "60px 24px 80px" }}>
          <div style={{ maxWidth: 1100, margin: "0 auto" }}>
            <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }} style={{ textAlign: "center", marginBottom: 56 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "#ef4444", letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 14 }}>THE PROBLEM</div>
              <h2 style={{ fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.15 }}>One Design. 47 Formats.<br /><span style={{ color: "rgba(239,68,68,0.8)" }}>Zero Fun.</span></h2>
            </motion.div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
              {[
                { icon: "✂", title: "The Format Chaos", desc: "Your perfect hero image needs to be 47 different sizes — Instagram, LinkedIn, Billboard, App, Print. Each one manually cropped." },
                { icon: "⚡", title: "Compromised Quality", desc: "Stretching, cropping faces, distorted logos. Manual resizing destroys your creative and kills brand consistency across channels." },
                { icon: "⏱", title: "Lost Creative Hours", desc: "A single campaign across all formats takes 3–4 days of manual layout work. Multiply by every campaign. That's your team's week, gone." },
              ].map((p, i) => (
                <motion.div key={i}
                  variants={i % 2 === 0 ? fadeLeft : fadeRight}
                  initial="hidden" whileInView="visible" viewport={{ once: true }}
                  className="problem-card"
                  style={{ background: "rgba(239,68,68,0.04)", border: "1px solid rgba(239,68,68,0.15)", borderRadius: 16, padding: "28px 24px", transition: "all 0.3s cubic-bezier(0.22,1,0.36,1)", cursor: "default" }}>
                  <div style={{ fontSize: 28, marginBottom: 14 }}>{p.icon}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 10 }}>{p.title}</div>
                  <div style={{ fontSize: 14, color: "rgba(255,255,255,0.5)", lineHeight: 1.7 }}>{p.desc}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Before / After */}
        <section style={{ padding: "40px 24px 80px" }}>
          <div style={{ maxWidth: 900, margin: "0 auto" }}>
            <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }} style={{ textAlign: "center", marginBottom: 36 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: PURPLE, letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 12 }}>SEE THE DIFFERENCE</div>
              <h2 style={{ fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.03em" }}>Drag to Reveal the AI Result</h2>
              <p style={{ fontSize: 14, color: "rgba(255,255,255,0.4)", marginTop: 10 }}>Same source image. Left: manual crop disaster. Right: AI-perfect adaptation.</p>
            </motion.div>
            <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.7 }}>
              <BeforeAfterSlider />
            </motion.div>
          </div>
        </section>

        {/* Solutions */}
        <section style={{ padding: "40px 24px 80px" }}>
          <div style={{ maxWidth: 1100, margin: "0 auto" }}>
            <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }} style={{ textAlign: "center", marginBottom: 56 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "#a78bfa", letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 14 }}>THE SOLUTION</div>
              <h2 style={{ fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.15 }}>AI That Understands<br /><span style={{ color: PURPLE }}>Your Creative Intent</span></h2>
            </motion.div>
            <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true }}
              style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 20 }}>
              {[
                { icon: "✨", title: "Flawless Adaptation", desc: "AI detects subjects, backgrounds, and hierarchy — then intelligently extends and recomposes for any dimension naturally." },
                { icon: "🎨", title: "Brand Integrity", desc: "Logos stay sharp. Faces stay framed. Text stays readable. Your brand looks intentional across every platform and format." },
                { icon: "⚡", title: "Instant Scaling", desc: "Upload once. Download 47 formats. What took your team 4 days now takes 4 seconds. Ship campaigns 100x faster." },
              ].map((s, i) => (
                <motion.div key={i} variants={fadeUp}
                  className="solution-card"
                  style={{ background: "rgba(3, 105, 161,0.06)", border: "1px solid rgba(3, 105, 161,0.2)", borderRadius: 16, padding: "28px 24px", transition: "all 0.3s cubic-bezier(0.22,1,0.36,1)", cursor: "default" }}>
                  <div style={{ fontSize: 28, marginBottom: 14 }}>{s.icon}</div>
                  <div style={{ fontSize: 16, fontWeight: 700, marginBottom: 10, color: "#c4b5fd" }}>{s.title}</div>
                  <div style={{ fontSize: 14, color: "rgba(255,255,255,0.5)", lineHeight: 1.7 }}>{s.desc}</div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* How it works timeline */}
        <section style={{ padding: "40px 24px 80px" }}>
          <div style={{ maxWidth: 900, margin: "0 auto" }}>
            <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 56 }}>
              <h2 style={{ fontSize: "clamp(26px, 3.5vw, 40px)", fontWeight: 800, letterSpacing: "-0.03em" }}>How It Works</h2>
            </motion.div>
            <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true }}
              style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 0, position: "relative" }}>
              <div style={{ position: "absolute", top: 28, left: "16%", right: "16%", height: 2, background: "linear-gradient(90deg, rgba(3, 105, 161,0.6), rgba(167,139,250,0.8), rgba(3, 105, 161,0.6))" }} />
              {[
                { step: "01", icon: "📤", title: "Upload Master", desc: "Drop your best version — any size, any format" },
                { step: "02", icon: "🤖", title: "AI Processes", desc: "Engine analyzes composition, subjects, and brand elements" },
                { step: "03", icon: "📦", title: "Download All", desc: "Get every format, pixel-perfect, ready to publish" },
              ].map((s, i) => (
                <motion.div key={i} variants={fadeUp} style={{ textAlign: "center", padding: "0 20px" }}>
                  <div style={{ width: 56, height: 56, borderRadius: "50%", background: "linear-gradient(135deg, #0369A1, #7c3aed)", margin: "0 auto 20px", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, boxShadow: "0 0 30px rgba(3, 105, 161,0.4)", position: "relative", zIndex: 1 }}>
                    {s.icon}
                  </div>
                  <div style={{ fontSize: 11, color: "#0369A1", fontWeight: 700, letterSpacing: "0.1em", marginBottom: 8 }}>STEP {s.step}</div>
                  <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 8 }}>{s.title}</div>
                  <div style={{ fontSize: 13, color: "rgba(255,255,255,0.45)", lineHeight: 1.6 }}>{s.desc}</div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Free CTA */}
        <section style={{ padding: "40px 24px 100px" }}>
          <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.7 }}
            style={{ maxWidth: 780, margin: "0 auto", background: "linear-gradient(135deg, rgba(3, 105, 161,0.2) 0%, rgba(124,58,237,0.1) 100%)", border: "1px solid rgba(3, 105, 161,0.4)", borderRadius: 28, padding: "64px 40px", textAlign: "center" }}>
            <div style={{ fontSize: 48, marginBottom: 20 }}>🎁</div>
            <h2 style={{ fontSize: "clamp(28px, 4vw, 44px)", fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 16 }}>
              Start With 2 Free Generations
            </h2>
            <p style={{ fontSize: 16, color: "rgba(255,255,255,0.55)", maxWidth: 480, margin: "0 auto 36px", lineHeight: 1.65 }}>
              No credit card. No account lock-in. Upload your first image and see AI-powered adaptation in under 5 seconds.
            </p>
            <button className="opt1-btn" onClick={() => router.push("/auth")}
              style={{ background: PURPLE, color: "white", border: "none", borderRadius: 12, padding: "18px 44px", fontSize: 16, fontWeight: 700, cursor: "pointer", transition: "all 0.2s", boxShadow: "0 8px 32px -6px rgba(3, 105, 161,0.6)" }}>
              Try Free Now — No Signup →
            </button>
            <div style={{ marginTop: 20, fontSize: 12, color: "rgba(255,255,255,0.3)" }}>
              Then from $29/month for unlimited · Cancel anytime
            </div>
          </motion.div>
        </section>

        {/* Footer */}
        <footer style={{ borderTop: "1px solid rgba(3, 105, 161,0.1)", padding: "32px 40px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
          <span style={{ fontSize: 12, color: "rgba(255,255,255,0.3)" }}>© 2026 Visual Engine. AI-Powered Creative Adaptation.</span>
          <div style={{ display: "flex", gap: 24 }}>
            {["Privacy Policy", "Terms of Service", "Contact Sales"].map((l) => (
              <span key={l} style={{ fontSize: 12, color: "rgba(255,255,255,0.3)", cursor: "pointer" }}>{l}</span>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}
