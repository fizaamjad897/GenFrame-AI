"use client";
import { useRouter } from "next/navigation";

const OPTIONS = [
  {
    number: 1,
    name: "Cinematic Dark",
    vibe: "Dark • Dramatic • Cinematic",
    description: "Full dark-theme with animated purple orbs, staggered word-by-word hero reveal, glowing problem/solution cards, and a draggable before/after slider.",
    features: ["Dark animated gradient background", "Draggable before/after showcase", "Glowing purple solution cards"],
    accent: "#0369A1",
    bg: "#07071100",
    cardBg: "#0d0d1a",
    border: "rgba(3, 105, 161,0.4)",
  },
  {
    number: 2,
    name: "Interactive Playground",
    vibe: "Light • Try-first • Conversion",
    description: "Upload zone IS the hero. Users try the product immediately (no sign-up). A sticky generation counter tracks their 2 free uses, then surfaces pricing.",
    features: ["Upload zone as primary hero", "Sticky 2-generation counter", "Format output gallery after upload"],
    accent: "#0369A1",
    bg: "#f9fafb00",
    cardBg: "#ffffff",
    border: "rgba(3, 105, 161,0.2)",
  },
  {
    number: 3,
    name: "Storytelling Scroll",
    vibe: "Narrative • Emotional • Dark",
    description: "Opens on black. Four scroll-triggered text scenes build emotional tension before the brand reveal. Then chaos → order visual transition pulls users through.",
    features: ["4-scene scroll-triggered intro", "Chaos-to-order visual transition", "Sticky product walkthrough panels"],
    accent: "#a78bfa",
    bg: "#05050d00",
    cardBg: "#0a0a18",
    border: "rgba(167,139,250,0.3)",
  },
  {
    number: 4,
    name: "Premium Minimal",
    vibe: "Clean • Apple-esque • Confident",
    description: "Pure white, extreme whitespace, floating product mockup. An infinite CSS marquee, staggered feature grid, and animated comparison table — no noise.",
    features: ["Infinite marquee of platform names", "Animated comparison table", "6-item staggered feature grid"],
    accent: "#0369A1",
    bg: "#ffffff00",
    cardBg: "#fafafa",
    border: "rgba(3, 105, 161,0.15)",
  },
  {
    number: 5,
    name: "Conversion Machine",
    vibe: "Aggressive • B2C • High-energy",
    description: "Deep purple gradient hero with a pulsing 'FREE' badge, rotating value props, social proof numbers, and the hardest-hitting pricing section.",
    features: ["Pulsing free-tier badge", "Rotating animated value props", "Social proof number strip"],
    accent: "#c4b5fd",
    bg: "#06040f00",
    cardBg: "#110d2a",
    border: "rgba(196,181,253,0.3)",
  },
];

export default function PreviewIndex() {
  const router = useRouter();

  return (
    <div style={{ minHeight: "100vh", background: "linear-gradient(135deg, #080812 0%, #120e24 50%, #080812 100%)", fontFamily: "'Inter', system-ui, sans-serif", padding: "60px 24px" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 64 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(3, 105, 161,0.12)", border: "1px solid rgba(3, 105, 161,0.3)", borderRadius: 100, padding: "6px 16px", marginBottom: 24 }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#0369A1", display: "inline-block" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: "#a78bfa", letterSpacing: "0.08em" }}>5 LANDING PAGE OPTIONS</span>
          </div>
          <h1 style={{ fontSize: 48, fontWeight: 700, color: "#ffffff", letterSpacing: "-0.03em", lineHeight: 1.1, margin: "0 0 16px" }}>
            Choose Your Landing Page
          </h1>
          <p style={{ fontSize: 16, color: "rgba(255,255,255,0.5)", maxWidth: 520, margin: "0 auto" }}>
            Five distinct designs for the Visual Engine B2C launch. Click any card to preview.
          </p>
        </div>

        {/* Cards Grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 24 }}>
          {OPTIONS.map((opt) => (
            <div
              key={opt.number}
              onClick={() => router.push(`/preview/option-${opt.number}`)}
              style={{
                background: "rgba(255,255,255,0.03)",
                border: `1px solid ${opt.border}`,
                borderRadius: 20,
                padding: 28,
                cursor: "pointer",
                transition: "all 0.25s cubic-bezier(0.22,1,0.36,1)",
                position: "relative",
                overflow: "hidden",
              }}
              onMouseEnter={e => {
                (e.currentTarget as HTMLDivElement).style.transform = "translateY(-6px)";
                (e.currentTarget as HTMLDivElement).style.background = "rgba(3, 105, 161,0.08)";
                (e.currentTarget as HTMLDivElement).style.borderColor = opt.accent;
                (e.currentTarget as HTMLDivElement).style.boxShadow = `0 20px 40px -10px rgba(3, 105, 161,0.3)`;
              }}
              onMouseLeave={e => {
                (e.currentTarget as HTMLDivElement).style.transform = "translateY(0)";
                (e.currentTarget as HTMLDivElement).style.background = "rgba(255,255,255,0.03)";
                (e.currentTarget as HTMLDivElement).style.borderColor = opt.border;
                (e.currentTarget as HTMLDivElement).style.boxShadow = "none";
              }}
            >
              {/* Number badge */}
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
                <div style={{ width: 44, height: 44, borderRadius: 12, background: `linear-gradient(135deg, ${opt.accent}33, ${opt.accent}11)`, border: `1px solid ${opt.accent}44`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <span style={{ fontSize: 18, fontWeight: 700, color: opt.accent }}>0{opt.number}</span>
                </div>
                <div style={{ background: "rgba(255,255,255,0.05)", borderRadius: 100, padding: "4px 10px", fontSize: 11, color: "rgba(255,255,255,0.4)", fontWeight: 500 }}>
                  {opt.vibe.split(" • ")[0]}
                </div>
              </div>

              <h2 style={{ fontSize: 22, fontWeight: 700, color: "#ffffff", marginBottom: 8, letterSpacing: "-0.02em" }}>
                {opt.name}
              </h2>
              <p style={{ fontSize: 12, color: "rgba(255,255,255,0.35)", marginBottom: 20, fontWeight: 500, letterSpacing: "0.06em", textTransform: "uppercase" }}>
                {opt.vibe}
              </p>
              <p style={{ fontSize: 14, color: "rgba(255,255,255,0.6)", lineHeight: 1.65, marginBottom: 24 }}>
                {opt.description}
              </p>

              {/* Features */}
              <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 28 }}>
                {opt.features.map((f, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <div style={{ width: 4, height: 4, borderRadius: "50%", background: opt.accent, flexShrink: 0 }} />
                    <span style={{ fontSize: 13, color: "rgba(255,255,255,0.5)" }}>{f}</span>
                  </div>
                ))}
              </div>

              {/* CTA */}
              <button style={{
                width: "100%", padding: "12px", borderRadius: 10,
                background: `linear-gradient(135deg, ${opt.accent}22, ${opt.accent}0a)`,
                border: `1px solid ${opt.accent}44`,
                color: opt.accent, fontSize: 14, fontWeight: 600, cursor: "pointer",
                transition: "all 0.2s",
              }}>
                Preview Option {opt.number} →
              </button>
            </div>
          ))}
        </div>

        <p style={{ textAlign: "center", marginTop: 48, fontSize: 13, color: "rgba(255,255,255,0.25)" }}>
          Visual Engine · B2C Landing Page Previews · 2026
        </p>
      </div>
    </div>
  );
}
