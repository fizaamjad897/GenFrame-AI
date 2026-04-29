"""
Visual Engine — OpenAI Image Edit Service

For extreme-wide targets (AR > 3.5, e.g. 2072×252, 3924×972):
  - PRE-COMPOSE: source is scaled and placed in the exact horizontal band
    that _resize_to_target will keep after scale-fill + center-crop.
  - PROMPT: tells OpenAI its only job is to extend the background
    into the blurred zones — the brand content is already placed correctly.

For moderate-wide / normal targets (AR ≤ 3.5):
  - Send raw source + size-directive-amended prompt (existing behaviour).

Post-processing: always scale-to-fill then center-crop — never stretches.
"""
import asyncio
import base64
import io
import os

import httpx
from PIL import Image, ImageFilter


OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
OPENAI_EDIT_URL  = "https://api.openai.com/v1/images/edits"
OPENAI_MODEL     = "gpt-image-2"

OPENAI_SUPPORTED_SIZES = [
    (1792, 1024),
    (1536, 1024),
    (1024, 1024),
    (1024, 1536),
    (1024, 1792),
]

# AR above which we switch to the pre-compose + band-fill strategy
EXTREME_WIDE_AR_THRESHOLD = 3.5

# Kept so existing imports in generation.py don't break
BANNER_AR_THRESHOLD = EXTREME_WIDE_AR_THRESHOLD


# ── helpers ──────────────────────────────────────────────────────────────────

def _closest_openai_size(target_width: int, target_height: int) -> tuple[int, int]:
    target_ar = target_width / max(1, target_height)
    def _score(s):
        w, h = s
        return (abs(w / h - target_ar), abs(w * h - target_width * target_height))
    return min(OPENAI_SUPPORTED_SIZES, key=_score)


def _normalize_source_image(source_bytes: bytes) -> bytes:
    src = Image.open(io.BytesIO(source_bytes)).convert("RGBA")
    buf = io.BytesIO()
    src.save(buf, format="PNG")
    return buf.getvalue()


def _crop_band_in_canvas(
    openai_w: int, openai_h: int, target_w: int, target_h: int
) -> tuple[int, int, int, int]:
    """
    Return (band_top, band_bot, band_left, band_right) — the region of the
    openai_w×openai_h canvas that _resize_to_target will keep.
    """
    scale  = max(target_w / openai_w, target_h / openai_h)
    fill_w = int(openai_w * scale)
    fill_h = int(openai_h * scale)
    y_crop = (fill_h - target_h) // 2
    x_crop = (fill_w - target_w) // 2
    band_top  = max(0, int(y_crop / scale))
    band_bot  = min(openai_h, int((y_crop + target_h) / scale))
    band_left = max(0, int(x_crop / scale))
    band_right = min(openai_w, int((x_crop + target_w) / scale))
    return band_top, band_bot, band_left, band_right


# ── pre-composition for extreme-wide ─────────────────────────────────────────

def _precompose_extreme_wide_canvas(
    source_bytes: bytes,
    openai_w: int, openai_h: int,
    target_w: int, target_h: int,
) -> tuple[bytes, int, int, int, int]:
    """
    Build a openai_w×openai_h canvas where:
    - The blurred-stretched source fills the whole canvas as background.
    - The source is scaled to fit inside the crop-band and pasted centred there.

    Returns (canvas_bytes, band_top, band_bot, band_left, band_right).
    OpenAI's job is then only to extend/clean the background zones.
    """
    band_top, band_bot, band_left, band_right = _crop_band_in_canvas(
        openai_w, openai_h, target_w, target_h
    )
    band_w = band_right - band_left
    band_h = band_bot - band_top

    src = Image.open(io.BytesIO(source_bytes)).convert("RGB")
    src_w, src_h = src.size

    # Background layer: stretch source to full canvas + heavy blur
    bg = src.resize((openai_w, openai_h), Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(radius=45))

    # Foreground: scale source to fill as much of the band as possible
    scale_to_band = min(band_w / src_w, band_h / src_h)
    # For extreme-wide targets the band height is tiny; let source fill the band height
    # and extend as far right as it can — content-first layout
    scaled_w = max(1, int(src_w * scale_to_band))
    scaled_h = max(1, int(src_h * scale_to_band))
    src_scaled = src.resize((scaled_w, scaled_h), Image.Resampling.LANCZOS)

    paste_x = band_left + (band_w - scaled_w) // 2
    paste_y = band_top  + (band_h - scaled_h) // 2

    canvas = bg.copy()
    canvas.paste(src_scaled, (paste_x, paste_y))

    print(
        f"[OPENAI-PRECOMPOSE] Band rows {band_top}–{band_bot} ({band_h}px) "
        f"cols {band_left}–{band_right} ({band_w}px) | "
        f"source scaled to {scaled_w}×{scaled_h} pasted at ({paste_x},{paste_y})"
    )

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return buf.getvalue(), band_top, band_bot, band_left, band_right


# ── prompt builders ───────────────────────────────────────────────────────────

def _build_extreme_wide_prompt(
    user_prompt: str,
    openai_w: int, openai_h: int,
    target_w: int, target_h: int,
    band_top: int, band_bot: int,
    band_left: int, band_right: int,
) -> str:
    """
    Dedicated prompt for extreme-wide targets (AR > 3.5).
    The canvas is already pre-composed: source sits in the crop band,
    surrounding area is a blurred placeholder.
    OpenAI must extend the background seamlessly — nothing else.
    """
    tgt_ar  = target_w / target_h
    band_h  = band_bot - band_top
    band_w  = band_right - band_left
    z1 = band_left + band_w // 3
    z2 = band_left + 2 * band_w // 3

    brand_line = (
        f"\nBRAND / STYLE CONTEXT (use only for background tone): {user_prompt}"
        if user_prompt and user_prompt.strip() else ""
    )

    return f"""TASK: Complete this pre-composited ultra-wide digital signage banner canvas.

CANVAS YOU ARE EDITING: {openai_w} × {openai_h} px
FINAL DELIVERY SIZE: {target_w} × {target_h} px  (ratio {tgt_ar:.1f}:1 — EXTREME WIDE BANNER)

━━ WHAT IS ALREADY ON THE CANVAS ━━
Rows {band_top} – {band_bot}  (the center {band_h}px horizontal band, columns {band_left}–{band_right}):
  → The ORIGINAL BRAND CONTENT is placed here — logos, text, product, imagery.
  → DO NOT touch, move, redraw, or recompose anything in this band.

Rows 0 – {band_top} and {band_bot} – {openai_h}  (above and below the brand band):
  → Currently filled with a blurred color approximation.
  → YOUR JOB: replace this with a seamless, natural extension of the brand background.

━━ YOUR ONLY TWO TASKS ━━
1. EXTEND THE BACKGROUND into the blurred top/bottom zones.
   Match the exact colors, gradients, and textures visible at the edges of the brand band.
   No hard seams. No color jumps. The join must be invisible.

2. FILL THE FULL WIDTH if the brand content does not already span columns 0 – {openai_w}.
   Use the same background style to extend left and right so the canvas feels intentional
   and wide — like a physical LED roadside billboard.

━━ LAYOUT REFERENCE (center band, rows {band_top}–{band_bot}) ━━
  Left zone   cols 0 – {z1}:    main visual / product / hero image
  Center zone cols {z1} – {z2}:  headline text / key message / price
  Right zone  cols {z2} – {openai_w}: logo / call-to-action / brand name
Keep this structure intact. Do not rearrange it.

━━ STRICT PROHIBITIONS ━━
✗ Do NOT redraw, recompose, or artistically reinterpret the brand content
✗ Do NOT move any text, logo, or subject from where it already sits
✗ Do NOT add new objects, people, or graphics not in the source
✗ Do NOT duplicate any element
✗ Do NOT leave blurred placeholder zones — replace them entirely
✗ Do NOT add black bars, white bars, or solid-color padding
✗ Do NOT stretch or distort any element{brand_line}

OUTPUT: A single seamless {openai_w}×{openai_h}px image.
The center {band_h}px strip (rows {band_top}–{band_bot}) will be cropped to the
final {target_w}×{target_h}px delivery. Make that band pixel-perfect."""


def _build_size_directive(
    openai_w: int, openai_h: int, target_w: int, target_h: int
) -> str:
    """Size/crop hint appended to regular prompts for moderate wide/tall cases."""
    tgt_ar    = target_w / target_h
    native_ar = openai_w / openai_h

    if tgt_ar >= native_ar * 1.5:
        scale    = target_w / openai_w
        scaled_h = int(openai_h * scale)
        band_top = (scaled_h - target_h) // 2
        band_bot = scaled_h - target_h - band_top
        band_pct = round(target_h / scaled_h * 100)
        return (
            f"\n\n━━ SIZE CONSTRAINT ━━\n"
            f"Renders at: {openai_w}×{openai_h}px → final {target_w}×{target_h}px ({tgt_ar:.2f}:1)\n"
            f"Top {band_top}px and bottom {band_bot}px will be cropped. "
            f"Only center {band_pct}% of height survives.\n"
            f"Place ALL content in the central horizontal band. "
            f"Spread across full {openai_w}px width.━━━━━━━━━━━━━━━━━━━━━━━"
        )

    if tgt_ar <= native_ar / 1.5:
        scale    = target_h / openai_h
        scaled_w = int(openai_w * scale)
        band_l   = (scaled_w - target_w) // 2
        band_r   = scaled_w - target_w - band_l
        band_pct = round(target_w / scaled_w * 100)
        return (
            f"\n\n━━ SIZE CONSTRAINT ━━\n"
            f"Renders at: {openai_w}×{openai_h}px → final {target_w}×{target_h}px ({tgt_ar:.2f}:1)\n"
            f"Left {band_l}px and right {band_r}px will be cropped. "
            f"Only center {band_pct}% of width survives.\n"
            f"Place ALL content in the central vertical band.━━━━━━━━━━━━━━━━━━━━━━━"
        )

    return f"\n\n[Renders at {openai_w}×{openai_h}px → rescaled to {target_w}×{target_h}px]"


# ── post-processing ───────────────────────────────────────────────────────────

def _resize_to_target(image_bytes: bytes, target_w: int, target_h: int) -> bytes:
    """
    Scale-to-fill then center-crop — no stretching.
    Matches the band positions communicated to OpenAI in the prompt.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    src_w, src_h = img.size
    src_ar = src_w / src_h
    tgt_ar = target_w / target_h

    if abs(src_ar - tgt_ar) / tgt_ar < 0.05:
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        print(f"[OPENAI-RESIZE] Direct scale (AR match) → {target_w}×{target_h}")
    else:
        scale  = max(target_w / src_w, target_h / src_h)
        fill_w = max(target_w, int(src_w * scale))
        fill_h = max(target_h, int(src_h * scale))
        img    = img.resize((fill_w, fill_h), Image.Resampling.LANCZOS)
        x = (fill_w - target_w) // 2
        y = (fill_h - target_h) // 2
        img = img.crop((x, y, x + target_w, y + target_h))
        print(
            f"[OPENAI-RESIZE] Scale-fill {src_w}×{src_h} → {fill_w}×{fill_h}, "
            f"center-crop ({x},{y}) → {target_w}×{target_h}"
        )

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


# ── main entry point ──────────────────────────────────────────────────────────

async def call_openai_image_edit(
    source_bytes: bytes,
    prompt: str,
    target_width: int,
    target_height: int,
) -> bytes:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in .env")

    openai_w, openai_h = _closest_openai_size(target_width, target_height)
    tgt_ar = target_width / target_height

    if tgt_ar >= EXTREME_WIDE_AR_THRESHOLD:
        # ── Extreme-wide path ────────────────────────────────────────────────
        # Pre-compose source into the exact crop band, then ask OpenAI to fill
        # only the background zones — no full recomposition needed.
        print(
            f"[OPENAI] EXTREME-WIDE path | AR {tgt_ar:.2f}:1 | "
            f"target {target_width}×{target_height} | native {openai_w}×{openai_h}"
        )
        canvas_bytes, band_top, band_bot, band_left, band_right = (
            await asyncio.get_event_loop().run_in_executor(
                None,
                _precompose_extreme_wide_canvas,
                source_bytes, openai_w, openai_h, target_width, target_height,
            )
        )
        full_prompt = _build_extreme_wide_prompt(
            user_prompt=prompt,
            openai_w=openai_w, openai_h=openai_h,
            target_w=target_width, target_h=target_height,
            band_top=band_top, band_bot=band_bot,
            band_left=band_left, band_right=band_right,
        )
        send_bytes = canvas_bytes

    else:
        # ── Standard path ────────────────────────────────────────────────────
        print(
            f"[OPENAI] STANDARD path | AR {tgt_ar:.2f}:1 | "
            f"target {target_width}×{target_height} | native {openai_w}×{openai_h}"
        )
        send_bytes = await asyncio.get_event_loop().run_in_executor(
            None, _normalize_source_image, source_bytes
        )
        size_directive = _build_size_directive(openai_w, openai_h, target_width, target_height)
        full_prompt = (prompt + size_directive)[:4000]

    print(f"[OPENAI] Sending prompt ({len(full_prompt)} chars) to {OPENAI_MODEL}")

    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(
            OPENAI_EDIT_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            files={"image": ("source.png", send_bytes, "image/png")},
            data={
                "model": OPENAI_MODEL,
                "prompt": full_prompt[:4000],
                "size": f"{openai_w}x{openai_h}",
                "n": "1",
            },
        )

        if resp.status_code != 200:
            print(f"[OPENAI] API error {resp.status_code}: {resp.text[:300]}")
            resp.raise_for_status()

        result = resp.json()

    b64_data = result["data"][0].get("b64_json")
    if not b64_data:
        raise RuntimeError("OpenAI returned no image data")

    raw_bytes = base64.b64decode(b64_data)
    raw_bytes = await asyncio.get_event_loop().run_in_executor(
        None, _resize_to_target, raw_bytes, target_width, target_height
    )

    print(f"[OPENAI] Done — {target_width}×{target_height}")
    return raw_bytes
