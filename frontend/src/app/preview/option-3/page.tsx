"use client";

import React, { useState, useRef, useEffect } from "react";
import { motion, useInView, useScroll, useTransform } from "motion/react";
import { useRouter } from "next/navigation";

const PURPLE = "#0369A1";

function useScrollReveal() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-120px" });
  return { ref, inView };
}

function Counter({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [val, setVal] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  useEffect(() => {
    if (!inView) return;
    const start = Date.now();
    const dur = 2000;
    const tick = () => {
      const p = Math.min((Date.now() - start) / dur, 1);
      setVal(Math.round(target * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, target]);
  return <span ref={ref}>{val.toLocaleString()}{suffix}</span>;
}

const CHAOS_ITEMS = [
  { label: "Face Cut Off", color: "#ef4444", angle: -8, w: 130, h: 130 },
  { label: "Logo Distorted", color: "#f59e0b", angle: 4, w: 180, h: 80 },
  { label: "Wrong Ratio", color: "#ef4444", angle: -3, w: 80, h: 140 },
  { label: "Stretched", color: "#dc2626", angle: 6, w: 160, h: 70 },
  { label: "Cropped Subject", color: "#f59e0b", angle: -5, w: 120, h: 120 },
  { label: "Text Hidden", color: "#ef4444", angle: 3, w: 170, h: 90 },
];

const ORDER_ITEMS = [
  { label: "1:1 Perfect", ratio: "1080×1080", color: "#10b981" },
  { label: "9:16 Story", ratio: "1080×1920", color: "#0369A1" },
  { label: "16:9 Banner", ratio: "1920×1080", color: "#10b981" },
  { label: "4:1 LinkedIn", ratio: "1584×396", color: "#0369A1" },
  { label: "2:3 Pinterest", ratio: "1000×1500", color: "#10b981" },
  { label: "3:1 Billboard", ratio: "14400×4800", color: "#0369A1" },
];

const INTRO_SCENES = [
  { text: "You created the perfect image.", color: "white", size: "clamp(28px, 5vw, 56px)" },
  { text: "Now it needs to be\n47 different sizes.", color: "#fbbf24", size: "clamp(26px, 4.5vw, 50px)" },
  { text: "That used to take days.", color: "#ef4444", size: "clamp(24px, 4vw, 44px)" },
  { text: "Visual Engine changes that.", color: "#a78bfa", size: "clamp(28px, 5vw, 56px)" },
];

function IntroScene({ scene, index }: { scene: typeof INTRO_SCENES[0]; index: number }) {
  const { ref, inView } = useScrollReveal();
  return (
    <div ref={ref} style={{ minHeight: "80vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "40px 24px" }}>
      <motion.div
        initial={{ opacity: 0, y: 60 }}
        animate={inView ? { opacity: 1, y: 0 } : { opacity: 0, y: 60 }}
        transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        style={{ textAlign: "center", maxWidth: 700 }}>
        <span style={{ fontSize: scene.size, fontWeight: 800, color: scene.color, lineHeight: 1.15, letterSpacing: "-0.04em", display: "block", whiteSpace: "pre-line" }}>
          {scene.text}
        </span>
        {index === 3 && (
          <motion.div initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : { opacity: 0 }} transition={{ delay: 0.6, duration: 0.6 }}
            style={{ marginTop: 32, display: "flex", alignItems: "center", justifyContent: "center", gap: 8, background: "rgba(3, 105, 161,0.15)", border: "1px solid rgba(3, 105, 161,0.4)", borderRadius: 100, padding: "10px 24px", display: "inline-flex" }}>
            <span style={{ fontSize: 14, color: "#a78bfa", fontWeight: 600 }}>↓ Scroll to see how</span>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}

export default function Option3() {
  const router = useRouter();
  const chaosRef = useRef<HTMLDivElement>(null);
  const chaosInView = useInView(chaosRef, { once: true, margin: "-100px" });
  const orderRef = useRef<HTMLDivElement>(null);
  const orderInView = useInView(orderRef, { once: true, margin: "-100px" });
  const numbersRef = useRef<HTMLDivElement>(null);
  const numbersInView = useInView(numbersRef, { once: true });

  return (
    <div style={{ background: "#050508", minHeight: "100vh", color: "white", fontFamily: "'Inter', system-ui, sans-serif", overflowX: "hidden" }}>
      <style>{`
        @keyframes flicker { 0%,100%{opacity:1} 92%{opacity:1} 93%{opacity:0.6} 96%{opacity:1} 97%{opacity:0.8} }
        @keyframes chaos-shake { 0%,100%{transform:rotate(var(--r)) translateY(0)} 50%{transform:rotate(calc(var(--r) + 2deg)) translateY(-3px)} }
        @keyframes wipe-in { from{clip-path:inset(0 100% 0 0)} to{clip-path:inset(0 0% 0 0)} }
        .chaos-item:hover { filter: brightness(1.2) !important; }
        .cta-btn:hover { background: #7c5dc4 !important; transform: translateY(-3px); box-shadow: 0 16px 40px -8px rgba(3, 105, 161,0.5) !important; }
      `}</style>

      {/* Sticky minimal nav */}
      <nav style={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 100, padding: "16px 40px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <img src="/Logo.svg" alt="" style={{ height: 24 }} onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <span style={{ fontSize: 15, fontWeight: 700, color: "rgba(255,255,255,0.9)" }}>Visual Engine</span>
        </div>
        <button onClick={() => router.push("/auth")} style={{ background: "rgba(3, 105, 161,0.3)", color: "#a78bfa", border: "1px solid rgba(3, 105, 161,0.4)", borderRadius: 8, padding: "8px 18px", fontSize: 13, fontWeight: 600, cursor: "pointer" }}>
          Sign In
        </button>
      </nav>

      {/* Scene 0 — opening black */}
      <div style={{ minHeight: "40vh", display: "flex", alignItems: "center", justifyContent: "center" }} />

      {/* Scroll-reveal scenes */}
      {INTRO_SCENES.map((scene, i) => (
        <IntroScene key={i} scene={scene} index={i} />
      ))}

      {/* Brand reveal transition */}
      <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ duration: 1.2 }}
        style={{ minHeight: "30vh", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(180deg, #050508 0%, #0e0720 50%, #050508 100%)", position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse 80% 60% at 50% 50%, rgba(3, 105, 161,0.25) 0%, transparent 70%)" }} />
        <div style={{ display: "flex", alignItems: "center", gap: 16, zIndex: 1 }}>
          <img src="/Logo.svg" alt="" style={{ height: 40 }} onError={(e) => { (e.target as HTMLImageElement).style.display = "none"; }} />
          <span style={{ fontSize: 32, fontWeight: 800, color: "white", letterSpacing: "-0.03em" }}>Visual Engine</span>
        </div>
      </motion.div>

      {/* CHAOS section */}
      <section style={{ padding: "80px 24px" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 60 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "#ef4444", letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 16 }}>THE REALITY</div>
            <h2 style={{ fontSize: "clamp(28px, 4vw, 48px)", fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.1 }}>
              Manual Resizing Is<br /><span style={{ color: "#ef4444", animation: "flicker 3s infinite" }}>Destroying Your Work</span>
            </h2>
          </motion.div>

          <div ref={chaosRef} style={{ display: "flex", flexWrap: "wrap", gap: 20, justifyContent: "center", minHeight: 280 }}>
            {CHAOS_ITEMS.map((item, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, scale: 0.7, rotate: 0 }}
                animate={chaosInView ? { opacity: 1, scale: 1, rotate: item.angle } : { opacity: 0, scale: 0.7, rotate: 0 }}
                transition={{ duration: 0.6, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                className="chaos-item"
                style={{ width: item.w, height: item.h, background: `linear-gradient(135deg, ${item.color}22, ${item.color}11)`, border: `2px solid ${item.color}55`, borderRadius: 8, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", position: "relative", filter: "brightness(1)", transition: "filter 0.2s", cursor: "default" }}>
                <div style={{ position: "absolute", top: 6, right: 6, fontSize: 12 }}>⚠️</div>
                <div style={{ fontSize: 11, fontWeight: 700, color: item.color, textAlign: "center", padding: "0 8px", lineHeight: 1.4 }}>{item.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* SOLUTION section — wipe reveal */}
      <section style={{ padding: "40px 24px 80px" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 60 }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "#10b981", letterSpacing: "0.14em", textTransform: "uppercase", marginBottom: 16 }}>WITH VISUAL ENGINE</div>
            <h2 style={{ fontSize: "clamp(28px, 4vw, 48px)", fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1.1 }}>
              Every Format.<br /><span style={{ color: "#10b981" }}>Perfectly Adapted.</span>
            </h2>
          </motion.div>

          <div ref={orderRef} style={{ display: "flex", flexWrap: "wrap", gap: 20, justifyContent: "center" }}>
            {ORDER_ITEMS.map((item, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, scale: 0.8, y: 20 }}
                animate={orderInView ? { opacity: 1, scale: 1, y: 0 } : { opacity: 0, scale: 0.8, y: 20 }}
                transition={{ duration: 0.55, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                style={{ background: `linear-gradient(135deg, ${item.color}15, ${item.color}08)`, border: `2px solid ${item.color}44`, borderRadius: 12, padding: "20px 24px", minWidth: 150, textAlign: "center" }}>
                <div style={{ fontSize: 20, marginBottom: 10 }}>✅</div>
                <div style={{ fontSize: 14, fontWeight: 700, color: item.color, marginBottom: 4 }}>{item.label}</div>
                <div style={{ fontSize: 11, color: "rgba(255,255,255,0.4)" }}>{item.ratio}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Sticky walkthrough panels */}
      <section style={{ padding: "40px 0 80px" }}>
        <div style={{ maxWidth: 1000, margin: "0 auto", padding: "0 24px" }}>
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 56 }}>
            <h2 style={{ fontSize: "clamp(26px, 3.5vw, 42px)", fontWeight: 800, letterSpacing: "-0.03em" }}>How Visual Engine Works</h2>
          </motion.div>
          <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
            {[
              { step: "01", icon: "📤", title: "Upload One Master Image", desc: "Your highest-quality creative — any size, any format. Visual Engine accepts PNG, JPG, WEBP up to 10MB." },
              { step: "02", icon: "🧠", title: "AI Analyzes Your Creative", desc: "The engine maps subjects, reads composition hierarchy, understands brand elements, and plans the adaptation strategy for each output format." },
              { step: "03", icon: "✨", title: "Formats Generate in Seconds", desc: "Background extension, intelligent recomposition, and quality preservation — all 47+ formats generated simultaneously. Average: 4 seconds." },
              { step: "04", icon: "📦", title: "Download Everything", desc: "ZIP download or individual files. Production-ready at full resolution. Every format, perfectly adapted, ready to publish immediately." },
            ].map((step, i) => (
              <motion.div key={i}
                initial={{ opacity: 0, x: -40 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.65, delay: i * 0.1, ease: [0.22, 1, 0.36, 1] }}
                style={{ display: "flex", gap: 28, padding: "36px 32px", background: "rgba(255,255,255,0.02)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 20, alignItems: "flex-start" }}>
                <div style={{ flexShrink: 0, width: 60, height: 60, borderRadius: 16, background: `linear-gradient(135deg, ${PURPLE}33, ${PURPLE}11)`, border: `1px solid ${PURPLE}44`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26 }}>
                  {step.icon}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 11, color: PURPLE, fontWeight: 700, letterSpacing: "0.1em", marginBottom: 8 }}>STEP {step.step}</div>
                  <div style={{ fontSize: 20, fontWeight: 700, marginBottom: 10 }}>{step.title}</div>
                  <div style={{ fontSize: 15, color: "rgba(255,255,255,0.5)", lineHeight: 1.7 }}>{step.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Numbers */}
      <section ref={numbersRef} style={{ padding: "80px 24px", background: "linear-gradient(135deg, rgba(3, 105, 161,0.1) 0%, transparent 100%)" }}>
        <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}
          style={{ maxWidth: 900, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 48, textAlign: "center" }}>
          {[
            { target: 47, suffix: "+", label: "Format Presets" },
            { target: 4, suffix: "s", label: "Avg Generation" },
            { target: 98, suffix: "%", label: "Accuracy Rate" },
            { target: 10, suffix: "K+", label: "Assets Created" },
          ].map((s, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.12, duration: 0.6 }}>
              <div style={{ fontSize: 52, fontWeight: 800, color: "#a78bfa", letterSpacing: "-0.04em", lineHeight: 1 }}>
                <Counter target={s.target} suffix={s.suffix} />
              </div>
              <div style={{ fontSize: 13, color: "rgba(255,255,255,0.45)", marginTop: 10, fontWeight: 500 }}>{s.label}</div>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* Emotional CTA */}
      <section style={{ padding: "80px 24px 120px", textAlign: "center" }}>
        <motion.div initial={{ opacity: 0, y: 40 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8 }} style={{ maxWidth: 680, margin: "0 auto" }}>
          <h2 style={{ fontSize: "clamp(32px, 5vw, 56px)", fontWeight: 800, letterSpacing: "-0.04em", lineHeight: 1.1, marginBottom: 20 }}>
            Ready to Get Your<br /><span style={{ color: PURPLE }}>Time Back?</span>
          </h2>
          <p style={{ fontSize: 17, color: "rgba(255,255,255,0.5)", maxWidth: 480, margin: "0 auto 44px", lineHeight: 1.65 }}>
            Start with 2 free generations. No account required. No credit card. Just results.
          </p>
          <div style={{ display: "flex", gap: 14, justifyContent: "center", flexWrap: "wrap" }}>
            <button className="cta-btn" onClick={() => router.push("/auth")}
              style={{ background: PURPLE, color: "white", border: "none", borderRadius: 14, padding: "18px 44px", fontSize: 16, fontWeight: 700, cursor: "pointer", transition: "all 0.25s", boxShadow: "0 8px 32px -6px rgba(3, 105, 161,0.5)" }}>
              Start Free — 2 Generations →
            </button>
            <button onClick={() => router.push("/pricing")}
              style={{ background: "transparent", color: "rgba(255,255,255,0.6)", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 14, padding: "18px 32px", fontSize: 16, fontWeight: 600, cursor: "pointer" }}>
              View Pricing
            </button>
          </div>
        </motion.div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid rgba(255,255,255,0.06)", padding: "32px 40px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 16 }}>
        <span style={{ fontSize: 12, color: "rgba(255,255,255,0.25)" }}>© 2026 Visual Engine. AI-Powered Creative Adaptation.</span>
        <div style={{ display: "flex", gap: 24 }}>
          {["Privacy", "Terms", "Contact"].map((l) => (
            <span key={l} style={{ fontSize: 12, color: "rgba(255,255,255,0.25)", cursor: "pointer" }}>{l}</span>
          ))}
        </div>
      </footer>
    </div>
  );
}
