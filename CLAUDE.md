# Visual Engine Backend — Claude Context

> Keep this file updated every time a significant feature is added, changed, or removed.
> This is the primary reference for Claude Code in every new session.

---

## Project Overview

**Visual Engine** is a FastAPI backend (`main.py`) that takes advertising/creative images and intelligently resizes/recomposes them into multiple output formats using Google Gemini AI.

The two primary use-cases are:
1. **Standard resize** — Gemini-powered smart crop/extend for common aspect ratios (16:9, 9:16, 1:1, etc.)
2. **OOH / QMS media recomposition** — Full component-decomposition pipeline for Out-of-Home billboard and QMS digital screen dimensions

**Stack:** FastAPI · Python 3.12 · Google Gemini AI (via AI Studio REST) · MongoDB · Stripe · Digital Ocean Spaces (S3-compatible) · Pillow · NumPy

---

## Repository Layout

```
Visual-Engine-BE-secure/
├── main.py                          # FastAPI app — all endpoints, routing logic
├── auth.py                          # JWT auth, user/plan/credit management
├── org_auth.py                      # Organisation-level JWT validation
├── stripe_manager.py                # Stripe checkout, portal, webhook handling
├── middleware.py                    # Custom middleware
├── models.py                        # Pydantic request/response models
├── validators.py                    # Input validators
├── plan_schema.py                   # Plan tier definitions
├── openai_service.py                # OpenAI fallback service
│
├── ooh_pipeline.py                  # OOH pipeline orchestrator (decompose → recompose)
├── ooh_dimensions.py                # DimProfile definitions for OOH dimensions
├── qms_dimensions.py                # DimProfile definitions for QMS dimensions (40 profiles)
├── banner_2072x252.py               # Ultra-wide recomposer — 2072×252 only
├── banner_2640x288.py               # Ultra-wide recomposer — 2640×288 only (dedicated file)
│
├── gemini_decomposition/
│   ├── banner_recomposer.py         # Primary Gemini-vision recomposer (all dims)
│   ├── gemini_isolate.py            # Gemini component isolation calls
│   ├── api_client.py                # Google AI Studio REST client
│   ├── pipeline.py                  # Original decomposition pipeline
│   ├── gemini_assembler.py          # PIL-based assembler (legacy)
│   ├── cv2_position_refiner.py      # CV2 position refinement
│   ├── schema.py                    # Component schema
│   ├── config.py                    # Config constants
│   ├── server.py                    # Standalone decomposition server
│   └── wrapper.py                   # Wrapper utilities
│
├── test_qms_landscape_wide.py       # Test: 7 landscape-wide QMS batch-2 dimensions
├── test_qms_landscape_moderate.py   # Test: 5 landscape-moderate QMS batch-2 dimensions
├── test_qms_portrait_moderate.py    # Test: 4 portrait-moderate QMS batch-2 dimensions
├── test_qms_batch2.py               # Test: all 16 batch-2 dimensions combined
│
└── ooh_decomposition_cache/         # SHA256-keyed decomposition cache (gitignored)
```

---

## OOH / QMS Recomposition Pipeline

This is the most complex and performance-critical part of the system.

### Architecture (4 steps)

```
1. analyze_components()     Gemini vision → JSON list of visual layers + bounding boxes
2. isolate_component_png()  Per-component Gemini edit → isolated PNG on white background
                              • solid_color background → PIL fill  (0 API calls)
                              • text                  → bbox crop  (0 API calls)
                              • photo/image           → Gemini isolation
                              • logo/icon/shape       → Gemini isolation
3. recompose_with_gemini_vision()
                            Component sheet + hi-res PNGs → Gemini composes target banner
                            Falls back to PIL manual compositor if Gemini fails
4. PIL resize               Guarantee exact output pixel dimensions
```

### Caching

- Cache key: SHA256 of raw image bytes
- Cache dir: `ooh_decomposition_cache/<sha256>/`
- Contents: `00_original.png`, `components.json`, `layer_NN_<type>_<desc>.png`
- Cache is also synced to/from Digital Ocean Spaces (S3) for multi-instance sharing
- TTL: 1 hour (based on last-accessed sentinel file; `_CACHE_MAX_AGE_HOURS` in `ooh_pipeline.py`)
- Photo/image layers are **always patched** with direct PIL crops after cache load to guarantee pixel-perfect face fidelity — even if S3 stored a stale Gemini-generated layer

### Gemini Input Image Size Cap (banner_recomposer.py)

`_GEMINI_MAX_INPUT_DIM = 3072` — any image sent to Gemini (extra_image_parts OR original source) is automatically downscaled to fit within 3072 px on its longest side before the API call. This prevents "dimension must be between X and Y" API errors for very large source images (4K+, 4530×990-class sources).

### Ultra-Wide Routing (AR ≥ 9:1)

Dimensions with extreme aspect ratios are routed to dedicated recomposers instead of the standard `banner_recomposer.py`. Currently:
- `2072×252` (8.2:1) → `banner_2072x252.py`
- `2640×288` (9.2:1) → `banner_2640x288.py` (dedicated file added 2026-05-10)

Routing happens in TWO places:
1. `ooh_pipeline.py` — `_ULTRA_WIDE_ROUTE = {(2640, 288)}` intercepts test-script calls to `ooh_resize()`
2. `main.py` — `_ULTRA_WIDE_BANNER_DIMS = {(2072, 252), (2640, 288)}` intercepts API-level calls

### Routing in main.py

```python
OOH_MEDIA_SITE_DIMENSIONS: Dict[str, Tuple[int, int]] = {
    # ── OOH dimensions ────────────────────────────────────────────────────────
    "OOH_1060X360":  (1060, 360),
    "OOH_1232X672":  (1232, 672),
    "OOH_1344X432":  (1344, 432),
    "OOH_1836X432":  (1836, 432),
    "OOH_1952X896":  (1952, 896),
    "OOH_2072X252":  (2072, 252),   # → banner_2072x252.py (ultra-wide special case)
    "OOH_3924X972":  (3924, 972),
    "OOH_504X1008":  (504,  1008),
    "OOH_768X1152":  (768,  1152),
    "OOH_792X216":   (792,   216),
    "OOH_800X400":   (800,   400),
    "OOH_840X360":   (840,   360),
    "OOH_1280X384":  (1280,  384),
    "OOH_1024X320":  (1024,  320),
    "OOH_960X576":   (960,   576),
    # ── QMS dimensions — Batch 1 (original 7) ────────────────────────────────
    "QMS_2640X288":  (2640,  288),   # → banner_2640x288.py (ultra-wide dedicated recomposer)
    "QMS_1824X432":  (1824,  432),
    "QMS_1728X432":  (1728,  432),
    "QMS_1440X360":  (1440,  360),
    "QMS_1120X320":  (1120,  320),
    "QMS_760X240":   (760,   240),
    "QMS_1184X384":  (1184,  384),
    # ── QMS dimensions — Batch 2 (33 new dimensions) ─────────────────────────
    # (see qms_dimensions.py for full list)
}
```

Any dimension in `OOH_MEDIA_SITE_DIMENSIONS` routes to `ooh_pipeline.ooh_resize()`.
Ultra-wide exceptions: `2072×252` → `banner_2072x252.py`, `2640×288` → `banner_2640x288.py`.

---

## Dimension Profile System

### How it works

`ooh_dimensions.py` and `qms_dimensions.py` define `DimProfile` TypedDicts — one per supported canvas size. These profiles are injected into Gemini prompts by `banner_recomposer.py` via `get_profile(target_w, target_h)`.

### `DimProfile` keys

| Key | Purpose |
|-----|---------|
| `label` | Human-readable name for logging |
| `canvas_description` | Canvas shape description injected into Gemini prompt |
| `ratio_str` | e.g. `"3:1"`, `"4.2:1"` |
| `orientation` | `landscape_extreme` / `landscape_wide` / `landscape_moderate` / `portrait_tall` / `portrait_moderate` |
| `layout_direction` | `"horizontal_flow"` / `"vertical_flow"` |
| `arrangement_order` | Ordered list of component types for placement priority |
| `element_max_height` | Fraction of canvas height for scaling guidance |
| `element_guidance` | Plain-English scaling/fill note injected into Gemini prompt Rule 4 |
| `fill_direction` | `"horizontally"` / `"vertically"` |
| `fill_description` | How to fill empty space (injected into Rule 2 / NO DUPLICATION) |
| `layout_rules` | List of layout rules for fallback layout planner prompt |
| `dimension_warnings` | WARNINGS injected into recompose prompt |

### `get_profile()` resolution order (banner_recomposer.py)

```
QMS_PROFILES (qms_dimensions.py)  →  exact match first
OOH_PROFILES (ooh_dimensions.py)  →  exact match second
ooh_dimensions fallback functions →  generic profile by AR category
```

### OOH Profiles (ooh_dimensions.py)

| Dimension | Label | Ratio | Orientation |
|-----------|-------|-------|-------------|
| 792 × 216 | Thin wide strip | 3.7:1 | landscape_extreme |
| 1344 × 432 | Wide billboard | 3:1 | landscape_wide |
| 1836 × 432 | Super wide billboard | 4.25:1 | landscape_wide |
| 1060 × 360 | Wide billboard | 3:1 | landscape_wide |
| 1280 × 384 | Wide strip billboard | 3.3:1 | landscape_wide |
| 1024 × 320 | Wide strip | 3.2:1 | landscape_wide |
| 3924 × 972 | Large wide billboard | 4:1 | landscape_wide |
| 840 × 360 | Moderate wide banner | 2.3:1 | landscape_moderate |
| 1232 × 672 | Moderate landscape banner | 1.8:1 | landscape_moderate |
| 1952 × 896 | Wide landscape banner | 2.2:1 | landscape_moderate |
| 960 × 576 | Near 16:9 banner | 1.67:1 | landscape_moderate |
| 800 × 400 | Standard 2:1 banner | 2:1 | landscape_moderate |
| 504 × 1008 | Tall portrait banner | 1:2 | portrait_tall |
| 768 × 1152 | Portrait banner | 2:3 | portrait_moderate |

### QMS Profiles (qms_dimensions.py)

**Batch 1 — original 7 (added 2026-05-07):**

| Dimension | Label | Ratio | Orientation |
|-----------|-------|-------|-------------|
| 2640 × 288 | Ultra-extreme thin strip | 9.2:1 | landscape_extreme |
| 1824 × 432 | Super wide billboard | 4.2:1 | landscape_wide |
| 1728 × 432 | Wide billboard | 4:1 | landscape_wide |
| 1440 × 360 | Wide billboard | 4:1 | landscape_wide |
| 1120 × 320 | Wide strip billboard | 3.5:1 | landscape_wide |
| 760 × 240 | Wide strip | 3.2:1 | landscape_wide |
| 1184 × 384 | Wide billboard | 3.1:1 | landscape_wide |

**Batch 2 — 33 new dimensions (added 2026-05-08/09):**

| Category | Dimensions |
|----------|-----------|
| Landscape wide | 4530×990, 1728×576, 1280×448, 1152×288, 816×288, 768×288, 736×256 |
| Landscape moderate | 3840×2160, 1920×1080, 1680×810, 864×480, 608×304, 600×320, 600×280, 960×540 |
| Portrait tall | 224×832, 240×960, 288×1024 |
| Portrait moderate | 648×1296, 480×960, 432×768, 360×720, 352×704, 480×640, 540×720, and others |

All batch 2 profiles use "MECHANICAL COMPOSITOR" + "SEALED STICKER" prompt framing.

---

## banner_recomposer.py vs banner_2072x252.py vs banner_2640x288.py

| File | Target dimensions | Notes |
|------|------------------|-------|
| `gemini_decomposition/banner_recomposer.py` | All OOH + QMS dims via `ooh_pipeline.py` | Uses `get_profile()` — checks QMS then OOH; has AR-aware post-processing |
| `banner_2072x252.py` | `2072×252` only | Purpose-built for 8.2:1 ultra-wide; simple prompt; direct LANCZOS resize |
| `banner_2640x288.py` | `2640×288` only | Dedicated 9.2:1 recomposer; horizontal input sheet + pre-distortion compensation prompt |

**`banner_2640x288.py` key design decisions (added 2026-05-10):**
- Builds a **horizontal component sheet** (9.2:1 aspect ratio) as Gemini input — the editing API preserves input orientation, so landscape-in → landscape-out
- Prompt uses **pre-distortion compensation**: tells Gemini to render elements 3–4x taller/narrower than normal, since the output will be horizontally stretched during final LANCZOS resize
- Components are placed as **percentage zones** (0–20%, 20–45%, 45–65%, 65–85%, 85–100%) not pixel coordinates, since Gemini's actual output dimensions vary per run

`banner_recomposer.py` has two compositors:
- **Primary**: `recompose_with_gemini_vision()` — sends component sheet + hi-res PNGs to Gemini
- **Fallback**: `recompose_banner()` — manual PIL compositor with AI-planned layout

---

## Key Design Decisions & Rules

1. **Never duplicate components** — photos, logos, people must appear exactly once. Background is extended to fill space.
2. **Photo layers are patched after cache load** — `_patch_photo_layers()` in `ooh_pipeline.py` always overwrites cached photo/image layers with direct PIL crops from the source. This prevents face drift from stale S3 caches.
3. **Text layers are passed as hi-res image crops** — Gemini receives isolated text PNGs so it pastes exact crops rather than retyping with a different font.
4. **Embedded components are merged** — logos/text physically printed ON a product (e.g. label) are removed from the component list before recomposition (`_merge_embedded_components()`).
5. **Ultra-wide dims have dedicated recomposers** — `2072×252` → `banner_2072x252.py`; `2640×288` → `banner_2640x288.py`. Both `ooh_pipeline.py` and `main.py` implement this routing.
6. **QMS dims share the same pipeline** — `qms_dimensions.py` follows identical TypedDict structure and `get_profile()` signature as `ooh_dimensions.py`. `banner_recomposer.py` checks QMS first, then OOH.
7. **Gemini input images are capped at 3072 px** — `_cap_image_bytes()` in `banner_recomposer.py` prevents "dimension must be between" API errors for high-res sources.

---

## Face Fidelity — Prompt Engineering Patterns

Gemini tends to regenerate human faces rather than faithfully copying the provided crop, especially when:
- The source person is against a **plain/white background** (easily confused with stock photos)
- The target AR is **similar to the source AR** (Gemini "rescales" instead of compositing)
- The target is **portrait-to-portrait** (Gemini regenerates the ad instead of assembling crops)

**Working prompt patterns** (implemented in affected QMS profiles):

| Pattern | Language |
|---------|---------|
| Logo analogy | "Treat the person photo EXACTLY like a LOGO — drop it in, do NOT regenerate it." |
| Ratio trap warning | "⚠ RATIO TRAP WARNING: The X:Y format may look similar to the source. DO NOT simply rescale or regenerate the source image. Place each crop INDIVIDUALLY." |
| Portrait trap | "⚠ PORTRAIT-TO-PORTRAIT TRAP: Source and target are both portrait. DO NOT regenerate — assemble component crops individually." |
| Same background | "Paste the crop AGAINST THE SAME plain/white background it already has — do NOT place them in a new scene." |
| Specific face fields | "MUST match on: skin tone, facial features, facial structure, expression, beard/hair, and eye shape." |
| Step-by-step workflow | Explicit STEP 1/2/3/4 with pixel positions rather than vague "position the person". |

Dimensions currently using these patterns: **1440×360, 1184×384, 864×480, 600×280, 360×720**, and all batch-2 dimensions.

---

## Authentication & Billing

- JWT-based auth (`auth.py`)
- Organisation-level auth via `org_auth.py`
- Plans: Starter, Pro, Enterprise — credit-based consumption
- Stripe integration for checkout and subscription management
- OOH access is gated per-user via `allowed_ooh_dimensions` field
- `AppOwner` and `SuperOrg` org types bypass dimension restrictions and get all OOH/QMS codes

---

## Environment Variables

```env
GOOGLE_AI_STUDIO_KEY        # Primary — used by banner_recomposer.py & api_client.py
GLENN_GOOGLE_API_KEY        # Injected as GOOGLE_AI_STUDIO_KEY by ooh_pipeline.py
GLENN_GOOGLE_API_KEY_2      # Fallback key 2
GLENN_GOOGLE_API_KEY_3      # Fallback key 3
OPENROUTER_KEY              # OpenRouter fallback for image generation
DO_SPACES_BUCKET_NAME       # Digital Ocean Spaces bucket
ACCESS_KEY_ID               # DO Spaces access key
SECRET_KEY                  # DO Spaces secret key
ENDPOINT                    # DO Spaces endpoint URL
MONGO_URI                   # MongoDB connection string
STRIPE_SECRET_KEY           # Stripe secret key
STRIPE_WEBHOOK_SECRET       # Stripe webhook signing secret
```

---

## Adding a New Dimension — Checklist

1. **Add a `DimProfile` entry** to `ooh_dimensions.py` (OOH) or `qms_dimensions.py` (QMS)
2. **Register the dimension** in `OOH_MEDIA_SITE_DIMENSIONS` in `main.py` with a `"PREFIX_WxH"` code key
3. **Test** with the matching test script (`test_qms_batch2.py`, `test_qms_landscape_wide.py`, etc.)
4. **If AR ≥ 8:1 (ultra-wide)**: add to `_ULTRA_WIDE_ROUTE` in `ooh_pipeline.py` and `_ULTRA_WIDE_BANNER_DIMS` / `_CUSTOM_ULTRA_WIDE_DIMS` in `main.py`
5. If the dimension is a new special routing case, also update `ooh_pipeline.py`

---

## Files NOT to Edit Casually

- `main.py` — very large (~5000+ lines); edits need careful grep/offset reads
- `gemini_decomposition/api_client.py` — Gemini REST client, handles retries and key rotation
- `gemini_decomposition/gemini_isolate.py` — component isolation prompts; tuned carefully
- `auth.py` — user/plan/credit logic; billing-critical
- `qms_dimensions.py` — 3100+ lines, 40 profiles; use offset reads; always verify with `python -c "from qms_dimensions import QMS_PROFILES"`
