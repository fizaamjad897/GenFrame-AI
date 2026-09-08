"use client";
import React, { useState, useRef, useEffect } from "react";
import { motion, useInView, useScroll, useTransform, AnimatePresence } from "motion/react";
import { useRouter } from "next/navigation";
import { useAuth } from "./context/AuthContext";
import { CREAM, CREAM_DEEP, INK, PANEL, PANEL_LINE, TEXT_MUTED_L, TEXT_MUTED_D, BORDER_L, BORDER_D, ACCENT, GOOD, BAD, DISPLAY, BODY, MONO, ease } from "./theme/terminal";
import GridMark from "./theme/GridMark";
import CropIcon from "@mui/icons-material/Crop";
import TimerOffIcon from "@mui/icons-material/TimerOff";
import VerifiedIcon from "@mui/icons-material/Verified";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
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
import ImageSearchIcon from "@mui/icons-material/ImageSearch";
import MenuIcon from "@mui/icons-material/Menu";
import CloseIcon from "@mui/icons-material/Close";
import StarIcon from "@mui/icons-material/Star";
import LockIcon from "@mui/icons-material/Lock";
import BoltIcon from "@mui/icons-material/Bolt";

/*
  IMPECCABLE DIRECTION — user-pinned reference (contentarchitecture.dev), replacing seed c3578073
  THESIS: Flat, technical, exact — a developer-tool register, not a soft SaaS hero
  or an industrial-craft pastiche. Two blocks, cream and near-black, nothing between.
  OWN-WORLD: cream/near-black two-tone flat blocks, dashed hairline module frames,
  monospace UI chrome (nav, tags, code-style log panels), one clean grotesk for
  headline and body, a single amber accent. Zero gradients, zero shadows, zero
  illustration, zero tilt.
  STORY: A media buyer sees the transform run as a literal log — decompose,
  recompose, ship — and believes this is an exact, inspectable engine, not a
  black box guess.
  FIRST VIEWPORT: dark hero over real desaturated video footage, headline at
  left, a dashed-frame line-numbered log panel at right running the actual
  demo as terminal output.
  FORM: user-pinned reference overrides the rolled Panel Catalog / Sketch
  Explainer directions. FINISH: unreviewed and undocumented is unfinished;
  this build ends with the finish review, the verdict, DESIGN.md, and every
  shipping raster carrying its provenance.
*/
const DIRECTION_CONTRACT = `
  IMPECCABLE DIRECTION form:user-pinned-reference (contentarchitecture.dev)
  THESIS Flat, technical, exact — a developer-tool register, not soft SaaS or industrial pastiche.
  OWN-WORLD cream/near-black two-tone, dashed hairline frames, monospace UI chrome, one grotesk, one accent.
  STORY A media buyer watches the transform run as a literal log: decompose, recompose, ship.
  FIRST-VIEWPORT cream hero, headline left, dark line-numbered log panel right running the real demo.
  FORM user-pinned reference, overrides the rolled directions.
  FINISH unreviewed and undocumented is unfinished; this build ends with the finish review,
  the verdict, DESIGN.md, and every shipping raster carrying its provenance.
`;

const SPEC_CODES = [
  { code: "OOH_1836X432", ratio: "4.25:1" },
  { code: "QMS_1440X360", ratio: "4:1" },
  { code: "OOH_768X1152", ratio: "2:3" },
  { code: "QMS_2640X288", ratio: "9.2:1" },
];

/* ── useBreakpoint ──────────────────────────────────────────────── */
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

/* ── FadeIn: the one authored entrance moment — quick, flat, no tilt ── */
function FadeIn({ children, delay = 0, style }: { children: React.ReactNode; delay?: number; style?: React.CSSProperties }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.4, delay, ease }} style={style}>
      {children}
    </motion.div>
  );
}

/* ── PopIn: guaranteed mount animation for always-visible hero content ── */
function PopIn({ children, delay = 0, style }: { children: React.ReactNode; delay?: number; style?: React.CSSProperties }) {
  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease }} style={style}>
      {children}
    </motion.div>
  );
}

/* ── Tag: small mono bordered label ───────────────────────────────── */
function Tag({ children, tone = "light", accent = false }: { children: React.ReactNode; tone?: "light" | "dark"; accent?: boolean }) {
  const border = accent ? ACCENT : tone === "dark" ? BORDER_D : BORDER_L;
  const color = accent ? ACCENT : tone === "dark" ? TEXT_MUTED_D : TEXT_MUTED_L;
  return (
    <span style={{ fontFamily: MONO, fontSize: 10.5, fontWeight: 500, letterSpacing: "0.04em", color, border: `1px solid ${border}`, borderRadius: 3, padding: "3px 8px", whiteSpace: "nowrap" }}>
      {children}
    </span>
  );
}

/* ── StatusDot: flat status readout ──────────────────────────────── */
function StatusDot({ state }: { state: "idle" | "running" | "done" }) {
  const label = state === "done" ? "complete" : state === "running" ? "running" : "idle";
  const color = state === "done" ? GOOD : state === "running" ? ACCENT : TEXT_MUTED_D;
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 6, fontFamily: MONO, fontSize: 10.5, color }}>
      <motion.span animate={state === "running" ? { opacity: [1, 0.3, 1] } : { opacity: 1 }} transition={{ duration: 0.9, repeat: state === "running" ? Infinity : 0 }}
        style={{ width: 6, height: 6, borderRadius: "50%", background: color, display: "inline-block" }} />
      {label}
    </span>
  );
}

/* ── HeroVideo: real footage behind the hero, desaturated to hold the palette ── */
function HeroVideo() {
  const vidRef = useRef<HTMLVideoElement>(null);
  useEffect(() => {
    const v = vidRef.current;
    if (v) v.playbackRate = 1.3;
  }, []);
  return (
    <video ref={vidRef} autoPlay muted loop playsInline
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", zIndex: 0, opacity: 0.6, filter: "grayscale(0.4) brightness(0.5) contrast(1.08)" }}>
      <source src="/bg-video.mp4" type="video/mp4" />
    </video>
  );
}

/* ── Counter: count-up on scroll into view — the one numeric motion beat ── */
function Counter({ to, suffix = "" }: { to: number; suffix?: string }) {
  const [v, setV] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  useEffect(() => {
    if (!inView) return;
    const t0 = Date.now(), dur = 1100;
    const tick = () => {
      const p = Math.min((Date.now() - t0) / dur, 1);
      setV(Math.round(to * (1 - Math.pow(1 - p, 3))));
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [inView, to]);
  return <span ref={ref}>{v}{suffix}</span>;
}

/* ── TerminalDemo: the interactive demo as a line-numbered log ──────── */
const LOAD_STEPS = ["decomposing layers", "isolating subject + logo", "recomposing to spec", "writing output panels"];
const FRAME_STOPS = [
  { key: "story",     label: "9:16",  ratio: 9 / 16,  code: "STORY_916" },
  { key: "portrait",  label: "3:4",   ratio: 3 / 4,   code: "PORT_034" },
  { key: "square",    label: "1:1",   ratio: 1,       code: "SQ_101" },
  { key: "landscape", label: "16:9",  ratio: 16 / 9,  code: "LAND_169" },
  { key: "wide",      label: "21:9",  ratio: 21 / 9,  code: "UWIDE_219" },
];

function RulerPull({ index, onChange }: { index: number; onChange: (i: number) => void }) {
  const trackRef = useRef<HTMLDivElement>(null);
  const drag = useRef(false);
  const move = (cx: number) => {
    if (!drag.current || !trackRef.current) return;
    const rc = trackRef.current.getBoundingClientRect();
    const pct = Math.max(0, Math.min(1, (cx - rc.left) / rc.width));
    onChange(Math.round(pct * (FRAME_STOPS.length - 1)));
  };
  return (
    <div ref={trackRef} onPointerDown={e => { drag.current = true; (e.target as Element).setPointerCapture?.(e.pointerId); move(e.clientX); }}
      onPointerUp={() => { drag.current = false; }} onPointerMove={e => move(e.clientX)}
      style={{ position: "relative", height: 28, cursor: "ew-resize", touchAction: "none" }}>
      <div style={{ position: "absolute", top: 13, left: 0, right: 0, height: 1, background: BORDER_D }} />
      {FRAME_STOPS.map((f, i) => (
        <div key={f.key} style={{ position: "absolute", top: 0, left: `${(i / (FRAME_STOPS.length - 1)) * 100}%`, transform: "translateX(-50%)", textAlign: "center" }}>
          <div style={{ width: 1, height: 12, background: i === index ? ACCENT : TEXT_MUTED_D, margin: "0 auto" }} />
          <div style={{ fontFamily: MONO, fontSize: 8.5, fontWeight: i === index ? 700 : 400, color: i === index ? ACCENT : TEXT_MUTED_D, marginTop: 4 }}>{f.label}</div>
        </div>
      ))}
      <motion.div animate={{ left: `${(index / (FRAME_STOPS.length - 1)) * 100}%` }} transition={{ type: "spring", stiffness: 380, damping: 30 }}
        style={{ position: "absolute", top: 8, width: 8, height: 8, background: ACCENT, transform: "translateX(-50%)" }} />
    </div>
  );
}

function TerminalDemo() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [phase, setPhase] = useState<"idle" | "loading" | "done">("idle");
  const [srcUrl, setSrcUrl] = useState("");
  const [loadStep, setLoadStep] = useState(0);
  const [frameIdx, setFrameIdx] = useState(2);
  const [dragging, setDragging] = useState(false);

  const runFake = (file: File) => {
    if (!file.type.startsWith("image/")) return;
    const url = URL.createObjectURL(file);
    setSrcUrl(url);
    setPhase("loading");
    setLoadStep(0);
    let step = 0;
    const iv = setInterval(() => {
      step++;
      setLoadStep(step);
      if (step >= LOAD_STEPS.length - 1) { clearInterval(iv); setTimeout(() => setPhase("done"), 450); }
    }, 650);
  };
  const reset = () => { if (srcUrl) URL.revokeObjectURL(srcUrl); setSrcUrl(""); setPhase("idle"); setLoadStep(0); };
  const frame = FRAME_STOPS[frameIdx];

  return (
    <div style={{ background: PANEL, border: `1px solid rgba(255,255,255,0.32)`, borderRadius: 3, boxShadow: "0 24px 60px -20px rgba(0,0,0,0.6)" }}>
      <div style={{ borderBottom: `1px solid ${PANEL_LINE}`, padding: "10px 16px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_D, letterSpacing: "0.04em" }}>TRANSFORM_LOG</span>
        <StatusDot state={phase === "idle" ? "idle" : phase === "loading" ? "running" : "done"} />
      </div>

      <div style={{ padding: "16px 16px 18px" }}>
        {phase === "idle" && (
          <div>
            <div style={{ fontFamily: MONO, fontSize: 11.5, lineHeight: 2, marginBottom: 14 }}>
              <div><span style={{ color: TEXT_MUTED_D }}>001  </span><span style={{ color: "#6f6a5c" }}>awaiting source image</span></div>
              <div><span style={{ color: TEXT_MUTED_D }}>002  </span><span style={{ color: "#6f6a5c" }}>target {frame.code} · {frame.label}</span></div>
            </div>
            <div
              onDrop={e => { e.preventDefault(); setDragging(false); const f = e.dataTransfer.files[0]; if (f) runFake(f); }}
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onClick={() => fileInputRef.current?.click()}
              style={{
                width: "100%", maxWidth: 220, aspectRatio: String(frame.ratio), margin: "0 auto",
                background: dragging ? "#232326" : "transparent",
                border: `1px solid ${dragging ? ACCENT : BORDER_D}`,
                borderRadius: 2, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                cursor: "pointer", gap: 6, transition: "aspect-ratio 0.28s ease, border-color 0.2s",
              }}>
              <CloudUploadIcon sx={{ fontSize: 22, color: dragging ? ACCENT : TEXT_MUTED_D }} />
              <span style={{ fontFamily: MONO, fontSize: 10.5, color: dragging ? ACCENT : TEXT_MUTED_D, textAlign: "center", padding: "0 12px" }}>
                {dragging ? "release" : "drop or click"}
              </span>
            </div>

            <div style={{ marginTop: 16, maxWidth: 260, margin: "16px auto 0" }}>
              <RulerPull index={frameIdx} onChange={setFrameIdx} />
            </div>

            <button onClick={() => fileInputRef.current?.click()}
              style={{ marginTop: 16, width: "100%", background: ACCENT, color: INK, border: "none", borderRadius: 2, padding: "11px", fontFamily: MONO, fontSize: 11.5, fontWeight: 600, cursor: "pointer" }}>
              RUN TRANSFORM
            </button>
          </div>
        )}

        {phase === "loading" && (
          <div style={{ fontFamily: MONO, fontSize: 11.5, lineHeight: 2, minHeight: 226, paddingTop: 4 }}>
            <div><span style={{ color: TEXT_MUTED_D }}>001  </span><span style={{ color: "#6f6a5c" }}>source pinned</span></div>
            {LOAD_STEPS.map((s, i) => (
              <div key={s} style={{ opacity: i <= loadStep ? 1 : 0.25 }}>
                <span style={{ color: TEXT_MUTED_D }}>{String(i + 2).padStart(3, "0")}  </span>
                <span style={{ color: i === loadStep ? ACCENT : "#6f6a5c" }}>{s}{i === loadStep ? " …" : i < loadStep ? " ✓" : ""}</span>
              </div>
            ))}
          </div>
        )}

        {phase === "done" && srcUrl && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div style={{ fontFamily: MONO, fontSize: 11.5, lineHeight: 2, marginBottom: 12 }}>
              <div><span style={{ color: TEXT_MUTED_D }}>001  </span><span style={{ color: GOOD }}>4 panels written</span></div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 6 }}>
              {[{ label: "STORY_916", pos: "center top" }, { label: "SQ_101", pos: "center center" }].map((f, i) => (
                <div key={i} onClick={() => router.push("/auth?tab=signup&redirect=/pricing")}
                  style={{ height: 92, position: "relative", borderRadius: 2, overflow: "hidden", cursor: "pointer", border: `1px solid ${PANEL_LINE}` }}>
                  <img src={srcUrl} alt="" style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", objectPosition: f.pos, filter: "blur(10px) saturate(1.05)", transform: "scale(1.12)" }} />
                  <div style={{ position: "absolute", inset: 0, background: "rgba(20,18,13,0.5)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <LockIcon sx={{ fontSize: 17, color: TEXT_MUTED_D }} />
                  </div>
                  <div style={{ position: "absolute", bottom: 4, left: 4, fontFamily: MONO, fontSize: 8, color: TEXT_MUTED_D }}>{f.label}</div>
                </div>
              ))}
            </div>
            <button onClick={() => router.push("/auth?tab=signup&redirect=/pricing")}
              style={{ width: "100%", background: ACCENT, color: INK, border: "none", borderRadius: 2, padding: "11px", fontFamily: MONO, fontSize: 11.5, fontWeight: 600, cursor: "pointer", marginTop: 6 }}>
              UNLOCK FULL RESOLUTION
            </button>
            <button onClick={reset} style={{ width: "100%", background: "transparent", color: TEXT_MUTED_D, border: "none", padding: "8px", fontFamily: MONO, fontSize: 10.5, cursor: "pointer" }}>
              run another
            </button>
          </motion.div>
        )}
      </div>
      <input ref={fileInputRef} type="file" accept="image/*" style={{ display: "none" }} onChange={e => { const f = e.target.files?.[0]; if (f) runFake(f); if (e.target) e.target.value = ""; }} />
    </div>
  );
}

/* ── SpecPlate: stats as a flat ruled row ─────────────────────────── */
function SpecPlate() {
  const rows = [
    { to: 47,  suffix: "+",  label: "format specs" },
    { to: 4,   suffix: "s",  label: "avg turnaround" },
    { to: 98,  suffix: "%",  label: "spec accuracy" },
    { to: 10,  suffix: "K+", label: "panels shipped" },
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)" }} className="spec-grid">
      {rows.map((r, i) => (
        <div key={r.label} style={{ padding: "20px 14px", borderLeft: i > 0 ? `1px solid ${BORDER_D}` : "none" }}>
          <div style={{ fontFamily: MONO, fontSize: 21, fontWeight: 600, color: CREAM }}><Counter to={r.to} suffix={r.suffix} /></div>
          <div style={{ fontFamily: MONO, fontSize: 10, color: TEXT_MUTED_D, marginTop: 4 }}>{r.label}</div>
        </div>
      ))}
    </div>
  );
}

/* ── ProblemPanel: flat bordered card, no tilt ────────────────────── */
function ProblemPanel({ Icon, title, short, detail, expanded, onToggle }: { Icon: React.ElementType; title: string; short: string; detail: string; expanded: boolean; onToggle: () => void }) {
  return (
    <div onClick={onToggle} style={{ border: `1px solid ${BORDER_L}`, borderRadius: 2, padding: "22px 20px", cursor: "pointer", background: expanded ? CREAM_DEEP : "transparent", transition: "background 0.2s" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
        <Icon sx={{ fontSize: 20, color: INK, opacity: 0.7 }} />
        <Tag>issue</Tag>
      </div>
      <h3 style={{ fontFamily: DISPLAY, fontSize: 18, fontWeight: 600, color: INK, marginBottom: 6, letterSpacing: "-0.01em" }}>{title}</h3>
      <p style={{ fontFamily: BODY, fontSize: 13, color: TEXT_MUTED_L, lineHeight: 1.6 }}>{short}</p>
      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
            <div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${BORDER_L}` }}>
              <p style={{ fontFamily: BODY, fontSize: 12.5, color: TEXT_MUTED_L, lineHeight: 1.7 }}>{detail}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ── RouteBoard: click a tag, the viewer swaps — no dragging ─────── */
const ROUTE_TAGS = [
  { label: "manual crop",  w: 130, h: 130, manual: true  },
  { label: "story 9:16",   w: 108, h: 192, manual: false },
  { label: "banner 4:1",   w: 240, h: 60,  manual: false },
  { label: "square 1:1",   w: 170, h: 170, manual: false },
  { label: "youtube 16:9", w: 220, h: 124, manual: false },
  { label: "x banner 3:1", w: 210, h: 70,  manual: false },
];

function RouteBoard() {
  const [active, setActive] = useState(1);
  const tag = ROUTE_TAGS[active];
  return (
    <div>
      <div style={{ display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap", marginBottom: 20 }}>
        {ROUTE_TAGS.map((t, i) => (
          <button key={t.label} onClick={() => setActive(i)}
            style={{
              background: active === i ? (t.manual ? BAD : ACCENT) : "transparent",
              border: `1px solid ${active === i ? (t.manual ? BAD : ACCENT) : BORDER_D}`,
              color: active === i ? INK : TEXT_MUTED_D, borderRadius: 2, padding: "7px 13px",
              fontFamily: MONO, fontSize: 10.5, cursor: "pointer", transition: "background 0.15s, border-color 0.15s",
            }}>
            {t.label}
          </button>
        ))}
      </div>
      <div style={{ position: "relative", minHeight: 300, borderRadius: 3, border: `1px solid ${BORDER_D}`, background: PANEL, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ position: "absolute", top: 14, left: 16, fontFamily: MONO, fontSize: 10, color: tag.manual ? "#c47a5f" : TEXT_MUTED_D }}>
          {tag.manual ? "manual_workflow" : "recreative_output"}
        </div>
        <AnimatePresence mode="wait">
          <motion.div key={active} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }} style={{ textAlign: "center", padding: "36px 24px" }}>
            {tag.manual ? (
              <>
                <div style={{ width: 140, height: 140, margin: "0 auto 14px", border: `1px solid ${PANEL_LINE}`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <CropIcon sx={{ fontSize: 34, color: TEXT_MUTED_D }} />
                </div>
                <Tag tone="dark">crop failed</Tag>
              </>
            ) : (
              <>
                <div style={{ width: tag.w, height: tag.h, margin: "0 auto 14px", background: PANEL_LINE, border: `1px solid ${ACCENT}66`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <div style={{ width: "60%", height: "60%", background: `${ACCENT}22` }} />
                </div>
                <Tag tone="dark" accent>spec cleared</Tag>
              </>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

/* ── RouteDiagram: flat source -> engine -> panel stack ───────────── */
function RouteDiagram() {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true });
  const outs = SPEC_CODES.slice(0, 4);
  return (
    <svg ref={ref} viewBox="0 0 480 220" style={{ width: "100%", height: "auto", overflow: "visible" }}>
      <motion.rect x="10" y="60" width="96" height="96" fill="none" stroke={BORDER_D} strokeWidth="1" initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} />
      {/* source: a small living illustration of the layers being decomposed.
          Each layer is a plain static rect wrapped in its own <motion.g>; the
          group's transform (not the rect's x/y attribute) carries the motion,
          which is the only unambiguous way to animate position on SVG shapes. */}
      <motion.g initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 0.15, duration: 0.4 }}>
        <rect x="22" y="70" width="72" height="72" fill={BORDER_D} opacity="0.5" />
        <motion.g animate={inView ? { y: [0, -4, 0] } : {}} transition={{ duration: 3.2, repeat: Infinity, ease: "easeInOut", delay: 0.6 }}>
          <rect x="30" y="78" width="42" height="42" fill={`${ACCENT}33`} stroke={ACCENT} strokeWidth="0.75" />
        </motion.g>
        <motion.g animate={inView ? { y: [0, -4, 0] } : {}} transition={{ duration: 2.6, repeat: Infinity, ease: "easeInOut", delay: 1.1 }}>
          <rect x="76" y="118" width="14" height="14" fill={CREAM} opacity="0.7" />
        </motion.g>
        <motion.g animate={inView ? { y: [0, -4, 0] } : {}} transition={{ duration: 2.9, repeat: Infinity, ease: "easeInOut", delay: 0.3 }}>
          <rect x="30" y="128" width="38" height="6" fill={TEXT_MUTED_D} />
        </motion.g>
        {/* scan sweep — the engine reading the source */}
        <motion.g animate={inView ? { y: [70, 142, 70], opacity: [0, 0.9, 0.9, 0] } : {}} transition={{ duration: 3.6, repeat: Infinity, ease: "linear", delay: 1.6 }}>
          <line x1="22" x2="94" y1="0" y2="0" stroke={ACCENT} strokeWidth="1" />
        </motion.g>
      </motion.g>
      <motion.text x="58" y="176" textAnchor="middle" fontFamily={MONO} fontSize="9" fill={TEXT_MUTED_D} initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 0.2 }}>source</motion.text>
      <motion.path d="M 110 108 H 168" stroke={ACCENT} strokeWidth="1" initial={{ pathLength: 0 }} animate={inView ? { pathLength: 1 } : {}} transition={{ delay: 0.4, duration: 0.35 }} />
      <motion.rect x="172" y="86" width="44" height="44" fill="none" stroke={ACCENT} strokeWidth="1.5" initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 0.55 }} />
      <motion.rect x="172" y="86" width="44" height="44" fill="none" stroke={ACCENT} strokeWidth="1"
        animate={inView ? { opacity: [0.15, 0.6, 0.15], scale: [1, 1.12, 1] } : {}} transition={{ duration: 1.8, repeat: Infinity, ease: "easeInOut", delay: 0.8 }}
        style={{ transformOrigin: "194px 108px" }} />
      <motion.text x="194" y="112" textAnchor="middle" fontFamily={MONO} fontSize="8" fill={ACCENT} initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 0.75 }}>engine</motion.text>
      {outs.map((o, i) => {
        const ty = 20 + i * 55;
        const d = `M 216 108 C 280 108 280 ${ty + 18} 340 ${ty + 18}`;
        return (
          <g key={o.code}>
            <motion.path d={d} fill="none" stroke={BORDER_D} strokeWidth="1"
              initial={{ pathLength: 0 }} animate={inView ? { pathLength: 1 } : {}} transition={{ delay: 0.9 + i * 0.1, duration: 0.4 }} />
            {/* flowing pulse: data in transit, one continuous ambient beat */}
            <motion.path d={d} fill="none" stroke={ACCENT} strokeWidth="1.4" strokeLinecap="round" strokeDasharray="3 9"
              initial={{ opacity: 0 }} animate={inView ? { opacity: [0, 0.9, 0.9, 0], strokeDashoffset: [0, -48] } : {}}
              transition={{ delay: 1.5 + i * 0.22, duration: 2.4, repeat: Infinity, repeatDelay: 0.6, ease: "linear" }} />
            <motion.g initial={{ opacity: 0 }} animate={inView ? { opacity: 1 } : {}} transition={{ delay: 1.15 + i * 0.1 }}>
              <rect x="340" y={ty} width="132" height="36" fill="none" stroke={BORDER_D} />
              <text x="350" y={ty + 15} fontFamily={MONO} fontSize="8" fontWeight="700" fill={CREAM}>{o.code}</text>
              <text x="350" y={ty + 27} fontFamily={MONO} fontSize="7" fill={TEXT_MUTED_D}>{o.ratio}</text>
              <motion.circle cx="462" cy={ty + 10} r="3" fill={ACCENT} initial={{ scale: 0 }} animate={inView ? { scale: 1 } : {}} transition={{ delay: 1.4 + i * 0.1 }} />
            </motion.g>
          </g>
        );
      })}
    </svg>
  );
}

/* ── SolutionPanel: flat bordered card ────────────────────────────── */
function SolutionPanel({ Icon, title, desc }: { Icon: React.ElementType; title: string; desc: string }) {
  return (
    <div style={{ border: `1px solid ${BORDER_D}`, borderRadius: 2, padding: "24px 22px", height: "100%" }}>
      <Icon sx={{ fontSize: 20, color: ACCENT, marginBottom: "14px" }} />
      <h3 style={{ fontFamily: DISPLAY, fontSize: 17, fontWeight: 600, color: CREAM, marginBottom: 8, letterSpacing: "-0.01em" }}>{title}</h3>
      <p style={{ fontFamily: BODY, fontSize: 13, color: TEXT_MUTED_D, lineHeight: 1.65 }}>{desc}</p>
    </div>
  );
}

/* ── StepStub: how-it-works, flat mono stage numbers ──────────────── */
function StepStub({ Icon, n, title, desc }: { Icon: React.ElementType; n: string; title: string; desc: string }) {
  return (
    <div className="step-item">
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
        <Icon sx={{ fontSize: 18, color: ACCENT }} />
        <span style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_L }}>step_{n}</span>
      </div>
      <div style={{ fontFamily: DISPLAY, fontSize: 16, fontWeight: 600, color: INK, marginBottom: 6 }}>{title}</div>
      <div style={{ fontFamily: BODY, fontSize: 12.5, color: TEXT_MUTED_L, lineHeight: 1.6 }}>{desc}</div>
    </div>
  );
}

/* ── EnginePanel: flat bordered job panel ─────────────────────────── */
function EnginePanel({ tone, tag, icon, name, desc, features, cta }: { tone: string; tag: string; icon: React.ReactNode; name: string; desc: React.ReactNode; features: string[]; cta: () => void }) {
  return (
    <div style={{ border: `1px solid ${BORDER_D}`, borderRadius: 2, padding: "28px", height: "100%", display: "flex", flexDirection: "column" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16, color: tone }}>
        {icon}
        <span style={{ fontFamily: MONO, fontSize: 10.5, color: tone }}>{tag}</span>
      </div>
      <h3 style={{ fontFamily: DISPLAY, fontSize: 19, fontWeight: 600, color: CREAM, marginBottom: 12 }}>{name}</h3>
      <p style={{ fontFamily: BODY, fontSize: 13, color: TEXT_MUTED_D, lineHeight: 1.65, marginBottom: 20 }}>{desc}</p>
      <div style={{ display: "flex", flexDirection: "column", gap: 7, flex: 1, marginBottom: 22 }}>
        {features.map(f => (
          <div key={f} style={{ fontFamily: MONO, fontSize: 11, color: TEXT_MUTED_D }}>· {f}</div>
        ))}
      </div>
      <button onClick={cta} style={{ width: "100%", background: "transparent", color: tone, border: `1px solid ${tone}`, borderRadius: 2, padding: "11px", fontFamily: MONO, fontSize: 11.5, fontWeight: 600, cursor: "pointer" }}>
        try {name.toLowerCase()} →
      </button>
    </div>
  );
}

/* ── Ledger: comparison table, flat ruled ─────────────────────────── */
function Ledger({ rows }: { rows: { label: string; manual: string; ai: string }[] }) {
  return (
    <div style={{ border: `1px solid ${BORDER_L}`, borderRadius: 2, overflow: "hidden" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 1fr", padding: "11px 18px", borderBottom: `1px solid ${BORDER_L}` }}>
        {["metric", "manual", "recreative"].map((h, i) => (
          <span key={h} style={{ fontFamily: MONO, fontSize: 10, color: i === 2 ? ACCENT : TEXT_MUTED_L }}>{h}</span>
        ))}
      </div>
      {rows.map((r, i) => (
        <div key={r.label} style={{ display: "grid", gridTemplateColumns: "1.2fr 1fr 1fr", padding: "12px 18px", borderTop: i > 0 ? `1px solid ${BORDER_L}` : "none", alignItems: "center" }}>
          <span style={{ fontFamily: BODY, fontSize: 13, color: INK }}>{r.label}</span>
          <span style={{ fontFamily: MONO, fontSize: 11.5, color: BAD }}>{r.manual}</span>
          <span style={{ fontFamily: MONO, fontSize: 11.5, color: GOOD, fontWeight: 600 }}>{r.ai}</span>
        </div>
      ))}
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════
   MAIN LANDING PAGE
════════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const router = useRouter();
  const { loading } = useAuth();
  const { isTablet } = useBreakpoint();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [expandedProblem, setExpandedProblem] = useState<number | null>(null);
  const { scrollY } = useScroll();
  const heroY = useTransform(scrollY, [0, 500], [0, -20]);

  if (loading) return null;

  const PROBLEMS = [
    { Icon: CropIcon,        title: "Format chaos",        short: "One creative → 47 manual resizes every campaign.", detail: "Your team spends 3–4 days per campaign manually cropping for every channel and OOH/QMS spec. Each format is a fresh battle with aspect ratios and composition." },
    { Icon: ImageSearchIcon, title: "Compromised quality",  short: "Cropped faces. Stretched logos. Broken layouts.",  detail: "Manual resizing destroys your creative. Subjects get cut off, logos distort, text overlaps. Every bad output damages brand perception." },
    { Icon: TimerOffIcon,    title: "Lost creative hours",  short: "Designers stuck resizing instead of creating.",     detail: "When your best designers burn hours on mechanical resizing, they're not doing strategy or ideation." },
  ];
  const SOLUTIONS = [
    { Icon: VerifiedIcon, title: "Brand integrity",   desc: "Logos stay crisp. Faces stay framed. Text stays readable — components are decomposed and recomposed, never regenerated." },
    { Icon: BoltIcon,     title: "Instant scaling",   desc: "Upload once. Get all 47+ formats in seconds. What took your team 4 days now takes 4 seconds." },
    { Icon: TaskAltIcon,  title: "Spec-exact output", desc: "Real OOH billboard and QMS digital-screen dimensions, not generic aspect-ratio buckets — pixel-exact to the media owner's sheet." },
  ];
  const STEPS = [
    { Icon: CloudUploadIcon, n: "01", title: "Pin source",           desc: "Drop your highest-quality creative. PNG, JPG, or WEBP, any dimensions." },
    { Icon: PsychologyIcon,  n: "02", title: "Decompose & recompose", desc: "The engine isolates every component and rebuilds it to spec for each target." },
    { Icon: FileDownloadIcon,n: "03", title: "Ship every panel",     desc: "All 47+ formats, pixel-perfect and production-ready. ZIP or individual files." },
  ];
  const COMPARE = [
    { label: "Time per format",      manual: "30–60 min",       ai: "< 1 sec" },
    { label: "Batch all formats",    manual: "multiple days",   ai: "4 sec total" },
    { label: "Subject preservation", manual: "manual crop",     ai: "component-exact" },
    { label: "OOH/QMS specs",        manual: "manual lookup",   ai: "built-in library" },
    { label: "Cost per format",      manual: "$15–50 designer", ai: "< $0.01" },
  ];

  return (
    <div style={{ background: CREAM, fontFamily: BODY, color: INK, overflowX: "hidden" }}>
      <div dangerouslySetInnerHTML={{ __html: `<!--${DIRECTION_CONTRACT}-->` }} />

      <style>{`
        *{box-sizing:border-box;}
        .nav-link{font-family:${MONO};font-size:11.5px;color:${TEXT_MUTED_D};cursor:pointer;padding:4px 0;border-bottom:1px solid transparent;transition:all 0.15s;}
        .nav-link:hover{color:${CREAM};border-bottom-color:${ACCENT};}
        ::selection{background-color:${ACCENT};color:${INK};}
        @media(max-width:639px){
          .hero-grid{grid-template-columns:1fr !important;gap:32px !important;}
          .spec-grid{grid-template-columns:1fr 1fr !important;}
          .three-grid{grid-template-columns:1fr !important;}
          .engine-grid{grid-template-columns:1fr !important;}
          .section-pad{padding:48px 18px !important;}
          .hero-pad{padding:28px 18px 36px !important;}
          .nav-pad{padding:0 18px !important;}
        }
        @media(min-width:640px) and (max-width:1023px){
          .hero-grid{grid-template-columns:1fr !important;}
          .section-pad{padding:64px 32px !important;}
        }
        @media(max-width:1023px){.hide-tablet{display:none !important;}}
        .mobile-nav-overlay{position:fixed;inset:0;background:${INK};z-index:200;display:flex;flex-direction:column;padding:20px;}
        .step-item{padding:0 18px;border-left:1px solid ${BORDER_L};}
        .step-item:first-child{border-left:none;padding-left:0;}
        @media(max-width:639px){
          .step-item{border-left:none !important;border-top:1px solid ${BORDER_L};padding:18px 0 0 !important;margin-top:18px;}
          .step-item:first-child{border-top:none;padding-top:0 !important;margin-top:0;}
        }
      `}</style>

      {/* ── MOBILE NAV ── */}
      <AnimatePresence>
        {mobileNavOpen && (
          <motion.div className="mobile-nav-overlay" initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }} transition={{ duration: 0.25, ease }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 48 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <GridMark size={24} />
                <span style={{ fontFamily: DISPLAY, fontSize: 16, fontWeight: 600, color: CREAM }}>Recreative AI</span>
              </div>
              <button onClick={() => setMobileNavOpen(false)} style={{ background: "transparent", border: `1px solid ${BORDER_D}`, borderRadius: 2, width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer" }}>
                <CloseIcon sx={{ color: CREAM }} />
              </button>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 4, flex: 1 }}>
              {["Pricing", "Features", "About"].map(l => (
                <button key={l} onClick={() => { setMobileNavOpen(false); if (l === "Pricing") router.push("/auth?tab=signup&redirect=/pricing"); }}
                  style={{ background: "transparent", border: "none", borderBottom: `1px solid ${PANEL_LINE}`, padding: "16px 0", fontFamily: DISPLAY, fontSize: 20, fontWeight: 600, color: CREAM, textAlign: "left", cursor: "pointer" }}>{l}</button>
              ))}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <button onClick={() => { setMobileNavOpen(false); router.push("/auth?tab=login"); }} style={{ textAlign: "center", padding: 13, background: "transparent", border: `1px solid ${BORDER_D}`, borderRadius: 2, color: CREAM, fontFamily: MONO, fontSize: 12.5, cursor: "pointer" }}>sign in</button>
              <button onClick={() => { setMobileNavOpen(false); router.push("/auth?tab=signup&redirect=/pricing"); }}
                style={{ background: ACCENT, color: INK, border: "none", borderRadius: 2, padding: 13, fontFamily: MONO, fontWeight: 600, fontSize: 12.5, cursor: "pointer" }}>get started</button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── NAV ── */}
      <nav className="nav-pad" style={{ position: "sticky", top: 0, zIndex: 100, background: CREAM, borderBottom: `1px solid ${BORDER_L}`, padding: "0 44px", height: 58, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <GridMark size={26} />
          <span style={{ fontFamily: DISPLAY, fontSize: 15, fontWeight: 600, color: INK }}>Recreative AI</span>
        </div>
        <div className="hide-tablet" style={{ display: "flex", gap: 26 }}>
          {["Pricing", "Features", "About"].map(l => <span key={l} className="nav-link" style={{ color: TEXT_MUTED_L }} onClick={() => l === "Pricing" && router.push("/auth?tab=signup&redirect=/pricing")}>{l}</span>)}
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div className="hide-tablet" style={{ display: "flex", gap: 10 }}>
            <button onClick={() => router.push("/auth?tab=login")} style={{ background: "transparent", border: `1px solid ${BORDER_L}`, color: INK, borderRadius: 2, padding: "8px 16px", fontFamily: MONO, fontSize: 11.5, cursor: "pointer" }}>sign in</button>
            <button onClick={() => router.push("/auth?tab=signup&redirect=/pricing")}
              style={{ background: INK, color: CREAM, border: "none", borderRadius: 2, padding: "8px 16px", fontFamily: MONO, fontSize: 11.5, fontWeight: 600, cursor: "pointer" }}>get started</button>
          </div>
          <button className="show-mobile-btn" style={{ background: "transparent", border: `1px solid ${BORDER_L}`, borderRadius: 2, width: 36, height: 36, alignItems: "center", justifyContent: "center", cursor: "pointer", display: "none" }} onClick={() => setMobileNavOpen(true)}>
            <MenuIcon sx={{ color: INK }} />
          </button>
          <style>{`.show-mobile-btn{display:none!important;}@media(max-width:1023px){.show-mobile-btn{display:flex!important;}}`}</style>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section style={{ position: "relative", overflow: "hidden", background: INK }}>
        <HeroVideo />
        <div style={{ position: "absolute", inset: 0, zIndex: 1, background: `linear-gradient(100deg, ${INK} 0%, rgba(17,24,39,0.88) 46%, rgba(17,24,39,0.58) 100%)` }} />

        <motion.div style={{ y: heroY, position: "relative", zIndex: 2, width: "100%", maxWidth: 1240, margin: "0 auto", display: "grid", gridTemplateColumns: "1fr 0.85fr", gap: "clamp(28px,4vw,60px)", alignItems: "center", padding: "clamp(36px,6vh,72px) clamp(18px,4vw,44px)" }}
          className="hero-grid hero-pad">

          <div>
            <PopIn>
              <div style={{ marginBottom: 20 }}><Tag tone="dark">no sign-in required</Tag></div>
            </PopIn>
            <PopIn delay={0.05}>
              <h1 style={{ fontFamily: DISPLAY, fontSize: "clamp(32px,4.6vw,58px)", fontWeight: 600, letterSpacing: "-0.03em", lineHeight: 1.04, color: CREAM, marginBottom: 20 }}>
                One upload.<br />Every exact <span style={{ color: ACCENT }}>spec.</span>
              </h1>
            </PopIn>
            <PopIn delay={0.1}>
              <p style={{ fontFamily: BODY, fontSize: "clamp(14px,1.2vw,16px)", color: TEXT_MUTED_D, lineHeight: 1.65, maxWidth: 440, marginBottom: 28 }}>
                Upload one master image and get production-ready panels for{" "}
                <span style={{ color: CREAM, fontWeight: 500 }}>47+ real OOH and platform specs</span>{" "}
                in seconds. Free to try.
              </p>
            </PopIn>
            <PopIn delay={0.15}>
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 28 }}>
                <button onClick={() => router.push("/auth?tab=signup&redirect=/pricing")}
                  style={{ background: ACCENT, color: INK, border: "none", borderRadius: 2, padding: "13px 26px", fontFamily: MONO, fontSize: 13, fontWeight: 600, cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 8 }}>
                  get started <ArrowForwardIcon sx={{ fontSize: 15 }} />
                </button>
                <button onClick={() => router.push("/auth?tab=signup&redirect=/pricing")}
                  style={{ background: "transparent", border: `1px solid ${BORDER_D}`, color: CREAM, borderRadius: 2, padding: "13px 26px", fontFamily: MONO, fontSize: 13, cursor: "pointer" }}>
                  view pricing
                </button>
              </div>
            </PopIn>
            <PopIn delay={0.2}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <div style={{ display: "flex", gap: 1 }}>{[1, 2, 3, 4, 5].map(s => <StarIcon key={s} sx={{ fontSize: 12, color: ACCENT }} />)}</div>
                <span style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_D }}><strong style={{ color: CREAM }}>500+</strong> creative teams shipping with Recreative AI</span>
              </div>
            </PopIn>
          </div>

          <div style={{ position: "relative", display: "flex", justifyContent: "center" }}>
            <PopIn delay={0.15} style={{ width: "100%", maxWidth: 400 }}><TerminalDemo /></PopIn>
          </div>
        </motion.div>

        {/* ticker */}
        <div style={{ position: "relative", zIndex: 2, borderTop: `1px solid ${BORDER_D}`, background: "rgba(17,24,39,0.92)", padding: "8px 0", overflow: "hidden" }}>
          <motion.div animate={{ x: ["0%", "-50%"] }} transition={{ duration: 28, repeat: Infinity, ease: "linear" }} style={{ display: "flex", whiteSpace: "nowrap", width: "max-content" }}>
            {[...Array(2)].flatMap(() => ["instagram story", "youtube thumb", "linkedin banner", "ooh billboard", "qms digital screen", "x banner", "app store banner", "email header"]).map((t, i) => (
              <span key={i} style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_D, padding: "0 22px", borderRight: `1px solid ${BORDER_D}` }}>{t}</span>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── SPEC PLATE (stats) ── */}
      <section style={{ background: INK }}><SpecPlate /></section>

      {/* ── PROBLEMS ── */}
      <section className="section-pad" style={{ padding: "80px 44px", background: CREAM }}>
        <div style={{ maxWidth: 1160, margin: "0 auto" }}>
          <FadeIn style={{ marginBottom: 44 }}>
            <div style={{ marginBottom: 12 }}><Tag>the problem</Tag></div>
            <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(24px,4vw,44px)", fontWeight: 600, letterSpacing: "-0.03em", lineHeight: 1.08, color: INK }}>
              One design. Too many formats.
            </h2>
          </FadeIn>
          <div className="three-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 20 }}>
            {PROBLEMS.map((p, i) => (
              <ProblemPanel key={i} {...p} expanded={expandedProblem === i} onToggle={() => setExpandedProblem(expandedProblem === i ? null : i)} />
            ))}
          </div>
        </div>
      </section>

      {/* ── ROUTE BOARD ── */}
      <section className="section-pad" style={{ background: INK, padding: "64px 44px 76px" }}>
        <div style={{ maxWidth: 940, margin: "0 auto" }}>
          <FadeIn style={{ marginBottom: 30 }}>
            <div style={{ marginBottom: 10 }}><span style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_D }}>select a spec to inspect</span></div>
            <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(22px,3.6vw,38px)", fontWeight: 600, letterSpacing: "-0.03em", color: CREAM }}>Proof check</h2>
          </FadeIn>
          <RouteBoard />
        </div>
      </section>

      {/* ── ROUTE DIAGRAM ── */}
      <section className="section-pad" style={{ padding: "80px 44px", maxWidth: 1160, margin: "0 auto", background: CREAM }}>
        <div style={{ display: "grid", gridTemplateColumns: isTablet ? "1fr" : "1fr 1fr", gap: 52, alignItems: "center" }}>
          <FadeIn>
            <div style={{ marginBottom: 16 }}><span style={{ fontFamily: MONO, fontSize: 10.5, color: ACCENT }}>the route</span></div>
            <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(22px,3.4vw,38px)", fontWeight: 600, letterSpacing: "-0.03em", lineHeight: 1.08, marginBottom: 16, color: INK }}>
              One upload.<br /><span style={{ color: ACCENT }}>Every spec, routed.</span>
            </h2>
            <p style={{ fontFamily: BODY, fontSize: 14.5, color: TEXT_MUTED_L, lineHeight: 1.7, marginBottom: 24 }}>
              The engine decomposes your source into components, then recomposes each one to its target's exact profile — never a generic rescale.
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
              {[["Subject-aware decomposition", "Isolates faces, logos, and focal points"], ["Background extension", "Fills new areas seamlessly, never duplicated"], ["Spec-exact recomposition", "Adapts layout to each target's own dimension profile"]].map(([t, d]) => (
                <div key={t} style={{ borderLeft: `1px solid ${ACCENT}`, padding: "8px 14px" }}>
                  <div style={{ fontFamily: BODY, fontSize: 13, fontWeight: 600, color: INK }}>{t}</div>
                  <div style={{ fontFamily: BODY, fontSize: 12, color: TEXT_MUTED_L }}>{d}</div>
                </div>
              ))}
            </div>
          </FadeIn>
          <FadeIn delay={0.1}>
            <div style={{ background: INK, borderRadius: 2, padding: "24px 18px", border: `1px solid ${BORDER_D}` }}>
              <RouteDiagram />
            </div>
          </FadeIn>
        </div>
      </section>

      {/* ── SOLUTIONS ── */}
      <section className="section-pad" style={{ padding: "80px 44px", background: INK }}>
        <div style={{ maxWidth: 1160, margin: "0 auto" }}>
          <FadeIn style={{ marginBottom: 44 }}>
            <div style={{ marginBottom: 10 }}><span style={{ fontFamily: MONO, fontSize: 10.5, color: ACCENT }}>quality control</span></div>
            <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(24px,4vw,44px)", fontWeight: 600, letterSpacing: "-0.03em", color: CREAM }}>Built to clear spec</h2>
          </FadeIn>
          <div className="three-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 18 }}>
            {SOLUTIONS.map((s, i) => <SolutionPanel key={i} {...s} />)}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="section-pad" style={{ padding: "80px 44px", background: CREAM }}>
        <div style={{ maxWidth: 940, margin: "0 auto" }}>
          <FadeIn style={{ marginBottom: 44 }}>
            <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(22px,3.6vw,38px)", fontWeight: 600, letterSpacing: "-0.03em", color: INK }}>Three stages. Under five seconds.</h2>
          </FadeIn>
          <div className="three-grid" style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)" }}>
            {STEPS.map((s, i) => <StepStub key={i} {...s} />)}
          </div>
        </div>
      </section>

      {/* ── TWO ENGINES ── */}
      <section className="section-pad" style={{ padding: "80px 44px", maxWidth: 1080, margin: "0 auto", background: INK }}>
        <FadeIn style={{ marginBottom: 40 }}>
          <div style={{ marginBottom: 10 }}><span style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_D }}>both included in every plan</span></div>
          <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(22px,3.4vw,38px)", fontWeight: 600, letterSpacing: "-0.03em", color: CREAM }}>Two engines</h2>
        </FadeIn>
        <div className="engine-grid" style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
          <EnginePanel tone={ACCENT} tag="transformation" icon={<TransformIcon sx={{ fontSize: 22 }} />} name="Transformation Engine"
            desc={<>Adapt <strong style={{ color: CREAM }}>any existing image</strong> to any format. The engine extends backgrounds, recomposes layouts, and preserves subjects while keeping your original creative intent.</>}
            features={["background extension AI", "subject-aware cropping", "layout recomposition", "47+ format presets"]}
            cta={() => router.push("/auth?tab=signup&redirect=/pricing")} />
          <EnginePanel tone="#4B8F6C" tag="creation" icon={<AddPhotoAlternateIcon sx={{ fontSize: 22 }} />} name="Creation Engine"
            desc={<>Generate <strong style={{ color: CREAM }}>new format variations</strong> from scratch. Platform-optimized assets tuned to each channel's visual requirements and brand guidelines.</>}
            features={["platform-optimized generation", "brand guideline awareness", "batch creation", "custom dimension support"]}
            cta={() => router.push("/auth?tab=signup&redirect=/pricing")} />
        </div>
      </section>

      {/* ── LEDGER ── */}
      <section className="section-pad" style={{ padding: "20px 44px 80px", maxWidth: 840, margin: "0 auto", background: CREAM }}>
        <FadeIn style={{ marginBottom: 24 }}>
          <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(20px,3.2vw,34px)", fontWeight: 600, letterSpacing: "-0.03em", textAlign: "center", color: INK }}>Manual vs Recreative AI</h2>
        </FadeIn>
        <Ledger rows={COMPARE} />
      </section>

      {/* ── CTA ── */}
      <section className="section-pad" style={{ padding: "40px 44px 96px", background: CREAM }}>
        <FadeIn style={{ maxWidth: 760, margin: "0 auto" }}>
          <div style={{ background: INK, borderRadius: 2, padding: "clamp(36px,6vw,60px) clamp(24px,5vw,48px)", textAlign: "center" }}>
            <RocketLaunchIcon sx={{ fontSize: 24, color: ACCENT, marginBottom: 16 }} />
            <h2 style={{ fontFamily: DISPLAY, fontSize: "clamp(22px,3.6vw,36px)", fontWeight: 600, letterSpacing: "-0.03em", color: CREAM, lineHeight: 1.1, marginBottom: 14 }}>
              Start with 2 free generations
            </h2>
            <p style={{ fontFamily: BODY, fontSize: "clamp(13px,1.3vw,15px)", color: TEXT_MUTED_D, maxWidth: 380, margin: "0 auto 30px", lineHeight: 1.6 }}>
              No account needed. Upload your image and watch every format clear spec in seconds.
            </p>
            <button onClick={() => router.push("/auth?tab=signup&redirect=/pricing")}
              style={{ background: ACCENT, color: INK, fontFamily: MONO, fontSize: "clamp(12.5px,1.2vw,14px)", padding: "14px 36px", borderRadius: 2, fontWeight: 600, border: "none", cursor: "pointer", display: "inline-flex", alignItems: "center", gap: 8 }}>
              try free now <ArrowForwardIcon sx={{ fontSize: 15 }} />
            </button>
            <div style={{ marginTop: 16, fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_D }}>then from $29/month · cancel anytime</div>
          </div>
        </FadeIn>
      </section>

      {/* ── FOOTER ── */}
      <footer className="section-pad" style={{ borderTop: `1px solid ${BORDER_L}`, padding: "22px 44px", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 14, background: CREAM }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <GridMark size={20} />
          <span style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_L }}>recreative ai · image adaptation · 2026</span>
        </div>
        <div style={{ display: "flex", gap: 18, flexWrap: "wrap" }}>
          {["privacy policy", "terms of service", "contact sales"].map(l => (
            <span key={l} style={{ fontFamily: MONO, fontSize: 10.5, color: TEXT_MUTED_L, cursor: "pointer" }}
              onMouseEnter={e => { (e.target as HTMLSpanElement).style.color = ACCENT; }}
              onMouseLeave={e => { (e.target as HTMLSpanElement).style.color = TEXT_MUTED_L; }}>{l}</span>
          ))}
        </div>
      </footer>
    </div>
  );
}
