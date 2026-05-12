"""
banner_2640x288.py — Dedicated Gemini recomposer for 2640×288 ultra-wide QMS strip.

9.2:1 aspect ratio requires:
  1. A HORIZONTAL input sheet fed to Gemini (not the standard portrait grid).
     The image editing API preserves approximate input orientation, so a wide
     landscape input produces a wide landscape output.
  2. A prompt that enforces left-to-right zone distribution and full-height fill.
  3. Exact sticker-paste fidelity — no redrawing of any component.
"""

import io
import json
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("banner_2640x288")

TARGET_W = 2640
TARGET_H = 288


def _build_horizontal_sheet(
    components: list[dict],
    layer_paths: dict[int, Path | None],
    target_w: int = TARGET_W,
    target_h: int = TARGET_H,
) -> Image.Image:
    """
    Build a single-row horizontal reference sheet at EXACTLY the target 9.2:1 AR.

    The sheet width is FIXED at target_ar × SHEET_H — components are scaled to
    fit equal-width slots within that fixed width.  The old approach used
    max(content_width, target_ar_width) which let the sheet balloon to 30:1+
    when there were many/wide components, causing Gemini 400 errors.
    """
    from banner_2072x252 import get_alpha_bbox

    PAD = 8
    TARGET_AR = target_w / target_h  # 9.167 for 2640×288

    # Keep sheet within Gemini's image-size limits (~3072px on longest side).
    # 2048px wide at 9.2:1 → 223px tall — clear, detailed, accepted by the API.
    MAX_SHEET_W = 2048
    SHEET_H = max(target_h, int(MAX_SHEET_W / TARGET_AR))  # ~223px
    COMP_H = int(SHEET_H * 0.82)
    LABEL_H = 24

    # ── FIXED sheet width at exact target AR ────────────────────────────────
    # This is the key: the sheet AR must match the output AR so Gemini's editing
    # API preserves the orientation and we get a 9.2:1 output without squishing.
    sheet_w = int(SHEET_H * TARGET_AR)  # exactly 9.2:1, ≈2048px

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except Exception:
        font = ImageFont.load_default()

    n = len(components)
    # Allocate equal-width slots. Background gets half-width since it's wide content.
    bg_count = sum(1 for c in components if c.get("type") == "background")
    fg_count = n - bg_count
    usable_w = sheet_w - PAD * (n + 1)
    # Weight: fg slots get 1 unit each, bg slots get 0.5 units
    total_units = fg_count * 1.0 + bg_count * 0.5
    unit_w = max(30, int(usable_w / max(total_units, 1)))

    sheet = Image.new("RGB", (sheet_w, SHEET_H + LABEL_H), (50, 50, 50))
    draw = ImageDraw.Draw(sheet)

    x = PAD
    for i, comp in enumerate(components):
        ctype = comp.get("type", "?")
        path = layer_paths.get(i)

        slot_w = max(30, unit_w // 2 if ctype == "background" else unit_w)

        thumb: Image.Image | None = None
        if path and path.exists():
            try:
                raw = Image.open(path).convert("RGBA")
                _, _, _, _, cropped = get_alpha_bbox(raw)
                # Scale to fill COMP_H, then clamp width to slot_w
                scale_h = COMP_H / max(cropped.height, 1)
                tw = max(1, int(cropped.width * scale_h))
                th = COMP_H
                if tw > slot_w:
                    # Too wide for slot — scale down to fit slot width instead
                    scale_w = slot_w / max(cropped.width, 1)
                    tw = slot_w
                    th = max(1, int(cropped.height * scale_w))
                thumb = cropped.resize((tw, th), Image.LANCZOS)
            except Exception as e:
                logger.warning(f"Could not load layer {i}: {e}")

        if thumb is None:
            thumb = Image.new("RGBA", (slot_w // 2, COMP_H), (120, 120, 120, 255))

        # Centre thumb in slot (horizontally and vertically)
        paste_x = x + (slot_w - thumb.width) // 2
        paste_y = (COMP_H - thumb.height) // 2 + 2
        if thumb.mode == "RGBA":
            sheet.paste(thumb, (paste_x, paste_y), thumb.split()[3])
        else:
            sheet.paste(thumb, (paste_x, paste_y))

        # Label
        label = f"[{i}]{ctype}"
        if comp.get("text_content"):
            label += f' "{comp["text_content"][:14]}"'
        draw.text((x + 2, SHEET_H + 2), label, fill=(220, 220, 220), font=font)

        # Slot divider
        if i < n - 1:
            draw.line([(x + slot_w, 0), (x + slot_w, SHEET_H)],
                      fill=(150, 150, 150), width=1)

        x += slot_w + PAD

    logger.info(f"Horizontal sheet: {sheet_w}×{SHEET_H + LABEL_H} "
                f"(AR {sheet_w / (SHEET_H + LABEL_H):.1f}:1, target {TARGET_AR:.1f}:1)")
    return sheet


async def recompose_with_gemini_vision(
    output_dir: str | Path,
    target_w: int = TARGET_W,
    target_h: int = TARGET_H,
    save_path: str | Path | None = None,
    original_image_path: str | Path | None = None,
    temperature: float = 0.1,
) -> bytes:
    """
    Compose isolated components into a 2640×288 ultra-wide horizontal strip.

    Key design choices:
    - Feeds Gemini a HORIZONTAL input sheet (not the standard portrait grid).
      The editing API preserves input orientation, so wide-in → wide-out.
    - Prompt enforces left-to-right zone distribution and full-height component fill.
    - Exact sticker fidelity: components are copied, never redrawn.
    """
    from gemini_decomposition.api_client import gemini_edit_image
    from banner_2072x252 import _load_layer_pngs, recompose_banner

    output_dir = Path(output_dir)
    components_file = output_dir / "components.json"
    if not components_file.exists():
        raise FileNotFoundError(f"components.json not found in {output_dir}")

    raw = json.loads(components_file.read_text())
    metadata = raw.get("metadata", {}) if isinstance(raw, dict) else {}
    components = raw["components"] if isinstance(raw, dict) else raw
    logger.info(f"Loaded {len(components)} components from {output_dir}")

    layer_paths = _load_layer_pngs(output_dir, len(components))

    # ── Build horizontal input sheet (9.2:1 landscape) ─────────────────────────
    logger.info("Building horizontal landscape reference sheet...")
    sheet = _build_horizontal_sheet(components, layer_paths, target_w, target_h)
    sheet_path = output_dir / "component_sheet_horizontal.png"
    sheet.save(str(sheet_path))
    logger.info(f"Horizontal sheet saved → {sheet_path}")

    # ── High-res component stickers ─────────────────────────────────────────────
    HIGH_RES_TYPES = {"photo", "image", "logo", "text"}
    extra_image_parts: list[bytes] = []
    extra_image_types: list[str] = []
    extra_image_labels: list[str] = []
    for i, comp in enumerate(components):
        if comp.get("type", "") not in HIGH_RES_TYPES:
            continue
        lp = layer_paths.get(i)
        if lp and lp.exists():
            try:
                extra_image_parts.append(lp.read_bytes())
                ctype = comp.get("type", "?")
                extra_image_types.append(ctype)
                extra_image_labels.append(f"{ctype.upper()}: {comp.get('description', '')[:60]}")
                logger.info(f"Added hi-res sticker: layer_{i:02d} ({ctype})")
            except Exception as e:
                logger.warning(f"Could not read layer {i}: {e}")

    # ── Prompt ──────────────────────────────────────────────────────────────────
    # IMPORTANT: do NOT include raw text_content strings for text components.
    # Leaking the text string into the prompt causes Gemini to re-render the text
    # with its own font instead of pasting the sealed image crop that was provided.
    comp_lines = []
    for i, c in enumerate(components):
        ctype = c.get("type", "?")
        if c.get("type") == "text":
            comp_lines.append(f"  [{i}] TEXT [SEALED STICKER — paste as-is, NO retyping]: {c.get('description', '')[:90]}")
        else:
            comp_lines.append(f"  [{i}] {ctype}: {c.get('description', '')[:90]}")

    # ── Image numbering MUST match the actual API order ──────────────────────
    # gemini_edit_image assembles parts as:
    #   parts[0] = sheet_bytes           → IMAGE 1 (always)
    #   parts[1] = original_image_bytes  → IMAGE 2 (if provided)
    #   parts[2+]= extra_image_parts     → IMAGE 3+ (if original provided) or IMAGE 2+ (if not)
    has_original = bool(original_image_path and Path(original_image_path).exists())
    extras_start_idx = 3 if has_original else 2

    original_context = ""
    if has_original:
        original_context = (
            "IMAGE 2 (original source ad — brand reference ONLY): For brand colour/atmosphere reference. "
            "Its layout is portrait — your output MUST be ultra-wide landscape, NOT portrait.\n"
        )

    has_text_stickers = "text" in extra_image_types
    extra_context = ""
    if extra_image_parts:
        # Build per-image lines so Gemini knows exactly which image is which sticker.
        per_sticker_lines = []
        for j, (etype, elabel) in enumerate(zip(extra_image_types, extra_image_labels)):
            img_num = extras_start_idx + j
            if etype == "text":
                per_sticker_lines.append(
                    f"  IMAGE {img_num} — TEXT STICKER ({elabel}): "
                    f"Paste pixel-for-pixel. Font/style baked in. DO NOT retype."
                )
            else:
                per_sticker_lines.append(
                    f"  IMAGE {img_num} — {etype.upper()} sticker ({elabel}): "
                    f"Copy 100% fidelity."
                )
        last_sticker_idx = extras_start_idx + len(extra_image_parts) - 1
        text_sticker_warning = (
            "\n⚠️  TEXT STICKERS: Each text image is a PHOTOGRAPH of the original ad typography. "
            "You MUST paste these images as-is — NEVER retype, NEVER re-render, NEVER substitute a font. "
            "The sticker IS the text — paste it, scale it, done."
            if has_text_stickers else ""
        )
        extra_context = (
            f"REFERENCE STICKER IMAGES (Images {extras_start_idx}–{last_sticker_idx}): "
            "Full-resolution pixel crops of every foreground component. "
            f"Copy each one with 100% fidelity.{text_sticker_warning}\n"
            + "\n".join(per_sticker_lines) + "\n"
        )

    # Build dynamic zone map based on actual component count.
    # Do NOT include text_content strings in zone labels — this prevents Gemini
    # from reading the text and retyping it with its own font.
    fg_comps = [(i, c) for i, c in enumerate(components) if c.get("type") != "background"]
    zone_pct = 100 // max(len(fg_comps), 1)
    zone_lines = []
    for z, (i, c) in enumerate(fg_comps):
        lo = z * zone_pct
        hi = lo + zone_pct if z < len(fg_comps) - 1 else 100
        label = c.get("type", "element")
        zone_lines.append(f"  {lo}%–{hi}%: [{i}] {label}")
    zone_map = "\n".join(zone_lines)

    prompt = f"""
████████████████████████████████████████████████████████████████████████
  OUTPUT FORMAT — ABSOLUTE REQUIREMENT (read before anything else)
████████████████████████████████████████████████████████████████████████

Your output image MUST be an ULTRA-WIDE horizontal strip.
Exact target: {target_w} × {target_h} pixels  →  {target_w/target_h:.1f} : 1 aspect ratio.

This means the output is NINE TIMES wider than it is tall.
• ✅ CORRECT:  ~{target_w}px wide  ×  ~{target_h}px tall  (9:1 landscape strip)
• ❌ FAILURE:  ~1000px wide × ~1000px tall  (square — unacceptable)
• ❌ FAILURE:  ~1000px wide × ~500px tall   (2:1 landscape — still wrong)
• ❌ FAILURE:  ~500px wide  × ~1000px tall  (portrait — completely wrong)

The INPUT IMAGE is already at this extreme 9.2:1 ultra-wide ratio.
YOUR OUTPUT MUST MATCH that same extreme ultra-wide ratio.
If you output anything other than an extreme horizontal strip you have failed.

████████████████████████████████████████████████████████████████████████

IMAGE 1 (horizontal component reference sheet): Shows ALL components laid out side-by-side with index labels [0], [1], etc. Use this to understand the visual elements.
{original_context}{extra_context}COMPONENTS in this ad (use every one):
{chr(10).join(comp_lines)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 1 — TEXT IS A LOGO: NEVER RETYPE, NEVER RE-RENDER (highest priority):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every text element in this ad (headlines, body copy, URLs, taglines) is provided
as a FULL-RESOLUTION IMAGE CROP in the sticker images above.

RULE: Treat every text sticker EXACTLY like a brand logo image — you paste it, you do NOT redraw it.

❌ FORBIDDEN — any of these is an automatic failure:
   • Typing the text yourself in any font (even the "same" font)
   • Re-rendering text with an AI font or system font
   • Approximating the lettering style
   • Changing weight (bold↔regular), style (italic↔upright), or spacing

✅ REQUIRED:
   • Take the text sticker image → scale it to fit the banner height → paste it.
   • The sticker crop IS the final text — there is nothing to interpret or rewrite.
   • If the original shows a condensed bold italic (e.g. "24HR LASTING HOLD"),
     your output must show that EXACT sticker crop at that EXACT condensed bold italic style.

Think of it this way: you have no keyboard in this task. You cannot type.
All text is delivered pre-rendered as sealed image crops. Paste. Done.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 2 — ELEMENT SIZE: MASSIVE, NOT TINY (critical — Gemini often fails here):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The strip is only {target_h}px tall. This is VERY SHORT. Elements must be HUGE to be visible.

MANDATORY HEIGHT RULE — no exceptions:
  Every foreground element (logo, text, product, widget, icon) MUST be scaled so its
  height is AT LEAST {int(target_h * 0.82)}px tall (= 82% of {target_h}px strip height).
  Elements shorter than {int(target_h * 0.6)}px are invisible at this scale — do NOT do that.

ZOOM IN MENTAL MODEL:
  Imagine you are holding the strip 5cm from your face.
  Each element should look ENORMOUS — nearly touching the top edge AND the bottom edge.
  If you can see more than {int(target_h * 0.12)}px of empty space above OR below any element → scale it up.

CONCRETE EXAMPLES for this {target_h}px strip:
  ✅ Logo height: {int(target_h * 0.85)}px  (CORRECT — large, fills the strip)
  ✅ Text height: {int(target_h * 0.70)}px  (CORRECT — big and readable)
  ❌ Logo height: {int(target_h * 0.25)}px  (WRONG — tiny dot, must scale up 3-4x)
  ❌ Text height: {int(target_h * 0.15)}px  (WRONG — unreadable, must scale up 5x)

The background bleeds to every edge (top, bottom, left, right) with no white margins.
Foreground elements are centred vertically within the strip.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 3 — HORIZONTAL ZONE MAP (left → right):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Place each component in its assigned horizontal zone. Fill the full width:

{zone_map}

Each component owns its zone. No two components share the same horizontal region.
Background seamlessly fills any horizontal gap between components.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RULE 4 — STICKER FIDELITY (copy, never redraw):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Every component is a SEALED STICKER from the reference images.
Copy each one pixel-for-pixel — same shape, same colours, same proportions.

• Logos: identical marks, wordmarks — never simplified or redrawn.
• Products: identical shape, exact label text, same colours.
• Shapes / widgets: identical fill, border radius, corner treatment.
• Each element appears EXACTLY ONCE. Never duplicate any element.

████████████████████████████████████████████████████████████████████████
  FINAL CHECK before you render:
  □ Is my output approximately {target_w}px wide × {target_h}px tall?
  □ Is the width ~9× the height? (9.2 : 1 aspect ratio)
  □ Does the background fill every pixel edge-to-edge?
  □ Is every foreground element at least {int(target_h*0.82)}px tall (82% of {target_h}px)?
  □ Are all {len(components)} components present, each exactly once?
  □ Is ALL text taken from the provided sticker crops — NOT retyped by me?
  □ Do all text elements show the EXACT font style from the sticker (not approximated)?
If any box is unchecked → fix it before outputting.
████████████████████████████████████████████████████████████████████████

Output ONLY the single ultra-wide horizontal strip image. Nothing else."""

    logger.info(
        f"Sending horizontal sheet to Gemini ({target_w}×{target_h}, "
        f"{len(extra_image_parts)} hi-res stickers)..."
    )

    buf = io.BytesIO()
    sheet.save(buf, format="PNG")
    sheet_bytes = buf.getvalue()

    original_bytes = None
    if original_image_path and Path(original_image_path).exists():
        original_bytes = Path(original_image_path).read_bytes()
        logger.info(f"Included original for colour reference: {original_image_path}")

    result_bytes = await gemini_edit_image(
        sheet_bytes,
        prompt,
        timeout=300,
        original_image_bytes=original_bytes,
        temperature=temperature,
        extra_image_parts=extra_image_parts,
    )

    if not result_bytes:
        logger.warning("Gemini returned no image — falling back to manual compositor")
        return await recompose_banner(output_dir, target_w, target_h, save_path)

    # Final resize to exact target dimensions
    try:
        result_img = Image.open(io.BytesIO(result_bytes)).convert("RGB")
        logger.info(f"Gemini output size: {result_img.size}")
        if result_img.size != (target_w, target_h):
            logger.info(f"Resizing {result_img.size} → {target_w}×{target_h}")
            result_img = result_img.resize((target_w, target_h), Image.LANCZOS)
        out_buf = io.BytesIO()
        result_img.save(out_buf, format="PNG")
        result_bytes = out_buf.getvalue()
    except Exception as e:
        logger.warning(f"Could not process result image: {e}")

    if save_path:
        Path(save_path).write_bytes(result_bytes)
        logger.info(f"Banner saved → {save_path}")

    logger.info(f"Done. {target_w}×{target_h}, {len(result_bytes):,} bytes")
    return result_bytes
