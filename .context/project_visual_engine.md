---
name: Visual Engine Backend — Full Project Context
description: Complete architecture, file layout, pipeline, dimension registry, and implementation history for the Visual Engine FastAPI backend
type: project
originSessionId: cea3306e-714a-4ee0-b3b9-ea3c39c2cba1
---
## What this project is

Visual Engine is a FastAPI backend (`Visual-Engine-BE-secure/main.py`) that resizes/recomposes advertising images into multiple output formats using Google Gemini AI.

Two primary use-cases:
1. Standard smart resize — Gemini-powered crop/extend for common aspect ratios (16:9, 9:16, 1:1, etc.)
2. OOH / QMS recomposition — Full component-decomposition pipeline for Out-of-Home billboard and QMS digital screen dimensions

**Stack:** FastAPI · Python 3.12 · Google Gemini AI (AI Studio REST + Vertex) · MongoDB · Stripe · Digital Ocean Spaces (S3) · Pillow · NumPy

---

## Core files

| File | Role |
|------|------|
| `main.py` | FastAPI app, all endpoints, OOH routing, `OOH_MEDIA_SITE_DIMENSIONS` dict (~5000 lines) |
| `auth.py` | JWT auth, credit/plan management |
| `org_auth.py` | Organisation-level JWT |
| `stripe_manager.py` | Stripe checkout, portal, webhooks |
| `ooh_pipeline.py` | OOH pipeline orchestrator (decompose, cache, recompose, ultra-wide routing) |
| `ooh_dimensions.py` | DimProfile TypedDicts for OOH dimensions (14 profiles) |
| `qms_dimensions.py` | DimProfile TypedDicts for QMS dimensions (40 profiles, 3100+ lines) |
| `banner_2072x252.py` | Ultra-wide standalone recomposer for **2072×252 only** |
| `banner_2640x288.py` | Ultra-wide standalone recomposer for **2640×288 only** — horizontal input sheet + pre-distortion compensation prompt (added 2026-05-10) |
| `gemini_decomposition/banner_recomposer.py` | Primary Gemini-vision recomposer; reads profiles via `get_profile()`; caps input images at 3072 px |
| `gemini_decomposition/gemini_isolate.py` | Component isolation API calls |
| `gemini_decomposition/api_client.py` | Gemini AI Studio REST client with retry + key rotation |
| `test_qms_batch2.py` | Runs all 16 batch-2 QMS test dimensions in one go |
| `test_qms_landscape_wide.py` | 7 landscape-wide batch-2 dimensions |
| `test_qms_landscape_moderate.py` | 5 landscape-moderate batch-2 dimensions |
| `test_qms_portrait_moderate.py` | 4 portrait-moderate batch-2 dimensions |

---

## OOH/QMS Pipeline Architecture

```
1. analyze_components()     Gemini vision → JSON component list with bounding boxes
2. isolate_component_png()  Per-component Gemini edit → isolated PNG
3. recompose_with_gemini_vision()  Component sheet + hi-res PNGs → Gemini composes banner
   └── fallback: recompose_banner()  Manual PIL compositor
4. PIL resize               Guarantee exact pixel dimensions
```

**Caching:** SHA256 of image bytes → `ooh_decomposition_cache/<hash>/`. TTL 48h. Also synced to DO Spaces S3.
Photo layers are always patched post-cache with direct PIL crops (`_patch_photo_layers()`) to prevent face drift.

**Gemini input cap:** `_cap_image_bytes()` in `banner_recomposer.py` resizes any input image exceeding 3072 px on its longest side before the API call. Prevents "dimension must be between X and Y" errors for large-format sources.

---

## OOH_MEDIA_SITE_DIMENSIONS (main.py ~line 1710)

All dimensions are registered and routable via the API:

```
── OOH (15 dims) ────────────────────────────────────────────────────────────
OOH_1060X360 · OOH_1232X672 · OOH_1344X432 · OOH_1836X432 · OOH_1952X896
OOH_2072X252 (→ banner_2072x252.py) · OOH_3924X972
OOH_504X1008 · OOH_768X1152
OOH_792X216 · OOH_800X400 · OOH_840X360 · OOH_1280X384 · OOH_1024X320 · OOH_960X576

── QMS Batch 1 (7 dims) ──────────────────────────────────────────────────────
QMS_2640X288 (→ banner_2072x252.py, ultra-wide) · QMS_1824X432 · QMS_1728X432
QMS_1440X360 · QMS_1120X320 · QMS_760X240 · QMS_1184X384

── QMS Batch 2 (33 dims) ────────────────────────────────────────────────────
Landscape wide:     QMS_4530X990 · QMS_1728X576 · QMS_1280X448 · QMS_1152X288
                    QMS_816X288 · QMS_768X288 · QMS_736X256
Landscape moderate: QMS_3840X2160 · QMS_1920X1080 · QMS_1680X810 · QMS_864X480
                    QMS_608X304 · QMS_600X320 · QMS_600X280 · QMS_960X540
Portrait tall:      QMS_224X832 · QMS_240X960 · QMS_288X1024
Portrait moderate:  QMS_648X1296 · QMS_480X960 · QMS_432X768 · QMS_360X720
                    QMS_352X704 · QMS_480X640 · QMS_540X720 · (+ others)
```

---

## Ultra-Wide Routing (AR ≥ 8:1)

Dimensions with extreme aspect ratios skip `banner_recomposer.py` and use `banner_2072x252.py` instead. That file uses a simpler ultra-wide prompt and direct LANCZOS resize (no AR-aware grey-bar padding).

**Currently routed to dedicated recomposers:**
- `2072×252` (8.2:1) → `banner_2072x252.py`
- `2640×288` (9.2:1) → `banner_2640x288.py` — horizontal input sheet + pre-distortion compensation

**Routing implemented in TWO places** (must update both when adding new ultra-wide dims):
1. `ooh_pipeline.py` → `_ULTRA_WIDE_ROUTE = {(2640, 288)}` (test scripts call `ooh_resize()` directly)
2. `main.py` → `_ULTRA_WIDE_BANNER_DIMS = {(2072, 252), (2640, 288)}` and `_CUSTOM_ULTRA_WIDE_DIMS` (API endpoint)

---

## DimProfile system

`ooh_dimensions.py` and `qms_dimensions.py` define `DimProfile` TypedDicts — one per canvas size.
Injected into Gemini prompts by `banner_recomposer.py` via `get_profile(target_w, target_h)`.

`get_profile()` resolution order:
1. `QMS_PROFILES` in `qms_dimensions.py` — exact match
2. `OOH_PROFILES` in `ooh_dimensions.py` — exact match
3. Generic fallback by AR category (in `ooh_dimensions.py`)

### OOH profiles (ooh_dimensions.py — 14 profiles)
792×216, 1344×432, 1836×432, 1060×360, 1280×384, 1024×320, 3924×972,
840×360, 1232×672, 1952×896, 960×576, 800×400, 504×1008, 768×1152

### QMS profiles (qms_dimensions.py — 40 profiles)
Batch 1: 2640×288, 1824×432, 1728×432, 1440×360, 1120×320, 760×240, 1184×384
Batch 2: 33 additional dimensions across all four orientation categories

---

## Face Fidelity — Prompt Engineering

Gemini regenerates human faces when:
- Person is against a **plain/white background** (mistaken for stock photo)
- Target AR is **similar to the source** (Gemini rescales instead of compositing)
- **Portrait-to-portrait** format match (Gemini regenerates instead of assembling)

**Working prompt patterns** in `qms_dimensions.py`:

| Pattern | Effect |
|---------|--------|
| Logo analogy: "Treat person EXACTLY like a LOGO — drop in, do NOT regenerate" | Triggers Gemini's trained logo-preservation behaviour |
| "⚠ RATIO TRAP WARNING: similar format ≠ regenerate — place crops INDIVIDUALLY" | Prevents rescaling the source |
| "⚠ PORTRAIT-TO-PORTRAIT TRAP: DO NOT regenerate — assemble crops" | Prevents portrait-to-portrait regeneration |
| "Paste AGAINST THE SAME plain/white background it already has" | Prevents inventing new scenes/furniture |
| Specific face fields: "skin tone, facial features, structure, expression, beard/hair, eye shape" | More precise than vague "face must match" |
| Step-by-step COMPOSITOR WORKFLOW with pixel positions | Replaces vague "position person at anchor" |

Applied to: **1440×360, 1184×384** (original fixes) + **864×480, 600×280, 360×720** (2026-05-09 fixes) + all batch-2 dimensions.

---

## Key invariants / design rules

- Each component appears EXACTLY ONCE — never duplicate humans/products/logos
- Photo/image layers: always patched with PIL crop after cache load (`_patch_photo_layers()`)
- Text layers: passed as hi-res image crops to Gemini (prevents font substitution)
- Embedded components (logo on bottle label etc.) are merged away before recomposition
- Ultra-wide dims (AR ≥ 8:1) route to `banner_2072x252.py` — currently `{(2072,252), (2640,288)}`
- QMS pipeline is identical to OOH — same 4-step flow, same `ooh_pipeline.py`
- Gemini inputs capped at 3072 px longest side before API calls

---

## Auth / Billing

- JWT, Stripe subscriptions, credit-based consumption
- OOH access gated per-user via `allowed_ooh_dimensions` field
- `AppOwner` / `SuperOrg` org types bypass dimension restrictions and see all codes

**Why:** How this should shape suggestions — prefer changes that respect credit gating and org access rules when touching OOH/QMS routing.
