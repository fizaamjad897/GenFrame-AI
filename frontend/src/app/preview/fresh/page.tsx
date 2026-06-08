"use client";
import React, { useState, useRef, useEffect, useMemo } from "react";
import { motion, useInView, useScroll, useTransform, useSpring, useMotionValue, AnimatePresence } from "motion/react";
import { useRouter } from "next/navigation";
import AutoFixHighIcon from "@mui/icons-material/AutoFixHigh";
import BoltIcon from "@mui/icons-material/Bolt";
import CropIcon from "@mui/icons-material/Crop";
import TimerOffIcon from "@mui/icons-material/TimerOff";
import BrushIcon from "@mui/icons-material/Brush";
import VerifiedIcon from "@mui/icons-material/Verified";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import AutoAwesomeIcon from "@mui/icons-material/AutoAwesome";
import FileDownloadIcon from "@mui/icons-material/FileDownload";
import SpeedIcon from "@mui/icons-material/Speed";
import GridViewIcon from "@mui/icons-material/GridView";
import TaskAltIcon from "@mui/icons-material/TaskAlt";
import PhotoLibraryIcon from "@mui/icons-material/PhotoLibrary";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import TransformIcon from "@mui/icons-material/Transform";
import AddPhotoAlternateIcon from "@mui/icons-material/AddPhotoAlternate";
import PsychologyIcon from "@mui/icons-material/Psychology";
import RocketLaunchIcon from "@mui/icons-material/RocketLaunch";
import TuneIcon from "@mui/icons-material/Tune";
import AspectRatioIcon from "@mui/icons-material/AspectRatio";
import ImageSearchIcon from "@mui/icons-material/ImageSearch";
import DoneAllIcon from "@mui/icons-material/DoneAll";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import StarIcon from "@mui/icons-material/Star";

const P = "#0369A1", PL = "#f5f0ff", PM = "#ede8f9", PD = "#4B3285";

/* ── useBreakpoint ─────────────────────────────────────── */
function useBreakpoint() {
  const [w, setW] = useState(1200);
  useEffect(() => {
    const upd = () => setW(window.innerWidth);
    upd();
    window.addEventListener("resize", upd);
    return () => window.removeEventListener("resize", upd);
  }, []);
  return { isMobile: w < 640, isTablet: w < 1024, w };
}

/* ── useRipple ─────────────────────────────────────────── */
function useRipple() {
  const [rs, setRs] = useState<{ x: number; y: number; id: number }[]>([]);
  const add = (e: React.MouseEvent<HTMLElement>) => {
    const r = e.currentTarget.getBoundingClientRect();
    const id = Date.now();
    setRs(p => [...p, { x: e.clientX - r.left, y: e.clientY - r.top, id }]);
    setTimeout(() => setRs(p => p.filter(x => x.id !== id)), 800);
  };
  return { rs, add };
}

/* ── Counter ───────────────────────────────────────────── */
function Counter({ to, suffix = "", prefix = "" }: { to: number; suffix?: string; prefix?: string }) {
  const [v, setV] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  useEffect(() => {
    if (!inView) return;
    const t0 = Date.now(), dur = 1800;
    const tick = () => { const p = Math.min((Date.now() - t0) / dur, 1); setV(Math.round(to * (1 - Math.pow(1 - p, 3)))); if (p < 1) requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  }, [inView, to]);
  return <span ref={ref}>{prefix}{v.toLocaleString()}{suffix}</span>;
}

/* ── ScrollBar ─────────────────────────────────────────── */
function ScrollBar() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 200, damping: 30 });
  return <motion.div style={{ position: "fixed", top: 0, left: 0, right: 0, height: 3, background: `linear-gradient(90deg,${P},#a78bfa,${P})`, scaleX, transformOrigin: "left", zIndex: 9999, pointerEvents: "none" }} />;
}

/* ── Cursor Glow ───────────────────────────────────────── */
function CursorGlow() {
  const [pos, setPos] = useState({ x: -300, y: -300 });
  const [vis, setVis] = useState(false);
  const sx = useSpring(pos.x, { stiffness: 100, damping: 28 });
  const sy = useSpring(pos.y, { stiffness: 100, damping: 28 });
  useEffect(() => {
    const m = (e: MouseEvent) => { setPos({ x: e.clientX, y: e.clientY }); setVis(true); };
    const l = () => setVis(false);
    window.addEventListener("mousemove", m);
    window.addEventListener("mouseleave", l);
    return () => { window.removeEventListener("mousemove", m); window.removeEventListener("mouseleave", l); };
  }, []);
  return (
    <motion.div style={{ position: "fixed", top: 0, left: 0, pointerEvents: "none", zIndex: 1, x: sx, y: sy, translateX: "-50%", translateY: "-50%", opacity: vis ? 1 : 0, width: 340, height: 340, borderRadius: "50%", background: `radial-gradient(circle, ${P}12 0%, transparent 70%)` }} />
  );
}

/* ── Magnetic Button ───────────────────────────────────── */
function MagBtn({ children, onClick, ghost, style: ex }: { children: React.ReactNode; onClick?: () => void; ghost?: boolean; style?: React.CSSProperties }) {
  const ref = useRef<HTMLButtonElement>(null);
  const [off, setOff] = useState({ x: 0, y: 0 });
  const { rs, add } = useRipple();
  return (
    <motion.button ref={ref}
      animate={{ x: off.x, y: off.y }}
      transition={{ type: "spring", stiffness: 420, damping: 32 }}
      onMouseMove={e => { if (!ref.current) return; const rc = ref.current.getBoundingClientRect(); setOff({ x: (e.clientX - rc.left - rc.width / 2) * 0.08, y: (e.clientY - rc.top - rc.height / 2) * 0.08 }); }}
      onMouseLeave={() => setOff({ x: 0, y: 0 })}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.96 }}
      onClick={e => { add(e); onClick?.(); }}
      className={ghost ? "btn-ghost" : "btn-primary"}
      style={{ position: "relative", overflow: "hidden", ...ex }}>
      {children}
      {rs.map(r => <span key={r.id} style={{ position: "absolute", left: r.x, top: r.y, width: 8, height: 8, borderRadius: "50%", background: ghost ? `${P}44` : "rgba(255,255,255,0.45)", transform: "translate(-50%,-50%)", animation: "ripple-out 0.75s ease-out forwards", pointerEvents: "none" }} />)}
    </motion.button>
  );
}

/* ── Tilt Card ─────────────────────────────────────────── */
function TiltCard({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  const el = useRef<HTMLDivElement>(null);
  return (
    <div ref={el}
      onMouseMove={e => { if (!el.current) return; const rc = el.current.getBoundingClientRect(); const x = (e.clientX - rc.left - rc.width / 2) / rc.width; const y = (e.clientY - rc.top - rc.height / 2) / rc.height; el.current.style.transform = `perspective(900px) rotateX(${-y * 7}deg) rotateY(${x * 7}deg) translateY(-5px)`; }}
      onMouseLeave={() => { if (el.current) el.current.style.transform = ""; }}
      style={{ transition: "transform 0.18s cubic-bezier(0.22,1,0.36,1)", ...style }}>
      {children}
    </div>
  );
}

/* ── Confetti ──────────────────────────────────────────── */
function Confetti({ on }: { on: boolean }) {
  if (!on) return null;
  const items = Array.from({ length: 36 }, (_, i) => ({ id: i, x: (Math.random() - 0.5) * 560, y: -(80 + Math.random() * 280), rot: Math.random() * 720, delay: Math.random() * 0.35, color: [P, "#a78bfa", "#f59e0b", "#10b981", "#f472b6"][i % 5], size: 5 + Math.random() * 9 }));
  return (
    <div style={{ position: "fixed", inset: 0, pointerEvents: "none", zIndex: 9999 }}>
      {items.map(p => <motion.div key={p.id} initial={{ x: "50vw", y: "55vh", opacity: 1, rotate: 0 }} animate={{ x: `calc(50vw + ${p.x}px)`, y: `calc(55vh + ${p.y}px)`, opacity: 0, rotate: p.rot }} transition={{ duration: 1.4, delay: p.delay, ease: "easeOut" }} style={{ position: "absolute", width: p.size, height: p.size, borderRadius: p.size > 10 ? 2 : "50%", background: p.color }} />)}
    </div>
  );
}

/* ── Interactive Hero Demo ─────────────────────────────── */
function HeroDemo() {
  const [phase, setPhase] = useState<"idle" | "loading" | "done">("idle");
  const [revealed, setRevealed] = useState(0);
  const formats = [{ w: 64, h: 64, label: "1:1" }, { w: 36, h: 64, label: "9:16" }, { w: 80, h: 45, label: "16:9" }, { w: 64, h: 28, label: "4:1" }, { w: 45, h: 64, label: "2:3" }, { w: 80, h: 32, label: "5:1" }];

  const run = () => {
    if (phase !== "idle") { setPhase("idle"); setRevealed(0); return; }
    setPhase("loading");
    setTimeout(() => {
      setPhase("done");
      let n = 0;
      const iv = setInterval(() => { n++; setRevealed(n); if (n >= formats.length) clearInterval(iv); }, 200);
    }, 1400);
  };

  return (
    <div style={{ background: "white", border: `1px solid ${P}1a`, borderRadius: 24, overflow: "hidden", boxShadow: `0 32px 80px -20px ${P}1e, 0 8px 32px rgba(0,0,0,0.05)` }}>
      {/* Chrome bar */}
      <div style={{ background: "#f9fafb", borderBottom: "1px solid #e5e7eb", padding: "10px 16px", display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{ display: "flex", gap: 5 }}>{["#ef4444", "#f59e0b", "#10b981"].map(c => <div key={c} style={{ width: 10, height: 10, borderRadius: "50%", background: c }} />)}</div>
        <div style={{ flex: 1, height: 20, background: "#e5e7eb", borderRadius: 5, marginLeft: 8, display: "flex", alignItems: "center", paddingLeft: 10 }}>
          <span style={{ fontSize: 10, color: "#9ca3af" }}>visualengine.ai/transform</span>
        </div>
      </div>
      <div style={{ padding: 20 }}>
        {/* Upload zone */}
        <motion.div
          animate={phase === "loading" ? { borderColor: P, background: PL } : {}}
          onClick={run}
          style={{ height: 100, background: phase === "idle" ? "#fafafa" : PL, border: `2px dashed ${phase === "idle" ? "#e5e7eb" : P}`, borderRadius: 14, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", marginBottom: 16, cursor: "pointer", transition: "all 0.3s", gap: 6, position: "relative", overflow: "hidden" }}>
          {phase === "idle" && (<><CloudUploadIcon sx={{ fontSize: 28, color: "#9ca3af" }} /><span style={{ fontSize: 12, color: "#9ca3af", fontWeight: 600 }}>Click to generate demo</span></>)}
          {phase === "loading" && (
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 8 }}>
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }} style={{ width: 28, height: 28, borderRadius: "50%", border: `3px solid ${PM}`, borderTopColor: P }} />
              <span style={{ fontSize: 11, color: P, fontWeight: 700 }}>AI adapting formats…</span>
            </div>
          )}
          {phase === "done" && (
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 300 }}>
                <DoneAllIcon sx={{ fontSize: 22, color: "#10b981" }} />
              </motion.div>
              <span style={{ fontSize: 12, fontWeight: 700, color: "#10b981" }}>Done! {formats.length} formats ready</span>
              <span style={{ fontSize: 11, color: "#9ca3af", marginLeft: 4 }}>click to reset</span>
            </div>
          )}
        </motion.div>

        {/* Formats grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 8, marginBottom: 14 }}>
          {formats.map((f, i) => (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4, height: 80, justifyContent: "flex-end" }}>
              <AnimatePresence>
                {(phase === "done" && i < revealed) && (
                  <motion.div initial={{ scaleY: 0, opacity: 0 }} animate={{ scaleY: 1, opacity: 1 }} transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                    style={{ width: f.w * 0.55, height: f.h * 0.55, borderRadius: 5, background: `linear-gradient(135deg,${P}33,#a78bfa22)`, border: `1.5px solid ${P}44`, transformOrigin: "bottom", position: "relative", overflow: "hidden" }}>
                    <motion.div initial={{ x: "-100%" }} animate={{ x: "100%" }} transition={{ duration: 0.5, delay: 0.1 }}
                      style={{ position: "absolute", inset: 0, background: "linear-gradient(90deg,transparent,rgba(255,255,255,0.6),transparent)" }} />
                  </motion.div>
                )}
              </AnimatePresence>
              <span style={{ fontSize: 8, color: i < revealed && phase === "done" ? P : "#d1d5db", fontWeight: 700, transition: "color 0.3s" }}>{f.label}</span>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div style={{ background: PL, borderRadius: 10, padding: "10px 14px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <SpeedIcon sx={{ fontSize: 14, color: P }} />
            <span style={{ fontSize: 11, fontWeight: 700, color: P }}>Visual Engine AI</span>
          </div>
          <AnimatePresence mode="wait">
            <motion.span key={phase} initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }}
              style={{ fontSize: 11, fontWeight: 700, color: phase === "done" ? "#10b981" : "#9ca3af", background: phase === "done" ? "#ecfdf5" : "#f3f4f6", borderRadius: 6, padding: "2px 8px" }}>
              {phase === "idle" ? "Ready" : phase === "loading" ? "Generating…" : "3.8s ✓"}
            </motion.span>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

/* ── Stat Ring ─────────────────────────────────────────── */
function StatRing({ to, suffix, label, icon, pct = 85 }: { to: number; suffix: string; label: string; icon: React.ReactNode; pct?: number }) {
  const wRef = useRef(null);
  const inView = useInView(wRef, { once: true });
  const [hov, setHov] = useState(false);
  const sz = 100, sw = 7, r = (sz - sw * 2) / 2, c = 2 * Math.PI * r;
  return (
    <motion.div ref={wRef} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
      <TiltCard style={{ display: "inline-block", width: "100%" }}>
        <div onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)}
          style={{ background: hov ? PL : "white", border: `1px solid ${hov ? P + "44" : P + "18"}`, borderRadius: 20, padding: "22px 16px", textAlign: "center", transition: "all 0.25s", boxShadow: hov ? `0 12px 32px ${P}18` : `0 4px 20px ${P}0a`, cursor: "default" }}>
          <div style={{ position: "relative", display: "inline-block", marginBottom: 10 }}>
            <svg width={sz} height={sz} style={{ transform: "rotate(-90deg)" }}>
              <circle cx={sz / 2} cy={sz / 2} r={r} fill="none" stroke={PM} strokeWidth={sw} />
              <motion.circle cx={sz / 2} cy={sz / 2} r={r} fill="none" stroke={`url(#rg${to})`} strokeWidth={sw} strokeLinecap="round"
                strokeDasharray={c} initial={{ strokeDashoffset: c }}
                animate={inView ? { strokeDashoffset: c - (pct / 100) * c } : { strokeDashoffset: c }}
                transition={{ duration: 1.8, delay: 0.2, ease: [0.22, 1, 0.36, 1] }} />
              <defs><linearGradient id={`rg${to}`} x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stopColor={P} /><stop offset="100%" stopColor="#a78bfa" /></linearGradient></defs>
            </svg>
            <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 1 }}>
              <div style={{ color: P }}>{icon}</div>
              <div style={{ fontSize: 17, fontWeight: 700, color: "#111827", lineHeight: 1.1 }}><Counter to={to} suffix={suffix} /></div>
            </div>
          </div>
          <div style={{ fontSize: 12, color: "#6b7280", fontWeight: 600, lineHeight: 1.3 }}>{label}</div>
        </div>
      </TiltCard>
    </motion.div>
  );
}

/* ── Animated SVG Flow ─────────────────────────────────── */
function FlowSVG() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });
  // All boxes positioned to fit inside 460×240, labels below don't overflow
  const fmts = [
    { x: 272, y: 20, w: 64, h: 64, label: "1:1"  },
    { x: 346, y: 14, w: 40, h: 72, label: "9:16" },
    { x: 272, y: 96, w: 114, h: 46, label: "16:9" },
    { x: 272, y: 154, w: 108, h: 36, label: "4:1"  },
    { x: 346, y: 96, w: 44, h: 44, label: "1:1"  },
  ];
  return (
    <svg ref={ref} viewBox="0 0 460 242" style={{ width: "100%", height: "auto", overflow: "visible" }}>
      {/* Source card */}
      <motion.rect x="8" y="56" width="112" height="112" rx="12" fill={PL} stroke={P} strokeWidth="2"
        initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ duration: 0.5 }} />
      <motion.rect x="20" y="68" width="88" height="88" rx="7" fill={PM}
        initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 0.25 }} />
      <motion.text x="64" y="118" textAnchor="middle" fontSize="10" fontWeight="700" fill={P}
        initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 0.35 }}>Source</motion.text>
      {/* Arrow → AI */}
      <motion.path d="M 124 112 C 152 112 152 112 180 112" fill="none" stroke={P} strokeWidth="2.5" strokeLinecap="round"
        initial={{ pathLength: 0 }} animate={inView ? { pathLength: 1 } : {}} transition={{ delay: 0.6, duration: 0.45 }} />
      <motion.path d="M 176 107 L 183 112 L 176 117" fill="none" stroke={P} strokeWidth="2.5" strokeLinecap="round"
        initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 1.0 }} />
      {/* AI node */}
      <defs>
        <radialGradient id="aigrad" cx="50%" cy="30%">
          <stop offset="0%" stopColor="#a78bfa" /><stop offset="100%" stopColor={P} />
        </radialGradient>
      </defs>
      <motion.circle cx="210" cy="112" r="23" fill="url(#aigrad)"
        initial={{ scale: 0, opacity: 0 }} animate={inView ? { scale: 1, opacity: 1 } : {}}
        transition={{ delay: 0.85, type: "spring", stiffness: 280 }} style={{ transformOrigin: "210px 112px" }} />
      <motion.text x="210" y="116" textAnchor="middle" fontSize="9" fontWeight="800" fill="white"
        initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 1.05 }}>AI</motion.text>
      {/* Arrow → outputs */}
      <motion.path d="M 233 112 L 250 112" fill="none" stroke={P} strokeWidth="2.5" strokeLinecap="round"
        initial={{ pathLength: 0 }} animate={inView ? { pathLength: 1 } : {}} transition={{ delay: 1.2, duration: 0.28 }} />
      {/* Connector lines to each format */}
      {fmts.map((f, i) => {
        const fy = f.y + f.h / 2;
        return (
          <motion.path key={i} d={`M 252 112 Q 252 ${fy} ${f.x} ${fy}`}
            fill="none" stroke={`${P}50`} strokeWidth="1.5" strokeDasharray="4 3"
            initial={{ pathLength: 0 }} animate={inView ? { pathLength: 1 } : {}}
            transition={{ delay: 1.35 + i * 0.1, duration: 0.4 }} />
        );
      })}
      {/* Format boxes — no x translation to avoid clipping */}
      {fmts.map((f, i) => (
        <motion.g key={`f${i}`}
          initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}}
          transition={{ delay: 1.5 + i * 0.1, duration: 0.4 }}>
          <rect x={f.x} y={f.y} width={f.w} height={f.h} rx="6" fill={PL} stroke={P} strokeWidth="1.5" />
          <rect x={f.x + 5} y={f.y + 5} width={f.w - 10} height={f.h - 10} rx="3" fill={PM} />
          <text x={f.x + f.w / 2} y={f.y + f.h / 2 + 4} textAnchor="middle" fontSize="8" fontWeight="700" fill={P}>{f.label}</text>
          <motion.circle cx={f.x + f.w - 5} cy={f.y + 5} r="7" fill="#10b981"
            initial={{ scale: 0 }} animate={inView ? { scale: 1 } : {}}
            transition={{ delay: 1.95 + i * 0.08, type: "spring", stiffness: 300 }}
            style={{ transformOrigin: `${f.x + f.w - 5}px ${f.y + 5}px` }} />
          <motion.text x={f.x + f.w - 5} y={f.y + 9} textAnchor="middle" fontSize="7" fontWeight="800" fill="white"
            initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 2.05 + i * 0.08 }}>✓</motion.text>
        </motion.g>
      ))}
    </svg>
  );
}

/* ── Comparison Bar ────────────────────────────────────── */
function CompareBar({ label, manual, ai }: { label: string; manual: string; ai: string }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  return (
    <motion.div ref={ref} initial={{ opacity: 0, x: -30 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.5 }}
      style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12, alignItems: "center", padding: "14px 0", borderBottom: "1px solid #f3f4f6" }}>
      <span style={{ fontSize: 13, fontWeight: 600, color: "#374151" }}>{label}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <CancelIcon sx={{ fontSize: 14, color: "#ef4444", flexShrink: 0 }} />
        <span style={{ fontSize: 12, color: "#ef4444" }}>{manual}</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <CheckCircleIcon sx={{ fontSize: 14, color: "#10b981", flexShrink: 0 }} />
        <span style={{ fontSize: 12, color: "#10b981", fontWeight: 700 }}>{ai}</span>
      </div>
    </motion.div>
  );
}

/* ── B/A Slider ────────────────────────────────────────── */
function BASlider() {
  const [pos, setPos] = useState(50);
  const ref = useRef<HTMLDivElement>(null);
  const drag = useRef(false);
  const [active, setActive] = useState(0);
  const platforms = ["Story 9:16", "Banner 4:1", "Square 1:1", "YouTube 16:9", "Billboard 3:1"];

  const move = (clientX: number) => {
    if (!drag.current || !ref.current) return;
    const rc = ref.current.getBoundingClientRect();
    setPos(Math.max(5, Math.min(95, ((clientX - rc.left) / rc.width) * 100)));
  };

  return (
    <div>
      <div ref={ref} className="ba-slider"
        onPointerDown={e => { drag.current = true; (e.target as Element).setPointerCapture?.(e.pointerId); }}
        onPointerUp={() => { drag.current = false; }}
        onPointerMove={e => move(e.clientX)}>
        {/* AFTER */}
        <div style={{ position: "absolute", inset: 0, background: `linear-gradient(135deg, ${PL}, white)`, display: "flex", alignItems: "center", justifyContent: "center", flexWrap: "wrap", gap: 10, padding: 24 }}>
          {[{ w: 75, h: 75 }, { w: 42, h: 75 }, { w: 120, h: 50 }, { w: 120, h: 68 }, { w: 100, h: 40 }].map((f, i) => (
            <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 5 }}>
              <motion.div initial={{ scaleY: 0 }} whileInView={{ scaleY: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.1, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                style={{ width: f.w, height: f.h, borderRadius: 6, background: `linear-gradient(135deg,${P}33,#a78bfa22)`, border: `2px solid ${P}55`, display: "flex", alignItems: "center", justifyContent: "center", transformOrigin: "bottom" }}>
                <div style={{ width: "55%", height: "55%", background: `${P}55`, borderRadius: 3 }} />
              </motion.div>
            </div>
          ))}
          <div style={{ position: "absolute", bottom: 16, background: "rgba(16,185,129,0.92)", borderRadius: 10, padding: "7px 16px", display: "flex", alignItems: "center", gap: 6 }}>
            <DoneAllIcon sx={{ fontSize: 14, color: "white" }} />
            <span style={{ fontSize: 12, fontWeight: 700, color: "white" }}>AI-Perfect</span>
          </div>
        </div>
        {/* BEFORE */}
        <div style={{ position: "absolute", inset: 0, clipPath: `inset(0 ${100 - pos}% 0 0)`, background: "linear-gradient(135deg,#fef2f2,#fff1f0)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ textAlign: "center" }}>
            <div style={{ width: 170, height: 170, margin: "0 auto 14px", background: "linear-gradient(135deg,#fee2e2,#fecaca)", border: "2px solid #ef444455", borderRadius: 12, display: "flex", alignItems: "center", justifyContent: "center", position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", inset: 0, backgroundImage: "repeating-linear-gradient(45deg,transparent,transparent 8px,rgba(239,68,68,0.06) 8px,rgba(239,68,68,0.06) 16px)" }} />
              <CropIcon sx={{ fontSize: 44, color: "#ef4444", opacity: 0.4 }} />
              <div style={{ position: "absolute", top: 8, left: 8, background: "rgba(239,68,68,0.88)", borderRadius: 6, padding: "3px 8px", fontSize: 9, color: "white", fontWeight: 700 }}>CROPPED</div>
              <div style={{ position: "absolute", bottom: 8, right: 8, background: "rgba(239,68,68,0.88)", borderRadius: 6, padding: "3px 8px", fontSize: 9, color: "white", fontWeight: 700 }}>DISTORTED</div>
            </div>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "rgba(239,68,68,0.12)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 100, padding: "6px 14px" }}>
              <CancelIcon sx={{ fontSize: 14, color: "#ef4444" }} />
              <span style={{ fontSize: 12, fontWeight: 700, color: "#ef4444" }}>Manual Fail</span>
            </div>
          </div>
        </div>
        {/* Handle */}
        <div style={{ position: "absolute", top: 0, bottom: 0, left: `${pos}%`, width: 3, background: "white", transform: "translateX(-50%)", zIndex: 10, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 0 1px rgba(0,0,0,0.07)" }}>
          <motion.div whileHover={{ scale: 1.14 }} style={{ width: 42, height: 42, borderRadius: "50%", background: "white", boxShadow: `0 4px 20px rgba(0,0,0,0.14),0 0 0 3px ${P}33`, display: "flex", alignItems: "center", justifyContent: "center", cursor: "ew-resize" }}>
            <TuneIcon sx={{ fontSize: 20, color: P }} />
          </motion.div>
        </div>
        <div style={{ position: "absolute", top: 12, left: 12, background: "rgba(239,68,68,0.9)", borderRadius: 7, padding: "3px 10px", fontSize: 10, fontWeight: 600, color: "white", zIndex: 5 }}>BEFORE</div>
        <div style={{ position: "absolute", top: 12, right: 12, background: `${P}ee`, borderRadius: 7, padding: "3px 10px", fontSize: 10, fontWeight: 600, color: "white", zIndex: 5 }}>AFTER</div>
      </div>
      <div style={{ display: "flex", gap: 8, justifyContent: "center", marginTop: 16, flexWrap: "wrap" }}>
        {platforms.map((pl, i) => (
          <motion.button key={i} whileTap={{ scale: 0.93 }} onClick={() => setActive(i)}
            style={{ background: active === i ? PM : "white", border: `1.5px solid ${active === i ? P : "#e5e7eb"}`, color: active === i ? P : "#6b7280", borderRadius: 10, padding: "7px 13px", fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all 0.2s" }}>
            {pl}
          </motion.button>
        ))}
      </div>
    </div>
  );
}

/* ── Format Burst ──────────────────────────────────────── */
/* ── Format Showcase — platform-branded card mosaic ─────── */
const SHOWCASE_CARDS = [
  // left column — tall cards
  { id:0, name:"Instagram Story", ratio:"9:16", sub:"1080 × 1920", l:0,   t:0,   w:80,  h:142, grad:"linear-gradient(160deg,#4f1c91,#7c3aed)",  accent:"#7c3aed"  },
  { id:1, name:"Pinterest Pin",   ratio:"2:3",  sub:"1000 × 1500", l:0,   t:152, w:80,  h:120, grad:"linear-gradient(160deg,#134e4a,#0d9488)",  accent:"#0d9488"  },
  // centre square
  { id:2, name:"Square Post",     ratio:"1:1",  sub:"1080 × 1080", l:94,  t:0,   w:112, h:112, grad:"linear-gradient(160deg,#1e1b4b,#4338ca)",  accent:"#4338ca"  },
  // right column — wide cards
  { id:3, name:"YouTube Thumb",   ratio:"16:9", sub:"1280 × 720",  l:220, t:0,   w:230, h:130, grad:"linear-gradient(160deg,#831843,#db2777)",  accent:"#db2777"  },
  { id:4, name:"LinkedIn Banner", ratio:"4:1",  sub:"1584 × 396",  l:94,  t:124, w:244, h:62,  grad:"linear-gradient(160deg,#1e3a5f,#2563eb)",  accent:"#2563eb"  },
  { id:5, name:"OOH Billboard",   ratio:"3:1",  sub:"14400 × 4800",l:94,  t:200, w:244, h:82,  grad:"linear-gradient(160deg,#78350f,#ea580c)",  accent:"#ea580c"  },
];

function FormatShowcase() {
  const [hov, setHov] = useState<number | null>(null);

  return (
    <div style={{ position:"relative", width:460, height:295, flexShrink:0 }}>
      {SHOWCASE_CARDS.map((c, i) => (
        <div key={c.id}
          style={{ position:"absolute", left:c.l, top:c.t,
            animation:`burst-float ${3.2 + i * 0.36}s ${i * -0.62}s ease-in-out infinite`,
            zIndex: hov === i ? 10 : 1 }}
          onMouseEnter={() => setHov(i)}
          onMouseLeave={() => setHov(null)}>

          <motion.div
            initial={{ opacity:0, scale:0.82, y:14 }}
            animate={{ opacity:1, scale:1, y:0 }}
            transition={{ delay:0.22 + i * 0.1, duration:0.6, ease:[0.22,1,0.36,1] }}
            whileHover={{ scale:1.04, y:-4, transition:{ duration:0.2 } }}
            style={{ width:c.w, height:c.h, borderRadius:14, background:c.grad,
              boxShadow: hov===i
                ? `0 20px 48px -8px ${c.accent}55, 0 4px 16px ${c.accent}33`
                : `0 6px 20px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06)`,
              position:"relative", overflow:"hidden", cursor:"default",
              transition:"box-shadow 0.25s" }}>

            {/* Simulated image inside card */}
            <div style={{ position:"absolute", top:10, left:10, right:10, bottom:28, borderRadius:8, background:"rgba(255,255,255,0.18)" }}>
              <div style={{ position:"absolute", top:6, left:6, right:6, bottom:6, borderRadius:5, background:"rgba(255,255,255,0.12)" }} />
            </div>

            {/* Bottom label bar */}
            <div style={{ position:"absolute", bottom:0, left:0, right:0, height:26, background:"rgba(0,0,0,0.28)", backdropFilter:"blur(4px)", display:"flex", alignItems:"center", justifyContent:"space-between", padding:"0 10px" }}>
              <span style={{ fontSize:9, fontWeight:700, color:"white", letterSpacing:"0.06em" }}>{c.ratio}</span>
              <span style={{ fontSize:8, color:"rgba(255,255,255,0.65)" }}>{c.name.split(" ")[0]}</span>
            </div>

            {/* Shimmer sweep */}
            <motion.div animate={{ x:["-140%","180%"] }} transition={{ duration:2.8 + i*0.4, repeat:Infinity, repeatDelay:1.5+i*0.6, ease:"easeInOut" }}
              style={{ position:"absolute", inset:0, width:"38%", background:"linear-gradient(90deg,transparent,rgba(255,255,255,0.2),transparent)", transform:"skewX(-14deg)", pointerEvents:"none" }} />

            {/* ✓ badge top-right */}
            <motion.div
              initial={{ scale:0 }}
              animate={{ scale:1 }}
              transition={{ delay:0.9 + i*0.09, type:"spring", stiffness:300 }}
              style={{ position:"absolute", top:8, right:8, width:20, height:20, borderRadius:"50%", background:"rgba(255,255,255,0.95)", display:"flex", alignItems:"center", justifyContent:"center", boxShadow:"0 2px 8px rgba(0,0,0,0.18)", zIndex:5 }}>
              <span style={{ fontSize:9, color:"#10b981", fontWeight:700 }}>✓</span>
            </motion.div>

            {/* Hover overlay — shows full name + dimensions */}
            <AnimatePresence>
              {hov === i && (
                <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} exit={{ opacity:0 }} transition={{ duration:0.18 }}
                  style={{ position:"absolute", inset:0, background:"rgba(0,0,0,0.38)", borderRadius:14, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:4 }}>
                  <span style={{ fontSize:12, fontWeight:600, color:"white", textShadow:"0 1px 4px rgba(0,0,0,0.4)" }}>{c.name}</span>
                  <span style={{ fontSize:10, color:"rgba(255,255,255,0.7)" }}>{c.sub}</span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      ))}
    </div>
  );
}

/* ── Hero Platform Cards — 3 depth layers, CSS float, mouse parallax ── */
const HC_L1 = [ // back / slowest / faintest
  { w:32,h:57,  rot:-10, l:"2.5%", t:"12%", dur:"28s", del:"0s",   an:"hca", col:"#833ab4" },
  { w:82,h:46,  rot:7,   l:"5%",   t:"66%", dur:"32s", del:"-10s", an:"hcb", col:"#0077b5" },
  { w:46,h:82,  rot:-6,  l:"87%",  t:"10%", dur:"25s", del:"-4s",  an:"hcc", col:"#ff0000" },
  { w:92,h:30,  rot:10,  l:"83%",  t:"63%", dur:"29s", del:"-15s", an:"hcd", col:"#e1306c" },
  { w:54,h:54,  rot:-8,  l:"42%",  t:"1%",  dur:"34s", del:"-20s", an:"hca", col:"#e60023" },
  { w:104,h:34, rot:5,   l:"38%",  t:"91%", dur:"27s", del:"-7s",  an:"hcb", col:"#f59e0b" },
];
const HC_L2 = [ // mid
  { w:40,h:71,  rot:9,   l:"13%",  t:"30%", dur:"20s", del:"-5s",  an:"hcc", col:"#0369A1" },
  { w:98,h:55,  rot:-7,  l:"70%",  t:"22%", dur:"22s", del:"-12s", an:"hcd", col:"#ff0000" },
  { w:60,h:60,  rot:13,  l:"90%",  t:"50%", dur:"19s", del:"-8s",  an:"hca", col:"#833ab4" },
  { w:80,h:26,  rot:-5,  l:"54%",  t:"76%", dur:"23s", del:"-16s", an:"hcb", col:"#0077b5" },
  { w:36,h:54,  rot:6,   l:"23%",  t:"80%", dur:"21s", del:"-3s",  an:"hcc", col:"#10b981" },
];
const HC_L3 = [ // front / fastest / most visible
  { w:48,h:85,  rot:-5,  l:"0.5%", t:"44%", dur:"14s", del:"-6s",  an:"hca", col:"#0369A1" },
  { w:108,h:61, rot:8,   l:"81%",  t:"36%", dur:"16s", del:"-11s", an:"hcb", col:"#833ab4" },
  { w:70,h:70,  rot:-12, l:"18%",  t:"56%", dur:"13s", del:"-2s",  an:"hcc", col:"#0077b5" },
  { w:106,h:35, rot:4,   l:"59%",  t:"10%", dur:"15s", del:"-9s",  an:"hcd", col:"#ff0000" },
  { w:46,h:69,  rot:11,  l:"76%",  t:"78%", dur:"17s", del:"-13s", an:"hca", col:"#e60023" },
];
const HC_OPS = [0.22, 0.38, 0.55];

function HeroCards() {
  const refs = [useRef<HTMLDivElement>(null), useRef<HTMLDivElement>(null), useRef<HTMLDivElement>(null)];
  const MULT = [22, 12, 5];
  useEffect(() => {
    let raf: number; let tx = 0, ty = 0, cx = 0, cy = 0;
    const onMove = (e: MouseEvent) => {
      tx = (e.clientX / window.innerWidth  - 0.5);
      ty = (e.clientY / window.innerHeight - 0.5);
    };
    const tick = () => {
      cx += (tx - cx) * 0.04; cy += (ty - cy) * 0.04;
      refs.forEach((r, i) => { if (r.current) r.current.style.transform = `translate(${cx * -MULT[i]}px,${cy * -MULT[i] * 0.65}px)`; });
      raf = requestAnimationFrame(tick);
    };
    window.addEventListener("mousemove", onMove);
    raf = requestAnimationFrame(tick);
    return () => { window.removeEventListener("mousemove", onMove); cancelAnimationFrame(raf); };
  }, []);

  const renderLayer = (cards: typeof HC_L1, ref: React.RefObject<HTMLDivElement>, op: number) => (
    <div ref={ref} style={{ position:"absolute", inset:0, pointerEvents:"none" }}>
      {cards.map((c, i) => (
        <div key={i} style={{ position:"absolute", left:c.l, top:c.t, transform:`rotate(${c.rot}deg)` }}>
          <div style={{ width:c.w, height:c.h, borderRadius:10,
            border:`1.5px solid ${c.col}`,
            background:`linear-gradient(145deg,${c.col}1a,${c.col}07)`,
            opacity:op,
            animation:`${c.an} ${c.dur} ${c.del} ease-in-out infinite`,
            display:"flex", flexDirection:"column", justifyContent:"flex-end", padding:"5px 6px", position:"relative", overflow:"hidden" }}>
            {/* Inner image block */}
            <div style={{ position:"absolute", top:6, left:6, right:6, bottom:14, borderRadius:6, background:`${c.col}20` }} />
            {/* Bottom ratio bar */}
            <div style={{ height:2, borderRadius:1, background:`${c.col}70`, position:"relative", zIndex:1 }} />
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div style={{ position:"absolute", inset:0, overflow:"hidden", zIndex:0 }}>
      {renderLayer(HC_L1, refs[0], HC_OPS[0])}
      {renderLayer(HC_L2, refs[1], HC_OPS[1])}
      {renderLayer(HC_L3, refs[2], HC_OPS[2])}
    </div>
  );
}

/* ── Platform Ticker ────────────────────────────────────── */
const TICKER = ["Instagram Story","YouTube Thumb","LinkedIn Banner","Pinterest Pin","Twitter Post","TikTok Video","Google Display","OOH Billboard","Facebook Cover","Snapchat Ad","App Store Banner","Email Header"];

function PlatformTicker() {
  const items = [...TICKER, ...TICKER];
  return (
    <div style={{ position:"absolute", bottom:0, left:0, right:0, borderTop:`1px solid ${P}10`, overflow:"hidden", background:"rgba(255,255,255,0.7)", backdropFilter:"blur(10px)", padding:"10px 0", zIndex:10 }}>
      <motion.div animate={{ x:["0%","-50%"] }} transition={{ duration:28, repeat:Infinity, ease:"linear" }}
        style={{ display:"flex", gap:0, whiteSpace:"nowrap", width:"max-content" }}>
        {items.map((t, i) => (
          <span key={i} style={{ fontSize:11, color:"#9ca3af", fontWeight:500, letterSpacing:"0.04em", padding:"0 28px", borderRight:i < items.length-1 ? "1px solid #e5e7eb" : "none" }}>
            {t}
          </span>
        ))}
      </motion.div>
    </div>
  );
}

/* ── Canvas Particles ──────────────────────────────────── */
function ParticleCanvas() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const cv = ref.current; if (!cv) return;
    const ctx = cv.getContext("2d")!;
    let raf: number;
    let W = cv.width = window.innerWidth;
    let H = cv.height = window.innerHeight;
    const mouse = { x: W / 2, y: H / 2 };
    const N = 75;
    const pts = Array.from({ length: N }, () => ({
      x: Math.random() * W, y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.45,
      vy: (Math.random() - 0.5) * 0.45,
      r: 1.4 + Math.random() * 2,
      op: 0.1 + Math.random() * 0.22,
    }));
    const onResize = () => {
      W = cv.width = window.innerWidth;
      H = cv.height = window.innerHeight;
    };
    const onMove = (e: MouseEvent) => { mouse.x = e.clientX; mouse.y = e.clientY; };
    const tick = () => {
      ctx.clearRect(0, 0, W, H);
      pts.forEach(p => {
        const dx = p.x - mouse.x, dy = p.y - mouse.y;
        const d = Math.hypot(dx, dy);
        if (d < 100 && d > 0) { const f = (100 - d) / 100 * 0.55; p.vx += dx / d * f; p.vy += dy / d * f; }
        p.vx *= 0.97; p.vy *= 0.97;
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
        p.x = Math.max(0, Math.min(W, p.x));
        p.y = Math.max(0, Math.min(H, p.y));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(3, 105, 161,${p.op})`;
        ctx.fill();
      });
      for (let i = 0; i < N - 1; i++) {
        for (let j = i + 1; j < N; j++) {
          const d = Math.hypot(pts[i].x - pts[j].x, pts[i].y - pts[j].y);
          if (d < 140) {
            ctx.beginPath();
            ctx.moveTo(pts[i].x, pts[i].y);
            ctx.lineTo(pts[j].x, pts[j].y);
            ctx.strokeStyle = `rgba(3, 105, 161,${(1 - d / 140) * 0.09})`;
            ctx.lineWidth = 0.7;
            ctx.stroke();
          }
        }
      }
      raf = requestAnimationFrame(tick);
    };
    window.addEventListener("resize", onResize);
    window.addEventListener("mousemove", onMove);
    raf = requestAnimationFrame(tick);
    return () => { window.removeEventListener("resize", onResize); window.removeEventListener("mousemove", onMove); cancelAnimationFrame(raf); };
  }, []);
  return <canvas ref={ref} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none", zIndex: 0 }} />;
}

/* ── Aurora Blobs (mouse-reactive) ─────────────────────── */
function AuroraBlobs() {
  const mx = useMotionValue(0), my = useMotionValue(0);
  const bx1 = useSpring(mx, { stiffness: 28, damping: 22 });
  const by1 = useSpring(my, { stiffness: 28, damping: 22 });
  const bx2 = useSpring(mx, { stiffness: 16, damping: 18 });
  const by2 = useSpring(my, { stiffness: 16, damping: 18 });
  useEffect(() => {
    const f = (e: MouseEvent) => {
      mx.set((e.clientX / window.innerWidth  - 0.5) * 90);
      my.set((e.clientY / window.innerHeight - 0.5) * 70);
    };
    window.addEventListener("mousemove", f);
    return () => window.removeEventListener("mousemove", f);
  }, [mx, my]);
  return (
    <>
      <motion.div style={{ x: bx1, y: by1, position:"absolute", top:-150, right:-100, width:720, height:720, borderRadius:"50%", background:`radial-gradient(circle,${P}1c 0%,transparent 68%)`, filter:"blur(90px)", pointerEvents:"none", zIndex:0 }} />
      <motion.div style={{ x: bx2, y: by2, position:"absolute", bottom:-100, left:-60, width:540, height:540, borderRadius:"50%", background:"radial-gradient(circle,#a78bfa18 0%,transparent 70%)", filter:"blur(80px)", pointerEvents:"none", zIndex:0 }} />
      <motion.div animate={{ scale:[1,1.12,1], opacity:[0.7,1,0.7] }} transition={{ duration:10, repeat:Infinity, ease:"easeInOut" }}
        style={{ position:"absolute", top:"38%", left:"28%", width:380, height:380, borderRadius:"50%", background:`radial-gradient(circle,${P}10 0%,transparent 70%)`, filter:"blur(60px)", pointerEvents:"none", zIndex:0 }} />
    </>
  );
}

/* ── Floating Format Shapes (hero bg) ─────────────────── */
const FLOAT_SHAPES = [
  { w:26, h:46, rot:-8,  l:"3%",  t:"20%", dur:"18s", del:"0s",   an:"fltA" },
  { w:64, h:36, rot:6,   l:"5%",  t:"62%", dur:"22s", del:"-6s",  an:"fltB" },
  { w:40, h:40, rot:-14, l:"89%", t:"14%", dur:"16s", del:"-3s",  an:"fltC" },
  { w:70, h:23, rot:8,   l:"83%", t:"55%", dur:"20s", del:"-9s",  an:"fltD" },
  { w:32, h:48, rot:-6,  l:"16%", t:"82%", dur:"24s", del:"-14s", an:"fltA" },
  { w:66, h:22, rot:12,  l:"73%", t:"76%", dur:"19s", del:"-7s",  an:"fltB" },
  { w:44, h:44, rot:-3,  l:"46%", t:"4%",  dur:"17s", del:"-4s",  an:"fltC" },
  { w:30, h:53, rot:9,   l:"35%", t:"88%", dur:"21s", del:"-11s", an:"fltD" },
  { w:58, h:20, rot:-11, l:"58%", t:"50%", dur:"26s", del:"-18s", an:"fltA" },
  { w:22, h:36, rot:5,   l:"76%", t:"30%", dur:"23s", del:"-8s",  an:"fltC" },
];

function FloatingFormats() {
  return (
    <div style={{ position:"absolute", inset:0, pointerEvents:"none", overflow:"hidden", zIndex:0 }}>
      {FLOAT_SHAPES.map((s, i) => (
        <div key={i} style={{ position:"absolute", left:s.l, top:s.t, transform:`rotate(${s.rot}deg)` }}>
          <div style={{ width:s.w, height:s.h, borderRadius:7, border:`1.5px solid ${P}1c`,
            background:`linear-gradient(135deg,${P}07,transparent)`,
            animation:`${s.an} ${s.dur} ${s.del} ease-in-out infinite` }} />
        </div>
      ))}
    </div>
  );
}

/* ── Rising Particles ──────────────────────────────────── */
function RisingParticles({ n = 12 }: { n?: number }) {
  const items = Array.from({ length: n }, (_, i) => ({
    x: 2 + (i * 96 / n),
    sz: 2 + (i % 3) * 1.8,
    dur: 11 + (i % 5) * 3,
    del: -(i * 1.6),
    drift: i % 2 === 0 ? 14 : -12,
  }));
  return (
    <div style={{ position:"absolute", inset:0, pointerEvents:"none", overflow:"hidden", zIndex:0 }}>
      {items.map((p, i) => (
        <div key={i} style={{
          position:"absolute", left:`${p.x}%`, bottom:-10,
          width:p.sz, height:p.sz, borderRadius:"50%", background:P,
          animationName:"rise-p",
          animationDuration:`${p.dur}s`,
          animationDelay:`${p.del}s`,
          animationTimingFunction:"linear",
          animationIterationCount:"infinite",
        }} />
      ))}
    </div>
  );
}

/* ── Twinkle Stars (CTA) ───────────────────────────────── */
const STAR_POS = [
  {l:"8%", t:"22%",d:"0s"}, {l:"91%",t:"17%",d:"-1.1s"}, {l:"18%",t:"72%",d:"-2.3s"},
  {l:"84%",t:"68%",d:"-0.7s"}, {l:"46%",t:"7%", d:"-1.8s"}, {l:"55%",t:"86%",d:"-3.1s"},
  {l:"29%",t:"44%",d:"-0.4s"}, {l:"71%",t:"38%",d:"-2.6s"}, {l:"62%",t:"56%",d:"-1.5s"},
];

function TwinkleStars() {
  return (
    <div style={{ position:"absolute", inset:0, pointerEvents:"none", zIndex:0 }}>
      {STAR_POS.map((s, i) => (
        <div key={i} style={{ position:"absolute", left:s.l, top:s.t, opacity:0,
          animationName:"twinkle", animationDuration:`${2.2+(i%4)*0.9}s`,
          animationDelay:s.d, animationTimingFunction:"ease-in-out",
          animationIterationCount:"infinite" }}>
          <div style={{ position:"relative", width:14, height:14 }}>
            <div style={{ position:"absolute", top:"50%", left:0, right:0, height:1.5,
              background:"rgba(255,255,255,0.6)", borderRadius:1, transform:"translateY(-50%)" }} />
            <div style={{ position:"absolute", left:"50%", top:0, bottom:0, width:1.5,
              background:"rgba(255,255,255,0.6)", borderRadius:1, transform:"translateX(-50%)" }} />
            <div style={{ position:"absolute", top:"50%", left:0, right:0, height:1.5,
              background:"rgba(255,255,255,0.6)", borderRadius:1, transform:"translateY(-50%) rotate(45deg)" }} />
          </div>
        </div>
      ))}
    </div>
  );
}

/* ── Trust Strip ───────────────────────────────────────── */
function TrustStrip() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.1 }}
      style={{ display: "flex", alignItems: "center", gap: 16, marginTop: 28, flexWrap: "wrap" }}>
      {/* Avatar stack */}
      <div style={{ display: "flex" }}>
        {[P, "#7c3aed", "#a78bfa", "#f472b6"].map((color, i) => (
          <div key={i} style={{ width: 30, height: 30, borderRadius: "50%", background: color, border: "2px solid white", marginLeft: i > 0 ? -9 : 0, zIndex: 4 - i, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 600, color: "white", flexShrink: 0 }}>
            {["J","M","S","A"][i]}
          </div>
        ))}
      </div>
      <div>
        <div style={{ display: "flex", gap: 1, marginBottom: 2 }}>
          {[1,2,3,4,5].map(s => <StarIcon key={s} sx={{ fontSize: 12, color: "#f59e0b" }} />)}
        </div>
        <span style={{ fontSize: 12, color: "#6b7280", lineHeight: 1 }}>
          <strong style={{ color: "#111827" }}>500+</strong> creative teams trust Visual Engine
        </span>
      </div>
      <div style={{ width: 1, height: 28, background: "#e5e7eb", flexShrink: 0 }} />
      <div style={{ display: "inline-flex", alignItems: "center", gap: 5, background: PL, border: `1px solid ${P}22`, borderRadius: 100, padding: "5px 12px" }}>
        <CheckCircleIcon sx={{ fontSize: 12, color: P }} />
        <span style={{ fontSize: 11, fontWeight: 600, color: P }}>No card needed</span>
      </div>
    </motion.div>
  );
}

/* ══════════════════════════════════════════════════════════
   MAIN PAGE
════════════════════════════════════════════════════════════ */
export default function FreshLanding() {
  const router = useRouter();
  const { isMobile, isTablet } = useBreakpoint();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [expandedProblem, setExpandedProblem] = useState<number | null>(null);
  const [hoveredSol, setHoveredSol] = useState<number | null>(null);
  const [activeEngine, setActiveEngine] = useState(0);
  const [confetti, setConfetti] = useState(false);
  const lineRef = useRef<HTMLDivElement>(null);
  const lineInView = useInView(lineRef, { once: true });
  const { scrollY } = useScroll();
  const heroY = useTransform(scrollY, [0, 500], [0, -60]);
  const handleCTA = () => { setConfetti(true); setTimeout(() => setConfetti(false), 2200); setTimeout(() => router.push("/auth"), 350); };

  const PROBLEMS = [
    { Icon: CropIcon, color: "#ef4444", bg: "#fef2f2", border: "#fecaca", title: "Format Chaos", short: "One creative → 47 manual resizes every campaign.", detail: "Your team spends 3–4 days per campaign manually cropping, resizing, and fixing layouts for every channel. Each format is a fresh battle with aspect ratios and composition." },
    { Icon: ImageSearchIcon, color: "#f59e0b", bg: "#fffbeb", border: "#fde68a", title: "Compromised Quality", short: "Cropped faces. Stretched logos. Broken layouts.", detail: "Manual resizing destroys your creative. Subjects get cut off, logos distort, text overlaps. Every bad output damages brand perception across every platform." },
    { Icon: TimerOffIcon, color: "#ef4444", bg: "#fef2f2", border: "#fecaca", title: "Lost Creative Hours", short: "Designers stuck resizing instead of creating.", detail: "When your best designers burn hours on mechanical resizing, they're not doing strategy or ideation. That's the real hidden cost every campaign." },
  ];
  const SOLUTIONS = [
    { Icon: AutoFixHighIcon, title: "Flawless Adaptation", desc: "AI detects subjects, composition, and brand hierarchy — then intelligently extends and recomposes for any dimension. Naturally, every time." },
    { Icon: VerifiedIcon, title: "Brand Integrity", desc: "Logos stay crisp. Faces stay framed. Text stays readable. Every format looks intentional because the AI understands your design, not just the pixels." },
    { Icon: BoltIcon, title: "Instant Scaling", desc: "Upload once. Get all 47+ formats in seconds. What took your team 4 days now takes 4 seconds. Ship campaigns 100× faster." },
  ];
  const STEPS = [
    { Icon: CloudUploadIcon, n: "01", title: "Upload Master Image", desc: "Drop your highest-quality creative. PNG, JPG, or WEBP up to 10MB. Any dimensions accepted." },
    { Icon: PsychologyIcon, n: "02", title: "AI Analyzes & Adapts", desc: "Engine maps composition, detects brand elements, and plans adaptation for every target format simultaneously." },
    { Icon: FileDownloadIcon, n: "03", title: "Download Everything", desc: "All 47+ formats — pixel-perfect, production-ready. ZIP or individual files at full resolution." },
  ];
  const ENGINES = [
    { icon: <TransformIcon sx={{ fontSize: 20 }} />, name: "Transformation Engine", desc: "Adapt any existing image to any format. The AI extends backgrounds, recomposes layouts, and preserves subjects while maintaining your original creative intent.", features: ["Background extension AI", "Subject-aware cropping", "Layout recomposition", "47+ format presets"] },
    { icon: <AddPhotoAlternateIcon sx={{ fontSize: 20 }} />, name: "Creation Engine", desc: "Generate new format variations from scratch. Select a template and the AI creates production-ready assets tuned to each platform's requirements and brand guidelines.", features: ["Platform-optimized generation", "Brand guideline awareness", "Batch creation", "Custom dimension support"] },
  ];
  const COMPARE = [
    { label: "Time per format", manual: "30–60 min", ai: "< 1 second" },
    { label: "Batch all formats", manual: "Multiple days", ai: "4 seconds total" },
    { label: "Subject preservation", manual: "Manual crop decisions", ai: "AI-perfect every time" },
    { label: "Brand compliance", manual: "Manual checklist", ai: "Built-in by design" },
    { label: "Cost per format", manual: "$15–50 designer time", ai: "< $0.01" },
  ];

  return (
    <div style={{ background: "#fff", fontFamily: "'Inter', system-ui, sans-serif", color: "#111827", overflowX: "hidden" }}>
      <ScrollBar />
      {!isMobile && <CursorGlow />}
      <Confetti on={confetti} />

      <style>{`
        * { box-sizing: border-box; }
        .btn-primary { background: linear-gradient(135deg,${P},#7c3aed); color:white; border:none; border-radius:12px; padding:14px 32px; font-size:15px; font-weight:700; cursor:pointer; display:inline-flex; align-items:center; gap:8px; }
        .btn-ghost { background:transparent; color:${P}; border:2px solid ${P}33; border-radius:12px; padding:13px 28px; font-size:14px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:8px; }
        .btn-primary:hover { box-shadow:0 12px 32px -8px ${P}55; }
        .btn-ghost:hover { background:${PL}; border-color:${P}; }
        .nav-link { font-size:13px; font-weight:500; color:#6b7280; cursor:pointer; padding:4px 0; border-bottom:2px solid transparent; transition:all 0.15s; }
        .nav-link:hover { color:${P}; border-bottom-color:${P}; }
        @keyframes ripple-out { from{transform:translate(-50%,-50%) scale(0);opacity:0.5} to{transform:translate(-50%,-50%) scale(5);opacity:0} }
        @keyframes burst-float { 0%,100%{transform:translateY(0px)} 50%{transform:translateY(-8px)} }
        @keyframes hca { 0%,100%{transform:translateY(0) translateX(0)} 30%{transform:translateY(-18px) translateX(7px)} 70%{transform:translateY(-10px) translateX(-5px)} }
        @keyframes hcb { 0%,100%{transform:translateY(0) translateX(0)} 40%{transform:translateY(-24px) translateX(-10px)} 80%{transform:translateY(-9px) translateX(11px)} }
        @keyframes hcc { 0%,100%{transform:translateY(0) translateX(0)} 50%{transform:translateY(-16px) translateX(5px)} }
        @keyframes hcd { 0%,100%{transform:translateY(0) translateX(0)} 25%{transform:translateY(-20px) translateX(-7px)} 75%{transform:translateY(-6px) translateX(3px)} }
        @keyframes aurora-drift { 0%,100%{transform:translate(0,0) scale(1)} 33%{transform:translate(50px,-35px) scale(1.07)} 66%{transform:translate(-30px,25px) scale(0.95)} }
        @keyframes fltA { 0%,100%{transform:translateY(0px)}  50%{transform:translateY(-16px)} }
        @keyframes fltB { 0%,100%{transform:translateY(0px)}  50%{transform:translateY(-22px)} }
        @keyframes fltC { 0%,100%{transform:translateY(0px)}  33%{transform:translateY(-13px)} 66%{transform:translateY(-7px)} }
        @keyframes fltD { 0%,100%{transform:translateY(0px)}  40%{transform:translateY(-20px)} 80%{transform:translateY(-9px)} }
        @keyframes rise-p { 0%{transform:translateY(0) translateX(0);opacity:0} 8%{opacity:0.11} 85%{opacity:0.06} 100%{transform:translateY(-320px) translateX(14px);opacity:0} }
        @keyframes twinkle { 0%,100%{opacity:0;transform:scale(0) rotate(0deg)} 50%{opacity:0.55;transform:scale(1) rotate(135deg)} }
        @keyframes badge-bob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-5px)} }
        @keyframes glow-dot { 0%,100%{box-shadow:0 0 0 0 ${P}44} 50%{box-shadow:0 0 0 8px ${P}00} }
        @keyframes float-card { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
        @keyframes spin-ring { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        @keyframes spin-slow { from{transform:rotate(0deg)} to{transform:rotate(360deg)} }
        .ba-slider { position:relative; height:360px; border-radius:24px; overflow:hidden; cursor:ew-resize; user-select:none; box-shadow:0 24px 80px -20px ${P}28; border:2px solid ${P}22; touch-action:none; }
        @media(max-width:639px) {
          .ba-slider { height:280px; }
          .hero-grid { grid-template-columns:1fr !important; }
          .stat-grid { grid-template-columns:1fr 1fr !important; }
          .three-grid { grid-template-columns:1fr !important; }
          .engine-grid { grid-template-columns:1fr !important; }
          .compare-grid { grid-template-columns:1fr 1fr 1fr !important; }
          .section-pad { padding:60px 20px !important; }
          .hero-pad { padding:70px 20px 60px !important; }
          .nav-pad { padding:0 20px !important; }
          .footer-pad { padding:28px 20px !important; flex-direction:column !important; gap:12px !important; }
          .cta-pad { padding:48px 24px !important; }
          .tab-row { flex-direction:column !important; }
        }
        @media(min-width:640px) and (max-width:1023px) {
          .hero-grid { grid-template-columns:1fr !important; }
          .stat-grid { grid-template-columns:repeat(2,1fr) !important; }
          .section-pad { padding:80px 32px !important; }
          .hero-pad { padding:80px 32px 70px !important; }
          .nav-pad { padding:0 32px !important; }
        }
        @media(max-width:1023px) {
          .hide-mobile { display:none !important; }
          .show-mobile { display:flex !important; }
        }
        @media(min-width:1024px) {
          .show-mobile { display:none !important; }
        }
        .mobile-nav-overlay { position:fixed; inset:0; background:white; z-index:200; display:flex; flex-direction:column; padding:20px; }
        .step-icon:hover { transform:scale(1.12) rotate(6deg); }
        .step-icon { transition:transform 0.2s cubic-bezier(0.22,1,0.36,1); cursor:pointer; }
      `}</style>

      {/* ── MOBILE NAV OVERLAY ────────────────────────────── */}
      <AnimatePresence>
        {mobileNavOpen && (
          <motion.div className="mobile-nav-overlay" initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }} transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 48 }}>
              <div style={{ fontSize: 17, fontWeight: 700, color: "#111827" }}>Visual Engine</div>
              <motion.button whileTap={{ scale: 0.9 }} onClick={() => setMobileNavOpen(false)} style={{ background: PL, border: "none", borderRadius: 10, width: 40, height: 40, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}>
                <CloseIcon sx={{ color: P }} />
              </motion.button>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8, flex: 1 }}>
              {["Pricing", "Features", "About"].map(l => (
                <button key={l} onClick={() => { setMobileNavOpen(false); if (l === "Pricing") router.push("/pricing"); }} style={{ background: "transparent", border: "none", borderBottom: "1px solid #f3f4f6", padding: "18px 0", fontSize: 20, fontWeight: 600, color: "#111827", textAlign: "left", cursor: "pointer" }}>{l}</button>
              ))}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <MagBtn ghost onClick={() => { setMobileNavOpen(false); router.push("/auth"); }} style={{ justifyContent: "center", borderRadius: 12, padding: "14px" }}>Sign In</MagBtn>
              <MagBtn onClick={() => { setMobileNavOpen(false); router.push("/auth"); }} style={{ justifyContent: "center", borderRadius: 12, padding: "14px" }}>Try Free <ArrowForwardIcon sx={{ fontSize: 16 }} /></MagBtn>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── NAV ───────────────────────────────────────────── */}
      <motion.nav initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: 0.5 }}
        className="nav-pad"
        style={{ position: "sticky", top: 0, zIndex: 100, background: "rgba(255,255,255,0.88)", backdropFilter: "blur(20px)", borderBottom: "1px solid #f3f4f6", padding: "0 52px", height: 64, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {/* VE icon mark */}
          <div style={{ width: 34, height: 34, borderRadius: 10, background: `linear-gradient(135deg, ${P}, #7c3aed)`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
            <AutoAwesomeIcon sx={{ fontSize: 16, color: "white" }} />
          </div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 700, color: "#111827", letterSpacing: "-0.03em", lineHeight: 1.1 }}>Visual Engine</div>
            <div style={{ fontSize: 9, fontWeight: 500, color: "#9ca3af", letterSpacing: "0.04em" }}>AI Image Adaptation</div>
          </div>
        </div>
        <div className="hide-mobile" style={{ display: "flex", gap: 28 }}>
          {["Pricing", "Features", "About"].map(l => <span key={l} className="nav-link" onClick={() => l === "Pricing" && router.push("/pricing")}>{l}</span>)}
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div className="hide-mobile" style={{ display: "flex", gap: 10 }}>
            <MagBtn ghost onClick={() => router.push("/auth")} style={{ padding: "9px 18px", fontSize: 13, borderRadius: 9 }}>Sign In</MagBtn>
            <MagBtn onClick={() => router.push("/auth")} style={{ padding: "9px 20px", fontSize: 13, borderRadius: 9 }}>Try Free <ArrowForwardIcon sx={{ fontSize: 15 }} /></MagBtn>
          </div>
          <motion.button className="show-mobile" whileTap={{ scale: 0.9 }} onClick={() => setMobileNavOpen(true)}
            style={{ background: PL, border: "none", borderRadius: 10, width: 40, height: 40, alignItems: "center", justifyContent: "center", cursor: "pointer" }}>
            <MenuIcon sx={{ color: P }} />
          </motion.button>
        </div>
      </motion.nav>

      {/* ── HERO ──────────────────────────────────────────── */}
      <section style={{ position:"relative", overflow:"hidden", minHeight:"calc(100vh - 64px)", display:"flex", alignItems:"center", background:"#fafafa" }}>

        {/* BG: floating platform cards */}
        <HeroCards />
        {/* BG: aurora blobs */}
        <div style={{ position:"absolute", top:-160, right:-120, width:680, height:680, borderRadius:"50%", background:`radial-gradient(circle,${P}1a 0%,transparent 68%)`, filter:"blur(90px)", pointerEvents:"none", zIndex:1, animation:"aurora-drift 18s ease-in-out infinite" }} />
        <div style={{ position:"absolute", bottom:-100, left:-80, width:520, height:520, borderRadius:"50%", background:"radial-gradient(circle,#a78bfa18 0%,transparent 70%)", filter:"blur(80px)", pointerEvents:"none", zIndex:1, animation:"aurora-drift 24s ease-in-out infinite reverse" }} />
        {/* BG: dot grid */}
        <svg style={{ position:"absolute", inset:0, width:"100%", height:"100%", pointerEvents:"none", zIndex:1 }} aria-hidden>
          <defs><pattern id="dg" width="30" height="30" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill={P} opacity="0.09" /></pattern></defs>
          <rect width="100%" height="100%" fill="url(#dg)" />
        </svg>
        {/* BG: centre vignette — makes content readable over the floating cards */}
        <div style={{ position:"absolute", inset:0, background:"radial-gradient(ellipse 90% 100% at 50% 50%, rgba(250,250,250,0.82) 20%, rgba(250,250,250,0.4) 55%, transparent 100%)", pointerEvents:"none", zIndex:2 }} />

        {/* ── 2-column content ── */}
        <motion.div style={{ y: heroY, position:"relative", zIndex:10, width:"100%", maxWidth:1280, margin:"0 auto", display:"grid", gridTemplateColumns:"1fr 1fr", gap:"clamp(32px,4vw,64px)", alignItems:"center", padding:"clamp(56px,7vh,88px) clamp(20px,4vw,52px)" }}
          className="hero-grid">

          {/* LEFT — copy */}
          <div>
            {/* Badge */}
            <motion.div initial={{ opacity:0, y:14 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.06, duration:0.5 }}>
              <div style={{ display:"inline-flex", alignItems:"center", gap:8, background:"rgba(255,255,255,0.9)", backdropFilter:"blur(12px)", border:`1px solid ${P}28`, borderRadius:100, padding:"7px 16px", marginBottom:24, boxShadow:`0 2px 12px ${P}0e` }}>
                <motion.div animate={{ rotate:360 }} transition={{ duration:4, repeat:Infinity, ease:"linear" }} style={{ display:"flex" }}>
                  <AutoAwesomeIcon sx={{ fontSize:13, color:P }} />
                </motion.div>
                <span style={{ fontSize:11, fontWeight:600, color:P, letterSpacing:"0.06em" }}>AI IMAGE ADAPTATION</span>
                <span style={{ background:`linear-gradient(135deg,${P},#7c3aed)`, color:"white", fontSize:9, fontWeight:600, borderRadius:100, padding:"2px 7px" }}>FREE</span>
              </div>
            </motion.div>

            {/* Headline — reasonable size, blur-in per line */}
            <div style={{ marginBottom:18 }}>
              {[
                { text:"One Upload.",     grad:false },
                { text:"Every Platform.", grad:false },
                { text:"4 Seconds.",      grad:true  },
              ].map((line, i) => (
                <motion.div key={i}
                  initial={{ opacity:0, filter:"blur(12px)", y:22 }}
                  animate={{ opacity:1, filter:"blur(0px)", y:0 }}
                  transition={{ delay:0.16 + i * 0.16, duration:0.68, ease:[0.22,1,0.36,1] }}>
                  <span style={{ display:"block", fontSize:"clamp(30px,3.8vw,52px)", fontWeight:700, letterSpacing:"-0.03em", lineHeight:1.08,
                    ...(line.grad
                      ? { background:`linear-gradient(135deg,${P} 10%,#a78bfa 55%,#7c3aed 100%)`, WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text" }
                      : { color:"#0d0d0d" }) }}>
                    {line.text}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Subtext */}
            <motion.p initial={{ opacity:0, y:12 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.68 }}
              style={{ fontSize:"clamp(13px,1.2vw,15px)", color:"#6b7280", lineHeight:1.72, maxWidth:430, marginBottom:28 }}>
              Upload one master image and get{" "}
              <span style={{ color:"#374151", fontWeight:600 }}>production-ready assets for 47+ platforms</span>{" "}
              in seconds. No resizing. No compromise.
            </motion.p>

            {/* CTAs */}
            <motion.div initial={{ opacity:0, y:12 }} animate={{ opacity:1, y:0 }} transition={{ delay:0.8 }}
              style={{ display:"flex", gap:10, flexWrap:"wrap", marginBottom:20 }}>
              <MagBtn onClick={handleCTA} style={{ fontSize:14, padding:"13px 28px", borderRadius:12 }}>
                Try Free — 2 Generations <ArrowForwardIcon sx={{ fontSize:15 }} />
              </MagBtn>
              <MagBtn ghost onClick={() => router.push("/pricing")} style={{ fontSize:13, padding:"12px 24px", borderRadius:12 }}>
                View Pricing
              </MagBtn>
            </motion.div>

            {/* Stat chips */}
            <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:1.0 }}
              style={{ display:"flex", gap:7, flexWrap:"wrap", marginBottom:20 }}>
              {[
                { icon:<BoltIcon sx={{ fontSize:12 }} />,         label:"4s avg" },
                { icon:<GridViewIcon sx={{ fontSize:12 }} />,     label:"47+ formats" },
                { icon:<CheckCircleIcon sx={{ fontSize:12 }} />,  label:"No card" },
              ].map((s, i) => (
                <div key={i} style={{ display:"flex", alignItems:"center", gap:4, background:"rgba(255,255,255,0.9)", backdropFilter:"blur(8px)", border:`1px solid ${P}1e`, borderRadius:100, padding:"4px 11px", fontSize:11, color:P, fontWeight:500 }}>
                  <span style={{ display:"flex" }}>{s.icon}</span>{s.label}
                </div>
              ))}
            </motion.div>

            {/* Trust strip */}
            <TrustStrip />
          </div>

          {/* RIGHT — FormatBurst animation */}
          <motion.div
            initial={{ opacity:0, x:44, scale:0.96 }}
            animate={{ opacity:1, x:0, scale:1 }}
            transition={{ delay:0.28, duration:0.85, ease:[0.22,1,0.36,1] }}
            className="hide-mobile"
            style={{ display:"flex", justifyContent:"center", alignItems:"center" }}>
            <FormatShowcase />
          </motion.div>

        </motion.div>

        {/* Platform ticker at bottom */}
        <PlatformTicker />
      </section>

      {/* ── STATS ─────────────────────────────────────────── */}
      <section className="section-pad" style={{ background: `linear-gradient(135deg,${PL},white,${PL})`, borderTop: `1px solid ${P}18`, borderBottom: `1px solid ${P}18`, padding: "52px", position: "relative", overflow: "hidden" }}>
        <RisingParticles n={14} />
        <div className="stat-grid" style={{ maxWidth: 960, margin: "0 auto", display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, position: "relative", zIndex: 1 }}>
          <StatRing to={47} suffix="+" label="Format Presets" icon={<GridViewIcon sx={{ fontSize: 15 }} />} pct={88} />
          <StatRing to={4} suffix="s" label="Avg Generation" icon={<SpeedIcon sx={{ fontSize: 15 }} />} pct={20} />
          <StatRing to={98} suffix="%" label="Accuracy Rate" icon={<TaskAltIcon sx={{ fontSize: 15 }} />} pct={98} />
          <StatRing to={10} suffix="K+" label="Assets Created" icon={<PhotoLibraryIcon sx={{ fontSize: 15 }} />} pct={75} />
        </div>
      </section>

      {/* ── PROBLEMS ──────────────────────────────────────── */}
      <section className="section-pad" style={{ padding: "100px 52px", position: "relative", overflow: "hidden" }}>
        <RisingParticles n={10} />
        <div style={{ maxWidth: 1200, margin: "0 auto", position: "relative", zIndex: 1 }}>
        <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 60 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 100, padding: "5px 14px", marginBottom: 16 }}>
            <CancelIcon sx={{ fontSize: 11, color: "#ef4444" }} />
            <span style={{ fontSize: 10, fontWeight: 600, color: "#ef4444", letterSpacing: "0.08em" }}>THE PROBLEM</span>
          </div>
          <h2 style={{ fontSize: "clamp(26px,4.5vw,50px)", fontWeight: 700, letterSpacing: "-0.025em", lineHeight: 1.15, marginBottom: 12 }}>
            One Design.{" "}<span style={{ color: "#ef4444", borderBottom: "3px solid #fecaca" }}>Too Many Formats.</span>
          </h2>
          <p style={{ fontSize: 15, color: "#6b7280", maxWidth: 420, margin: "0 auto" }}>Click any card to read the full story.</p>
        </motion.div>

        <motion.div className="three-grid" variants={{ h: { opacity: 0 }, s: { opacity: 1, transition: { staggerChildren: 0.13 } } }} initial="h" whileInView="s" viewport={{ once: true }}
          style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 18 }}>
          {PROBLEMS.map((p, i) => (
            <motion.div key={i} variants={{ h: { opacity: 0, y: 38 }, s: { opacity: 1, y: 0, transition: { duration: 0.6 } } }}>
              <TiltCard>
                <motion.div onClick={() => setExpandedProblem(expandedProblem === i ? null : i)}
                  animate={{ boxShadow: expandedProblem === i ? `0 20px 50px -14px ${p.color}44` : "0 2px 12px rgba(0,0,0,0.04)" }}
                  style={{ background: p.bg, border: `2px solid ${expandedProblem === i ? p.color : p.border}`, borderRadius: 20, padding: "26px 22px", cursor: "pointer", transition: "border-color 0.2s" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
                    <motion.div whileHover={{ rotate: 10, scale: 1.08 }}
                      style={{ width: 50, height: 50, borderRadius: 14, background: `${p.color}15`, border: `1.5px solid ${p.color}28`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                      <p.Icon sx={{ fontSize: 24, color: p.color }} />
                    </motion.div>
                    <motion.div animate={{ rotate: expandedProblem === i ? 45 : 0 }} transition={{ duration: 0.22 }}
                      style={{ width: 26, height: 26, borderRadius: "50%", background: `${p.color}15`, display: "flex", alignItems: "center", justifyContent: "center", color: p.color, fontWeight: 700, fontSize: 17 }}>+</motion.div>
                  </div>
                  <h3 style={{ fontSize: 17, fontWeight: 700, color: "#111827", marginBottom: 7 }}>{p.title}</h3>
                  <p style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.68 }}>{p.short}</p>
                  <AnimatePresence>
                    {expandedProblem === i && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }} style={{ overflow: "hidden" }}>
                        <div style={{ marginTop: 14, paddingTop: 14, borderTop: `1px solid ${p.color}20` }}>
                          <p style={{ fontSize: 13, color: "#374151", lineHeight: 1.78 }}>{p.detail}</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </TiltCard>
            </motion.div>
          ))}
        </motion.div>
        </div>
      </section>

      {/* ── BEFORE/AFTER ──────────────────────────────────── */}
      <section className="section-pad" style={{ background: `linear-gradient(180deg,#fff 0%,${PL} 25%,${PL} 75%,#fff 100%)`, padding: "60px 52px 80px" }}>
        <div style={{ maxWidth: 980, margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 38 }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: PM, border: `1px solid ${P}33`, borderRadius: 100, padding: "5px 14px", marginBottom: 14 }}>
              <TuneIcon sx={{ fontSize: 11, color: P }} />
              <span style={{ fontSize: 10, fontWeight: 600, color: P, letterSpacing: "0.08em" }}>DRAG TO REVEAL · TOUCH SUPPORTED</span>
            </div>
            <h2 style={{ fontSize: "clamp(24px,4vw,44px)", fontWeight: 700, letterSpacing: "-0.04em" }}>Before vs After</h2>
          </motion.div>
          <motion.div initial={{ opacity: 0, scale: 0.97 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ duration: 0.65 }}>
            <BASlider />
          </motion.div>
        </div>
      </section>

      {/* ── FLOW DIAGRAM ──────────────────────────────────── */}
      <section className="section-pad" style={{ padding: "60px 52px 80px", maxWidth: 1200, margin: "0 auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: isTablet ? "1fr" : "1fr 1fr", gap: 60, alignItems: "center" }}>
          <motion.div initial={{ opacity: 0, x: -40 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.7 }}>
            <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: PL, border: `1px solid ${P}33`, borderRadius: 100, padding: "5px 14px", marginBottom: 20 }}>
              <AutoAwesomeIcon sx={{ fontSize: 11, color: P }} />
              <span style={{ fontSize: 10, fontWeight: 600, color: P, letterSpacing: "0.08em" }}>THE TRANSFORMATION</span>
            </div>
            <h2 style={{ fontSize: "clamp(24px,3.5vw,42px)", fontWeight: 700, letterSpacing: "-0.04em", lineHeight: 1.12, marginBottom: 16 }}>
              One upload.<br /><span style={{ color: P }}>Every format.</span>
            </h2>
            <p style={{ fontSize: 15, color: "#6b7280", lineHeight: 1.72, marginBottom: 28 }}>The Visual Engine AI analyzes your source image's composition, then adapts it for every format and platform — keeping subjects framed, brands intact, and layouts natural.</p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {[["Subject-aware AI", "Detects faces, logos, and focal points"], ["Background extension", "Fills new areas seamlessly"], ["Layout recomposition", "Adapts hierarchy to each format"]].map(([t, d]) => (
                <motion.div key={t} whileHover={{ x: 4 }} style={{ display: "flex", alignItems: "flex-start", gap: 10, padding: "10px 14px", background: PL, borderRadius: 10, border: `1px solid ${P}18`, cursor: "default" }}>
                  <CheckCircleIcon sx={{ fontSize: 18, color: P, flexShrink: 0, mt: 0.2 }} />
                  <div><div style={{ fontSize: 13, fontWeight: 700, color: "#111827" }}>{t}</div><div style={{ fontSize: 12, color: "#6b7280" }}>{d}</div></div>
                </motion.div>
              ))}
            </div>
          </motion.div>
          <motion.div initial={{ opacity: 0, x: 40 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.7, delay: 0.1 }}>
            <div style={{ background: "white", border: `1px solid ${P}18`, borderRadius: 24, padding: "28px 24px", boxShadow: `0 16px 48px ${P}0d`, overflow: "visible" }}>
              <FlowSVG />
            </div>
          </motion.div>
        </div>
      </section>

      {/* ── SOLUTIONS ─────────────────────────────────────── */}
      <section className="section-pad" style={{ padding: "60px 52px 80px", position: "relative", overflow: "hidden" }}>
        <RisingParticles n={10} />
        <div style={{ maxWidth: 1200, margin: "0 auto", position: "relative", zIndex: 1 }}>
        <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 56 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 6, background: PL, border: `1px solid ${P}33`, borderRadius: 100, padding: "5px 14px", marginBottom: 16 }}>
            <CheckCircleIcon sx={{ fontSize: 11, color: P }} />
            <span style={{ fontSize: 10, fontWeight: 600, color: P, letterSpacing: "0.08em" }}>THE SOLUTION</span>
          </div>
          <h2 style={{ fontSize: "clamp(26px,4.5vw,50px)", fontWeight: 700, letterSpacing: "-0.025em", lineHeight: 1.15, marginBottom: 12 }}>
            AI That Understands <span style={{ color: P }}>Your Creative</span>
          </h2>
        </motion.div>

        <motion.div className="three-grid" variants={{ h: { opacity: 0 }, s: { opacity: 1, transition: { staggerChildren: 0.12 } } }} initial="h" whileInView="s" viewport={{ once: true }}
          style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 18 }}>
          {SOLUTIONS.map((s, i) => (
            <motion.div key={i} variants={{ h: { opacity: 0, y: 36 }, s: { opacity: 1, y: 0, transition: { duration: 0.6 } } }}>
              <TiltCard style={{ height: "100%" }}>
                <div onMouseEnter={() => setHoveredSol(i)} onMouseLeave={() => setHoveredSol(null)}
                  style={{ background: hoveredSol === i ? `linear-gradient(135deg,${PL},white)` : "white", border: `2px solid ${hoveredSol === i ? P + "44" : "#e5e7eb"}`, borderRadius: 20, padding: "30px 26px", height: "100%", transition: "all 0.28s cubic-bezier(0.22,1,0.36,1)", boxShadow: hoveredSol === i ? `0 20px 56px ${P}1e` : "0 2px 12px rgba(0,0,0,0.04)", cursor: "default" }}>
                  <motion.div animate={hoveredSol === i ? { rotate: [0, -8, 8, 0], scale: [1, 1.12, 1] } : {}} transition={{ duration: 0.45 }}
                    style={{ width: 52, height: 52, borderRadius: 14, background: PL, border: `1.5px solid ${P}33`, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 18 }}>
                    <s.Icon sx={{ fontSize: 24, color: P }} />
                  </motion.div>
                  <h3 style={{ fontSize: 17, fontWeight: 700, color: "#111827", marginBottom: 9 }}>{s.title}</h3>
                  <p style={{ fontSize: 13, color: "#6b7280", lineHeight: 1.76 }}>{s.desc}</p>
                  <AnimatePresence>
                    {hoveredSol === i && (
                      <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                        style={{ marginTop: 16, display: "flex", alignItems: "center", gap: 5, color: P, fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
                        Learn more <ArrowForwardIcon sx={{ fontSize: 13 }} />
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </TiltCard>
            </motion.div>
          ))}
        </motion.div>
        </div>
      </section>

      {/* ── HOW IT WORKS ──────────────────────────────────── */}
      <section className="section-pad" style={{ background: `linear-gradient(135deg,${PL},white,${PL})`, padding: "80px 52px", borderTop: `1px solid ${P}18`, borderBottom: `1px solid ${P}18` }}>
        <div style={{ maxWidth: 960, margin: "0 auto" }}>
          <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 60 }}>
            <h2 style={{ fontSize: "clamp(24px,4vw,44px)", fontWeight: 700, letterSpacing: "-0.04em" }}>How It Works</h2>
            <p style={{ fontSize: 15, color: "#6b7280", marginTop: 10 }}>Three steps. Under five seconds.</p>
          </motion.div>
          <div style={{ position: "relative" }}>
            <div ref={lineRef} style={{ position: "absolute", top: 36, left: "17%", right: "17%", height: 3, background: "#e5e7eb", borderRadius: 2, zIndex: 0 }}>
              <motion.div initial={{ width: 0 }} animate={lineInView ? { width: "100%" } : {}} transition={{ delay: 0.4, duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
                style={{ height: "100%", background: `linear-gradient(90deg,${P},#a78bfa)`, borderRadius: 2 }} />
            </div>
            <motion.div variants={{ h: { opacity: 0 }, s: { opacity: 1, transition: { staggerChildren: 0.2 } } }} initial="h" whileInView="s" viewport={{ once: true }}
              style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 0, position: "relative", zIndex: 1 }}>
              {STEPS.map((s, i) => (
                <motion.div key={i} variants={{ h: { opacity: 0, y: 36 }, s: { opacity: 1, y: 0, transition: { duration: 0.65, ease: [0.22, 1, 0.36, 1] } } }}
                  style={{ textAlign: "center", padding: "0 clamp(8px,2vw,24px)" }}>
                  <motion.div whileHover={{ scale: 1.12, rotate: 8 }} whileTap={{ scale: 0.93 }} className="step-icon"
                    style={{ width: 72, height: 72, borderRadius: "50%", background: `linear-gradient(135deg,${P},#7c3aed)`, margin: "0 auto 20px", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 8px 28px -8px ${P}55` }}>
                    <s.Icon sx={{ fontSize: 30, color: "white" }} />
                  </motion.div>
                  <div style={{ fontSize: 10, color: P, fontWeight: 700, letterSpacing: "0.1em", marginBottom: 7 }}>STEP {s.n}</div>
                  <div style={{ fontSize: "clamp(13px,1.4vw,16px)", fontWeight: 700, color: "#111827", marginBottom: 7 }}>{s.title}</div>
                  <div style={{ fontSize: "clamp(11px,1.1vw,13px)", color: "#6b7280", lineHeight: 1.65 }}>{s.desc}</div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </div>
      </section>

      {/* ── ENGINE TABS ───────────────────────────────────── */}
      <section className="section-pad" style={{ padding: "80px 52px", maxWidth: 960, margin: "0 auto" }}>
        <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ textAlign: "center", marginBottom: 40 }}>
          <h2 style={{ fontSize: "clamp(24px,3.5vw,42px)", fontWeight: 700, letterSpacing: "-0.04em", marginBottom: 10 }}>Two Powerful Engines</h2>
          <p style={{ fontSize: 15, color: "#6b7280" }}>Both included in every plan.</p>
        </motion.div>
        <div className="tab-row" style={{ display: "flex", gap: 8, justifyContent: "center", marginBottom: 28, flexWrap: "wrap" }}>
          {ENGINES.map((e, i) => (
            <motion.button key={i} whileTap={{ scale: 0.95 }} onClick={() => setActiveEngine(i)}
              style={{ display: "flex", alignItems: "center", gap: 8, padding: "11px 22px", borderRadius: 12, border: `2px solid ${activeEngine === i ? P : "#e5e7eb"}`, background: activeEngine === i ? PL : "white", color: activeEngine === i ? P : "#6b7280", fontWeight: 700, fontSize: 13, cursor: "pointer", transition: "all 0.22s" }}>
              {e.icon} {e.name}
            </motion.button>
          ))}
        </div>
        <AnimatePresence mode="wait">
          <motion.div key={activeEngine} initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.32, ease: [0.22, 1, 0.36, 1] }}
            className="engine-grid"
            style={{ background: "white", border: `2px solid ${P}20`, borderRadius: 24, padding: "36px", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 36, alignItems: "center", boxShadow: `0 8px 32px ${P}0a` }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: PL, border: `1.5px solid ${P}33`, display: "flex", alignItems: "center", justifyContent: "center", color: P }}>{ENGINES[activeEngine].icon}</div>
                <h3 style={{ fontSize: "clamp(15px,1.6vw,19px)", fontWeight: 700, color: "#111827" }}>{ENGINES[activeEngine].name}</h3>
              </div>
              <p style={{ fontSize: 14, color: "#6b7280", lineHeight: 1.76, marginBottom: 22 }}>{ENGINES[activeEngine].desc}</p>
              <MagBtn onClick={() => router.push("/auth")} style={{ fontSize: 13, padding: "11px 22px", borderRadius: 10 }}>
                Try {ENGINES[activeEngine].name.split(" ")[0]} Engine <ArrowForwardIcon sx={{ fontSize: 14 }} />
              </MagBtn>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {ENGINES[activeEngine].features.map((f, i) => (
                <motion.div key={f} initial={{ opacity: 0, x: 18 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
                  style={{ display: "flex", alignItems: "center", gap: 10, background: PL, borderRadius: 10, padding: "11px 14px" }}>
                  <CheckCircleIcon sx={{ fontSize: 16, color: P, flexShrink: 0 }} />
                  <span style={{ fontSize: 13, fontWeight: 600, color: "#374151" }}>{f}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>
      </section>

      {/* ── COMPARISON TABLE ──────────────────────────────── */}
      <section className="section-pad" style={{ padding: "20px 52px 80px", maxWidth: 860, margin: "0 auto" }}>
        <motion.div initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: "clamp(22px,3.5vw,38px)", fontWeight: 700, letterSpacing: "-0.04em", textAlign: "center", marginBottom: 8 }}>Manual vs Visual Engine</h2>
        </motion.div>
        <div style={{ background: "white", border: "1px solid #e5e7eb", borderRadius: 20, overflow: "hidden", boxShadow: "0 4px 16px rgba(0,0,0,0.05)" }}>
          <div className="compare-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", background: "#f9fafb", padding: "12px 20px", borderBottom: "1px solid #e5e7eb" }}>
            {["Metric", "Manual Workflow", "Visual Engine"].map((h, i) => (
              <span key={h} style={{ fontSize: 11, fontWeight: 700, color: i === 1 ? "#ef4444" : i === 2 ? P : "#374151", letterSpacing: "0.06em", textTransform: "uppercase" }}>{h}</span>
            ))}
          </div>
          <div style={{ padding: "0 8px" }}>
            {COMPARE.map((row, i) => <CompareBar key={i} {...row} />)}
          </div>
        </div>
      </section>

      {/* ── CTA ───────────────────────────────────────────── */}
      <section className="section-pad" style={{ padding: "40px 52px 100px" }}>
        <motion.div initial={{ opacity: 0, y: 48 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
          className="cta-pad"
          style={{ maxWidth: 780, margin: "0 auto", background: `linear-gradient(135deg,${P},#7c3aed 50%,#9333ea)`, borderRadius: 32, padding: "72px 56px", textAlign: "center", position: "relative", overflow: "hidden", boxShadow: `0 40px 100px -30px ${P}66` }}>
          <div style={{ position: "absolute", top: -80, right: -80, width: 300, height: 300, borderRadius: "50%", background: "rgba(255,255,255,0.07)", pointerEvents: "none" }} />
          <div style={{ position: "absolute", bottom: -60, left: -60, width: 240, height: 240, borderRadius: "50%", background: "rgba(255,255,255,0.05)", pointerEvents: "none" }} />
          <div style={{ position: "absolute", top: "50%", left: "50%", width: 600, height: 600, borderRadius: "50%", border: "1px solid rgba(255,255,255,0.06)", transform: "translate(-50%,-50%)", animation: "spin-slow 22s linear infinite", pointerEvents: "none" }} />
          <div style={{ position: "absolute", top: "50%", left: "50%", width: 360, height: 360, borderRadius: "50%", border: "1px solid rgba(255,255,255,0.04)", transform: "translate(-50%,-50%)", animation: "spin-slow 14s linear infinite reverse", pointerEvents: "none" }} />
          <TwinkleStars />

          <motion.div animate={{ scale: [1, 1.08, 1] }} transition={{ duration: 2.5, repeat: Infinity }}
            style={{ width: 60, height: 60, borderRadius: "50%", background: "rgba(255,255,255,0.15)", margin: "0 auto 22px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <RocketLaunchIcon sx={{ fontSize: 28, color: "white" }} />
          </motion.div>

          <h2 style={{ fontSize: "clamp(24px,4vw,44px)", fontWeight: 700, color: "white", letterSpacing: "-0.04em", lineHeight: 1.1, marginBottom: 14 }}>
            Start With 2 Free Generations
          </h2>
          <p style={{ fontSize: "clamp(14px,1.4vw,17px)", color: "rgba(255,255,255,0.72)", maxWidth: 420, margin: "0 auto 40px", lineHeight: 1.65 }}>
            No account. No credit card. Upload your image and watch the AI generate every format in seconds.
          </p>

          <MagBtn onClick={handleCTA} style={{ background: "white", color: P, fontSize: "clamp(14px,1.3vw,17px)", padding: "17px 48px", borderRadius: 14, fontWeight: 700, boxShadow: "0 8px 32px -8px rgba(0,0,0,0.22)", border: "none" }}>
            Try Free Now <ArrowForwardIcon sx={{ fontSize: 17 }} />
          </MagBtn>

          <div style={{ marginTop: 18, fontSize: 12, color: "rgba(255,255,255,0.42)" }}>Then from $29/month · Cancel anytime</div>
          <div style={{ display: "flex", gap: 8, justifyContent: "center", marginTop: 24, flexWrap: "wrap" }}>
            {["47+ formats", "Both engines", "Full resolution", "Instant ZIP"].map(t => (
              <div key={t} style={{ background: "rgba(255,255,255,0.12)", border: "1px solid rgba(255,255,255,0.18)", borderRadius: 100, padding: "5px 12px", fontSize: 11, fontWeight: 600, color: "rgba(255,255,255,0.82)", display: "flex", alignItems: "center", gap: 4 }}>
                <CheckCircleIcon sx={{ fontSize: 11 }} />{t}
              </div>
            ))}
          </div>
        </motion.div>
      </section>

      {/* ── FOOTER ────────────────────────────────────────── */}
      <footer className="section-pad footer-pad" style={{ borderTop: "1px solid #f3f4f6", padding: "36px 52px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 14 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 26, height: 26, borderRadius: 7, background: `linear-gradient(135deg,${P},#7c3aed)`, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <AutoAwesomeIcon sx={{ fontSize: 12, color: "white" }} />
          </div>
          <span style={{ fontSize: 13, color: "#9ca3af" }}>Visual Engine · AI Image Adaptation · 2026</span>
        </div>
        <div style={{ display: "flex", gap: 22, flexWrap: "wrap" }}>
          {["Privacy Policy", "Terms of Service", "Contact Sales"].map(l => (
            <span key={l} style={{ fontSize: 12, color: "#9ca3af", cursor: "pointer", transition: "color 0.15s" }}
              onMouseEnter={e => { (e.target as HTMLSpanElement).style.color = P; }}
              onMouseLeave={e => { (e.target as HTMLSpanElement).style.color = "#9ca3af"; }}>{l}</span>
          ))}
        </div>
      </footer>
    </div>
  );
}
