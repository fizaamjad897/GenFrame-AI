"""
gemini_isolate.py — Isolate design components using Gemini AI.

Uses Vertex AI (gemini-2.5-pro) for image analysis and text generation.
Uses Gemini image editing model (gemini-3.1-flash-image) for component isolation.

For each component Gemini detects:
  - background / photo / image  →  PNG  (raster, via Gemini image editing)
  - text                        →  PNG  (bounding-box crop — avoids hallucination)
  - icon / logo / shape / button→  SVG  (Vertex AI text model writes SVG code)
                                +  PNG  (raster fallback also kept)

Usage:
    python gemini_isolate.py
    python gemini_isolate.py --image path/to/image.png
    python gemini_isolate.py --url https://...
    python gemini_isolate.py --parallel
"""

import os
import sys
import io
import re
import json
import time
import asyncio
import argparse
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from PIL import Image

load_dotenv()

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("gemini_isolate")

# ── Config ────────────────────────────────────────────────────────────────────
# Using Vertex AI models instead of Gemini
VISION_MODEL = "gemini-2.5-pro"  # Component analysis + image understanding
TEXT_MODEL = "gemini-2.5-pro"    # SVG writing
DEFAULT_IMAGE = str(
    Path(__file__).parent.parent / "test_layer_output" / "00_original.png"
)
OUTPUT_BASE = Path(__file__).parent / "output"

# Types that get SVG output (API writes SVG code)
SVG_TYPES = {"logo", "icon", "shape", "button"}
# Types that stay as PNG only
PNG_ONLY_TYPES = {"scene", "background", "image", "photo", "illustration", "text"}

# ── Prompts ───────────────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """Analyze this design image and identify every distinct visual component as separate layers.

STRICT RULES:
1. Each component must be a SINGLE, independent visual element — never combine multiple unrelated elements into one
2. LOGOS and ICONS are ALWAYS a single component — never split a logo's text, icon mark, or tagline into separate components. A logo is ONE unit even if it contains both a symbol and text. Do NOT list any part of a logo as a separate "text" component — all text that belongs to a logo must stay inside that logo entry only.
3. BUTTONS: list the shape AND its label text as SEPARATE components with DIFFERENT box_2d
4. Background is ONLY the flat color, gradient, or pattern behind everything — NOT the full design
5. If the design is shown within a real-world scene (billboard, mockup, poster on wall), list the scene as type "scene" and the design background separately as type "background"
6. Bounding boxes must be TIGHT — wrap only the specific element, not the area around it
7. If two elements overlap (e.g. a frame around a photo), give them DIFFERENT box_2d values — the frame should have a LARGER box_2d than the photo inside it
8. Every piece of standalone text (not part of a logo) that is visually distinct (different font, size, or position) should be its own component
9. Decorative elements (lines, dividers, borders) are type "shape" — describe their exact appearance

For each component, describe its EXACT visual appearance: specific colors (hex if obvious), font style, content, and position.

EXTRA FIELDS:
- For "text" components: include ALL of these fields:
  - "text_content": exact text string visible in the image (required)
  - "font_family": the font family name as accurately as possible (e.g. "Bebas Neue", "Playfair Display", "Montserrat", "Arial". If unknown: "sans-serif" or "serif")
  - "font_weight": "bold", "semibold", "normal", or "light"
  - "text_color": hex color of the text (e.g. "#FFFFFF", "#000000", "#C9A94E")
  - "text_align": "left", "center", or "right"
- For "scene" or "background" components that are a SOLID flat color (not a photo or texture): include "solid_color" with the exact hex code (e.g. "#6B7346")
- For "background" components with a texture or gradient: do NOT include "solid_color"

Return ONLY this JSON (no markdown):
{
  "components": [
    {"type": "scene", "description": "solid muted olive green background surrounding the poster", "box_2d": [0, 0, 1000, 1000], "solid_color": "#6B7346"},
    {"type": "background", "description": "dark blue to purple gradient fill covering entire canvas", "box_2d": [0, 0, 1000, 1000]},
    {"type": "text", "description": "'Save More Today' — large white serif headline, centered at top", "text_content": "Save More Today", "font_family": "Playfair Display", "font_weight": "bold", "text_color": "#FFFFFF", "text_align": "center", "box_2d": [100, 50, 200, 450]},
    {"type": "image", "description": "gold credit card with chip, angled 15 degrees, centered", "box_2d": [250, 200, 550, 500]},
    {"type": "text", "description": "'0% APR for 12 months' — small white sans-serif text", "text_content": "0% APR for 12 months", "font_family": "Montserrat", "font_weight": "normal", "text_color": "#FFFFFF", "text_align": "center", "box_2d": [580, 300, 620, 700]},
    {"type": "shape", "description": "green (#008955) rounded rectangle button background", "box_2d": [650, 350, 720, 650]},
    {"type": "text", "description": "'Apply Now' — white sans-serif button label text", "text_content": "Apply Now", "font_family": "Montserrat", "font_weight": "bold", "text_color": "#FFFFFF", "text_align": "center", "box_2d": [660, 380, 710, 620]},
    {"type": "logo", "description": "white stylized B arrow logo mark, bottom-right", "box_2d": [800, 800, 900, 900]}
  ]
}

Valid types: scene, background, text, image, photo, shape, button, icon, logo
Box format: [ymin, xmin, ymax, xmax] in 0-1000 coordinates (top-left = 0,0)
IMPORTANT: background box_2d should ALWAYS be [0, 0, 1000, 1000] unless the design area doesn't fill the image.
"""


def _is_light_element(description: str) -> bool:
    """Detect if a component is light/white colored from its description."""
    light_keywords = ["white", "light", "bright", "cream", "ivory", "pale", "silver"]
    desc_lower = description.lower()
    return any(kw in desc_lower for kw in light_keywords)


def _build_other_elements_list(component: dict, all_components: list) -> str:
    """Build a list of OTHER elements with bounding boxes that must be removed."""
    others = []
    for c in all_components:
        if c is component:
            continue
        c_type = c.get("type", "element")
        if c_type in ("background", "scene"):
            continue
        c_desc = c.get("description", "")[:70]
        box = c.get("box_2d")
        box_str = f" [box: y{box[0]}-{box[2]}, x{box[1]}-{box[3]}]" if box and len(box) == 4 else ""
        others.append(f"  - [{c_type}]{box_str} {c_desc}")
    if not others:
        return ""
    return "Elements that MUST be completely removed (with their pixel regions):\n" + "\n".join(others[:15])


def _get_foreground_boxes(component: dict, all_components: list, img_w: int, img_h: int) -> list:
    """Return pixel bounding boxes of all foreground elements (excluding self and scene/bg)."""
    boxes = []
    for c in all_components:
        if c is component:
            continue
        if c.get("type") in ("background", "scene"):
            continue
        box = c.get("box_2d")
        if not box or len(box) != 4:
            continue
        ymin, xmin, ymax, xmax = box
        left   = int(max(0, xmin / 1000.0 * img_w))
        top    = int(max(0, ymin / 1000.0 * img_h))
        right  = int(min(img_w,  xmax / 1000.0 * img_w))
        bottom = int(min(img_h,  ymax / 1000.0 * img_h))
        if right > left and bottom > top:
            boxes.append((left, top, right, bottom))
    return boxes


def _box_2d_hint(component: dict) -> str:
    """Convert box_2d to a human-readable location hint."""
    box = component.get("box_2d")
    if not box or len(box) != 4:
        return ""
    ymin, xmin, ymax, xmax = box
    # Describe position in human terms
    vert = "top" if ymin < 333 else ("middle" if ymin < 666 else "bottom")
    horiz = "left" if xmin < 333 else ("center" if xmin < 666 else "right")
    return f"Location: {vert}-{horiz} area of the image (approximately {ymin/10:.0f}%-{ymax/10:.0f}% from top, {xmin/10:.0f}%-{xmax/10:.0f}% from left)"


def build_isolation_prompt(component: dict, all_components: list) -> str:
    """
    Build a focused prompt for isolating one component.
    Includes spatial context and explicit removal list to prevent mixing.
    """
    comp_type = component.get("type", "element")
    comp_desc = component.get("description", "element")
    is_light = _is_light_element(comp_desc)
    location = _box_2d_hint(component)
    remove_list = _build_other_elements_list(component, all_components)

    # Pick contrasting background for visibility
    if is_light:
        bg_hex, bg_name = "#333333", "dark gray"
    else:
        bg_hex, bg_name = "#F0F0F0", "light gray"

    # ── Scene: the real-world environment behind the design ──
    if comp_type == "scene":
        fg_items = []
        for c in all_components:
            if c is component:
                continue
            box = c.get("box_2d")
            box_str = f" [y{box[0]}-{box[2]}, x{box[1]}-{box[3]}]" if box and len(box) == 4 else ""
            fg_items.append(f"  - {c.get('description', '')[:70]}{box_str}")

        return f"""TASK: Remove every single design element from this image and return only the bare background scene.

I need you to ERASE ALL of the following elements completely — use content-aware fill to replace each erased region with the natural surrounding background (sky, wall, sand, texture, etc.):

{chr(10).join(fg_items[:20])}

What to keep: ONLY the real-world environment/scene behind everything ({comp_desc}).
What to remove: EVERY element listed above — text, graphics, shapes, logos, overlays, frames, boxes — all of it gone.

Do NOT partially erase. Do NOT leave any ghosting or bleed. Each listed element must be 100% replaced with the background scene continuing naturally behind it.

Output: The background scene as if none of those design elements were ever placed on it."""

    # ── Background: the flat canvas/surface of the design ──
    if comp_type == "background":
        fg_items = []
        for c in all_components:
            if c is component or c.get("type") in ("scene",):
                continue
            box = c.get("box_2d")
            box_str = f" [y{box[0]}-{box[2]}, x{box[1]}-{box[3]}]" if box and len(box) == 4 else ""
            fg_items.append(f"  - {c.get('description', '')[:70]}{box_str}")

        return f"""TASK: Remove every single foreground element from this design image and return only the bare background surface.

I need you to ERASE ALL of the following elements completely — replace each erased region with the background color/gradient/texture that lies underneath:

{chr(10).join(fg_items[:20])}

What to keep: ONLY the background fill/color/gradient/pattern ({comp_desc}).
What to remove: EVERY element listed above — all text, all images, all shapes, all icons, all logos, all buttons — completely gone.

Do NOT partially erase. Do NOT leave outlines, shadows, or ghosting of any removed element. Each listed element must be 100% replaced with the clean background fill continuing behind it.

Output: A completely empty background surface — no content of any kind remaining, just the background."""

    # ── Text: show only the specified text ──
    if comp_type == "text":
        return f"""Isolate ONLY this specific text element from the design. Output just this text on a plain background.

Target text: {comp_desc}
{location}

Instructions:
1. Find this EXACT text in the image at the specified location
2. Keep ONLY this text — preserve its exact font, size, weight, color, and styling
3. Replace EVERYTHING else with a solid {bg_name} background ({bg_hex})
4. Do NOT include any other text, images, shapes, buttons, or design elements
5. Do NOT include nearby elements even if they are close to this text
6. The text should appear at roughly the same position in the output image

{remove_list}

Result: Just the text "{comp_desc[:50]}" on a plain {bg_hex} background, nothing else."""

    # ── Images/Photos: show only the specified image ──
    if comp_type in ("photo", "image"):
        # A full-canvas photo is the background scene — treat it like a scene:
        # remove all foreground design elements and keep only the environment.
        box_2d = component.get("box_2d")
        is_full_canvas = (
            box_2d and len(box_2d) == 4 and
            box_2d[1] <= 50 and box_2d[0] <= 50 and
            box_2d[3] >= 950 and box_2d[2] >= 950
        )
        if is_full_canvas:
            fg_items = "\n".join(
                f"  - {c.get('description', '')[:80]}"
                for c in all_components
                if c is not component and c.get("type") not in ("background",)
            )
            return f"""This is a background photograph. Remove ALL overlaid design elements and return only the clean background environment.

Target: {comp_desc}

Instructions:
1. Keep ONLY the real-world photographic scene/environment (people, surfaces, buildings, sky, props that belong naturally to the scene)
2. REMOVE every design overlay completely — erase all of the following and fill the removed areas with natural-looking surroundings using content-aware fill:
{fg_items}
3. The result should look like the original photograph was taken WITHOUT any of those design elements present
4. Do NOT add any new elements — only remove the listed overlays

Result: A clean background photograph with all design overlays removed."""

        return f"""Isolate ONLY this specific image/photo from the design. Output just this image on a plain background.

Target image: {comp_desc}
{location}

Instructions:
1. Find this EXACT image/photo in the design at the specified location
2. Keep ONLY this image with all its original details, colors, and quality
3. Replace EVERYTHING else with a clean white background (#FFFFFF)
4. Do NOT include any text overlaid on or near the image
5. Do NOT include frames, borders, or decorative elements around the image
6. Do NOT include other photos or images from the design — only this specific one
7. Crop tightly to just this image element

{remove_list}

Result: Just the image "{comp_desc[:50]}" on a white background, nothing else."""

    # ── Shapes/Buttons ──
    if comp_type in ("shape", "button"):
        return f"""Isolate ONLY this specific {comp_type} element from the design. Output just this element on a plain background.

Target element: {comp_desc}
{location}

Instructions:
1. Find this EXACT {comp_type} at the specified location in the image
2. Keep ONLY this {comp_type} — preserve its exact colors, shape, and proportions
3. Replace EVERYTHING else with a solid {bg_name} background ({bg_hex})
4. Do NOT include any text that may be on top of or inside this {comp_type} — remove text too
5. Do NOT include images, photos, or other elements near this {comp_type}
6. If this is a thin line or divider, show ONLY that line — nothing else
7. The element should appear at roughly the same position in the output image
8. CRITICAL: The background MUST be {bg_hex} — do NOT use black (#000000) or any dark color as background

{remove_list}

Result: Just the {comp_type} "{comp_desc[:50]}" on a plain {bg_hex} background, nothing else."""

    # ── Icons/Logos ──
    return f"""Isolate ONLY this specific {comp_type} from the design. Output just this element on a plain background.

Target element: {comp_desc}
{location}

Instructions:
1. Find this EXACT {comp_type} at the specified location in the image
2. Keep ONLY this {comp_type} — preserve its exact colors, shape, and details
3. Replace EVERYTHING else with a solid {bg_name} background ({bg_hex})
4. Do NOT include any text near or around this {comp_type}
5. Do NOT include other icons, logos, or decorative elements
6. Crop tightly around just this element
7. CRITICAL: The background MUST be {bg_hex} — do NOT use black (#000000) or any dark color as background

{remove_list}

Result: Just the {comp_type} "{comp_desc[:50]}" on a plain {bg_hex} background, nothing else."""


SVG_PROMPT_TEMPLATE = """You are an SVG expert. Generate a clean, valid SVG for this single UI element.


Element: "{description}"
Type: {type}
Target size: {svg_width} x {svg_height} pixels

Rules:
- Output ONLY raw SVG code starting with <svg and ending with </svg> — no markdown, no explanation
- Use viewBox="0 0 {svg_width} {svg_height}" — match the target size exactly
- Background MUST be fully transparent — do NOT add ANY <rect> or background fill of any kind (no black, no white, no solid color backdrop). The SVG must have zero background elements.
- For TEXT elements:
  - Use the exact text content from the description
  - Font: if "serif" → font-family="Georgia, 'Times New Roman', serif"
          if "sans-serif" or unspecified → font-family="Montserrat, Arial, sans-serif"
          if "bold" → add font-weight="bold"
  - Google Fonts preferred: Montserrat, Playfair Display, Roboto, Open Sans, Lato, Poppins, Oswald, Bebas Neue
  - Use exact fill color: white=#FFFFFF, gold=#C9A94E
  - Center text using text-anchor="middle" x="50%" y="50%" dominant-baseline="middle"
  - IMPORTANT: Scale font-size to fit the viewBox. Calculate: font-size = ({svg_height} × 0.25) for single line, smaller for multi-line
  - Multi-line: use <tspan> with dy="1.2em" on separate lines, ensure all text fits within viewBox
  - Text must fit completely within the viewBox — NEVER let text be clipped or overflow
  - Add padding around text if needed (keep 10% margins)
- For SHAPES/BUTTONS:
  - Render ONLY the geometric shape itself — fill color, borders, rx/ry for rounded corners
  - CRITICAL: Do NOT include ANY text, labels, or text content inside the SVG — text elements are handled as separate editable layers
  - If the description mentions text ON the shape (e.g. a sign with words), render only the shape frame/background, leave the interior empty
- For ICONS/LOGOS:
  - Reproduce the COMPLETE logo — icon mark, wordmark, tagline, and any text that is part of the logo — all as ONE SVG
  - For logo text/wordmarks: use <text> elements with the exact font family and weight described. If the font is unknown, use the closest matching Google Font
  - For icon marks and symbols: use geometric <path>, <circle>, <rect>, <polygon> elements with exact colors
  - Fill the entire viewBox — the logo should scale to fit
  - Background MUST be transparent — zero background rectangles
- Minimal code — only what's needed

SVG:"""

# ── Gemini — Component Analysis ───────────────────────────────────────────────

async def analyze_components(image: Image.Image) -> list:
    """Use Vertex AI Vision directly to list all components. No count limit."""
    from api_client import gemini_generate_with_image

    # Encode image as PNG bytes
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    image_bytes = buf.getvalue()

    prompt = f"""{ANALYSIS_PROMPT}

Analyze the provided image and return ONLY the JSON response as specified above."""

    logger.info(f"Analyzing components with {VISION_MODEL}…")

    try:
        raw = await gemini_generate_with_image(image_bytes, prompt)
        raw = raw.strip()
    except Exception as e:
        logger.error(f"Failed to call Vertex AI: {e}")
        return []

    # Strip markdown fences if present
    raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("```").strip()

    try:
        data = json.loads(raw)
    except Exception:
        logger.error(f"Failed to parse component JSON: {raw[:200]}")
        return []

    # Response can be: a list of components directly, or {"components": [...]}
    if isinstance(data, list):
        components = data
    else:
        components = data.get("components", [])

    # Ensure background is always first and present
    has_bg = any(c.get("type") == "background" for c in components)
    if not has_bg:
        logger.warning("No background detected — inserting placeholder")
        components.insert(0, {
            "type": "background",
            "description": "canvas background fill"
        })

    logger.info(f"Found {len(components)} components (no limit applied)")
    for i, c in enumerate(components):
        logger.info(f"  [{i:02d}] type={c.get('type','?'):<14} {c.get('description','')[:60]}")

    return components


# ── Bounding-Box Crop (fallback / text bypass) ────────────────────────────────

def _crop_component_from_image(component: dict, image: Image.Image) -> bytes | None:
    """
    Crop the component's bounding box directly from the original image.
    Used as:
      - Primary method for 'text' type (image models hallucinate text)
      - Fallback for all other types when Gemini image edit fails
    """
    box_2d = component.get("box_2d")
    if not box_2d or len(box_2d) != 4:
        # No box_2d — return the full image as fallback
        buf = io.BytesIO()
        image.convert("RGB").save(buf, format="PNG")
        return buf.getvalue()

    ymin, xmin, ymax, xmax = box_2d
    left   = int(max(0, xmin / 1000.0 * image.width))
    top    = int(max(0, ymin / 1000.0 * image.height))
    right  = int(min(image.width,  xmax / 1000.0 * image.width))
    bottom = int(min(image.height, ymax / 1000.0 * image.height))

    if right <= left or bottom <= top:
        return None

    cropped = image.crop((left, top, right, bottom))
    buf = io.BytesIO()
    cropped.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


# ── PIL — Background Masking Fallback ─────────────────────────────────────────

def _sample_edge_color(image: Image.Image, left: int, top: int, right: int, bottom: int) -> tuple:
    """
    Sample pixels from a border strip around a bounding box and return the median color.
    Falls back to (0, 0, 0) if the sampling region is out of bounds.
    """
    import numpy as np

    img_w, img_h = image.width, image.height
    margin = max(4, min(20, int(min(img_w, img_h) * 0.015)))
    samples = []

    # Sample top strip
    sy1, sy2 = max(0, top - margin), max(0, top)
    if sy2 > sy1:
        strip = image.crop((max(0, left), sy1, min(img_w, right), sy2))
        samples.append(np.array(strip).reshape(-1, 3))

    # Sample bottom strip
    sy1, sy2 = min(img_h, bottom), min(img_h, bottom + margin)
    if sy2 > sy1:
        strip = image.crop((max(0, left), sy1, min(img_w, right), sy2))
        samples.append(np.array(strip).reshape(-1, 3))

    # Sample left strip
    sx1, sx2 = max(0, left - margin), max(0, left)
    if sx2 > sx1:
        strip = image.crop((sx1, max(0, top), sx2, min(img_h, bottom)))
        samples.append(np.array(strip).reshape(-1, 3))

    # Sample right strip
    sx1, sx2 = min(img_w, right), min(img_w, right + margin)
    if sx2 > sx1:
        strip = image.crop((sx1, max(0, top), sx2, min(img_h, bottom)))
        samples.append(np.array(strip).reshape(-1, 3))

    if not samples:
        return (128, 128, 128)

    all_pixels = np.concatenate(samples, axis=0)
    median_color = tuple(int(v) for v in np.median(all_pixels, axis=0))
    return median_color


def _mask_foreground_from_background(
    component: dict,
    all_components: list,
    image: Image.Image,
) -> bytes:
    """
    PIL fallback for background/scene layers when Gemini fails to erase foreground elements.

    For each foreground component's bounding box:
      1. Sample the median color from edge pixels surrounding the box
      2. Fill the box region with that color (approximates background continuing underneath)

    This is not content-aware fill, but it reliably removes foreground duplication
    and produces a clean placeholder background layer.
    """
    from PIL import ImageDraw

    img_w, img_h = image.width, image.height
    result = image.copy().convert("RGB")
    draw = ImageDraw.Draw(result)

    fg_boxes = _get_foreground_boxes(component, all_components, img_w, img_h)

    if not fg_boxes:
        logger.info("  _mask_foreground: no foreground boxes to erase — returning original")
        buf = io.BytesIO()
        result.save(buf, format="PNG")
        return buf.getvalue()

    logger.info(f"  _mask_foreground: erasing {len(fg_boxes)} foreground regions via PIL")

    for (left, top, right, bottom) in fg_boxes:
        left   = max(0, left)
        top    = max(0, top)
        right  = min(img_w, right)
        bottom = min(img_h, bottom)
        if right <= left or bottom <= top:
            continue

        fill_color = _sample_edge_color(image, left, top, right, bottom)
        draw.rectangle([left, top, right - 1, bottom - 1], fill=fill_color)

    buf = io.BytesIO()
    result.save(buf, format="PNG")
    logger.info(f"  _mask_foreground: done ({buf.tell()} bytes)")
    return buf.getvalue()


# ── Vertex AI — Raster Isolation (PNG) ────────────────────────────────────────

async def isolate_component_png(
    component: dict,
    all_components: list,
    image: Image.Image,
    index: int,
) -> bytes | None:
    """Use Gemini image editing to isolate one component. Returns PNG bytes."""
    from api_client import gemini_edit_image

    comp_desc = component.get("description", f"component_{index}")
    comp_type = component.get("type", "image")
    logger.info(f"  PNG [{index:02d}]: {comp_desc[:60]}…")

    # TEXT — bounding-box crop only (image models hallucinate/regenerate text)
    if comp_type == "text":
        logger.info(f"  [{index:02d}] Text component — using bounding-box crop")
        return _crop_component_from_image(component, image)

    # SOLID COLOR — generate fill directly from the color Gemini identified
    solid_color = component.get("solid_color", "").strip()
    if solid_color and (comp_type in ("scene", "background")):
        logger.info(f"  [{index:02d}] Solid color {comp_type} ({solid_color}) — generating fill directly")
        img_fill = Image.new("RGB", (image.width, image.height), solid_color)
        buf = io.BytesIO()
        img_fill.save(buf, format="PNG")
        return buf.getvalue()

    # TINY ELEMENTS — Gemini image model cannot reliably isolate sub-30-unit elements
    box_2d = component.get("box_2d")
    if box_2d and len(box_2d) == 4:
        ymin, xmin, ymax, xmax = box_2d
        box_w = xmax - xmin
        box_h = ymax - ymin
        if box_w < 30 or box_h < 30:
            logger.info(f"  [{index:02d}] Tiny element ({box_w}×{box_h} units) — using bounding-box crop")
            return _crop_component_from_image(component, image)

    # Convert source image to PNG bytes
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="PNG")
    image_bytes = buf.getvalue()

    # Build the detailed isolation prompt
    isolation_prompt = build_isolation_prompt(component, all_components)

    # 2 retries (3 total attempts). _ai_studio_image_request handles only 429s
    # internally; all other failures surface as None so this loop fires cleanly
    # with no attempt multiplication.
    for attempt in range(3):
        logger.info(f"  [{index:02d}] Gemini image edit attempt {attempt + 1}/3…")
        result = await gemini_edit_image(image_bytes, isolation_prompt, timeout=120)
        if result:
            logger.info(f"  ✓ PNG [{index:02d}] ({len(result)} bytes)")
            return result
        if attempt < 2:
            wait = (attempt + 1) * 5
            logger.warning(f"  [{index:02d}] No result — retrying in {wait}s…")
            await asyncio.sleep(wait)

    logger.warning(f"  [{index:02d}] All 3 attempts failed — falling back to bounding-box crop")
    return _crop_component_from_image(component, image)


# ── Gemini — SVG Generation ───────────────────────────────────────────────────

def _fix_svg_attributes(svg_str: str, target_w: int, target_h: int) -> str:
    """Ensure SVG has explicit width, height, and overflow attributes."""
    svg_tag_end = svg_str.index(">")
    svg_tag = svg_str[:svg_tag_end]

    if 'width=' not in svg_tag:
        svg_str = svg_str.replace('<svg ', f'<svg width="{target_w}" height="{target_h}" ', 1)
    if 'overflow=' not in svg_tag:
        svg_str = svg_str.replace('<svg ', '<svg overflow="visible" ', 1)
    return svg_str


def _strip_svg_background(svg_str: str) -> str:
    """
    Remove any full-canvas background rectangle that Gemini may add despite being told not to.
    Targets <rect> elements that:
      - cover the full canvas (x/y = 0 or absent, width/height = 100% or match viewBox)
      - use fill="black", fill="#000", fill="#000000", fill="white", fill="#fff", etc.
      - appear as the first child of the <svg> root (typical AI-generated backdrop)
    Uses regex so we don't need an XML parser dependency.
    """
    # Match standalone <rect .../> or <rect ...></rect> that look like backgrounds.
    # A background rect typically has no meaningful x/y offset and a solid fill.
    bg_rect_pattern = re.compile(
        r'<rect\b[^>]*\bfill\s*=\s*["\']'
        r'(?:black|#000|#000000|white|#fff|#ffffff|#[0-9a-fA-F]{3,6})'
        r'["\'][^>]*/?>(?:</rect>)?',
        re.IGNORECASE,
    )

    def is_background_rect(match: re.Match) -> bool:
        tag = match.group(0)
        # Must not have x/y offset (or x=0/y=0)
        x_val = re.search(r'\bx\s*=\s*["\']([^"\']+)["\']', tag)
        y_val = re.search(r'\by\s*=\s*["\']([^"\']+)["\']', tag)
        if x_val and x_val.group(1) not in ("0", "0.0"):
            return False
        if y_val and y_val.group(1) not in ("0", "0.0"):
            return False
        # width/height must be 100%, "100", or any numeric value >= 50 (catches "400", "200", etc.)
        w_val = re.search(r'\bwidth\s*=\s*["\']([^"\']+)["\']', tag)
        h_val = re.search(r'\bheight\s*=\s*["\']([^"\']+)["\']', tag)
        if w_val:
            wv = w_val.group(1)
            if wv not in ("100%",) and not (wv.replace('.','',1).isdigit() and float(wv) >= 50):
                return False
        if h_val:
            hv = h_val.group(1)
            if hv not in ("100%",) and not (hv.replace('.','',1).isdigit() and float(hv) >= 50):
                return False
        return True

    cleaned = bg_rect_pattern.sub(
        lambda m: "" if is_background_rect(m) else m.group(0),
        svg_str,
    )
    return cleaned


async def generate_svg(component: dict, index: int, png_bytes: bytes | None = None) -> str | None:
    """
    Ask Vertex AI to write SVG code for this component.
    If png_bytes is provided, the API receives the actual isolated PNG as visual reference
    so it can trace shapes accurately instead of guessing.
    Returns raw SVG string or None on failure.
    """
    import base64

    comp_desc = component.get("description", f"component_{index}")
    comp_type = component.get("type", "element")

    # Calculate SVG viewBox from box_2d dimensions
    box_2d = component.get("box_2d")
    svg_width, svg_height = 400, 200  # fallback
    if box_2d and len(box_2d) == 4:
        ymin, xmin, ymax, xmax = box_2d
        box_w = xmax - xmin
        box_h = ymax - ymin
        if box_w > 0 and box_h > 0:
            aspect = box_w / box_h
            if aspect >= 1:
                svg_width = min(600, max(100, box_w))
                svg_height = max(20, int(svg_width / aspect))
            else:
                svg_height = min(600, max(100, box_h))
                svg_width = max(20, int(svg_height * aspect))
        # Add padding for text elements to prevent cutoff
        if comp_type == "text":
            svg_width = int(svg_width * 1.15)  # Add 15% padding for text overflow
            svg_height = int(svg_height * 1.15)
    elif comp_type in ("icon", "logo"):
        svg_width, svg_height = 100, 100

    base_prompt = SVG_PROMPT_TEMPLATE.format(
        description=comp_desc, type=comp_type,
        svg_width=svg_width, svg_height=svg_height,
    )
    # Prepend hard constraint so the model never enters description mode
    svg_constraint = (
        "IMPORTANT: Your response must contain ONLY raw SVG code. "
        "Do NOT describe the image. Do NOT explain anything. "
        "Do NOT use markdown. Start your response directly with <svg and end with </svg>.\n\n"
    )
    prompt = svg_constraint + base_prompt

    if png_bytes:
        prompt += (
            "\n\nThe image above shows the actual isolated element — "
            "use it as visual reference for accurate colors, shapes, and proportions."
        )

    logger.info(f"  SVG [{index:02d}]: {comp_desc[:60]}… (viewBox {svg_width}x{svg_height})")

    from api_client import gemini_generate_with_image, vertex_ai_generate

    for attempt in range(3):
        try:
            if png_bytes:
                svg_text = await gemini_generate_with_image(png_bytes, prompt)
            else:
                svg_text = await vertex_ai_generate(prompt)
            svg_text = svg_text.strip()

            # Strip all markdown/code-fence variants
            svg_text = re.sub(r"^```[a-z]*\n?", "", svg_text, flags=re.MULTILINE)
            svg_text = re.sub(r"\n?```$", "", svg_text, flags=re.MULTILINE).strip()
            # Strip leading prose before <svg (model sometimes explains first)
            svg_text = re.sub(r"^[^<]*(?=<svg)", "", svg_text, flags=re.DOTALL).strip()

            if "<svg" in svg_text and "</svg>" in svg_text:
                start = svg_text.index("<svg")
                end = svg_text.rindex("</svg>") + len("</svg>")
                svg_clean = svg_text[start:end]
                # Post-process: ensure width/height/overflow attributes and strip bg rects
                svg_clean = _fix_svg_attributes(svg_clean, svg_width, svg_height)
                svg_clean = _strip_svg_background(svg_clean)
                logger.info(f"  ✓ SVG [{index:02d}] ({len(svg_clean)} chars)")
                return svg_clean
            else:
                logger.warning(
                    f"  [{index:02d}] Response missing <svg> tags (attempt {attempt+1}). "
                    f"Got: {svg_text[:120]!r}"
                )
                if attempt < 2:
                    await asyncio.sleep(3 * (attempt + 1))

        except Exception as e:
            logger.error(f"  [{index:02d}] SVG error (attempt {attempt+1}): {e}")
            if attempt < 2:
                await asyncio.sleep(3 * (attempt + 1))

    return None


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="Isolate design components into PNG (raster) + SVG (vector)."
    )
    parser.add_argument("--image",    default=DEFAULT_IMAGE)
    parser.add_argument("--url",      default=None)
    parser.add_argument("--parallel", action="store_true", default=True,
                        help="Run PNG isolations in parallel (default: on).")
    parser.add_argument("--sequential", action="store_true",
                        help="Run PNG isolations sequentially (slower, avoids rate limits).")
    args = parser.parse_args()
    if args.sequential:
        args.parallel = False

    # ── Load image ────────────────────────────────────────────────────────────
    if args.url:
        import httpx
        logger.info(f"Downloading: {args.url[:80]}")
        async with httpx.AsyncClient(timeout=60) as hc:
            r = await hc.get(args.url)
            r.raise_for_status()
            image = Image.open(io.BytesIO(r.content)).convert("RGB")
    else:
        img_path = Path(args.image)
        if not img_path.exists():
            print(f"ERROR: File not found: {img_path}"); sys.exit(1)
        logger.info(f"Loading: {img_path}")
        image = Image.open(img_path).convert("RGB")

    logger.info(f"Image size: {image.width}×{image.height}")

    # ── Output dir ────────────────────────────────────────────────────────────
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = OUTPUT_BASE / f"isolation_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output: {out_dir}")
    image.save(out_dir / "00_original.png")

    # ═════════════════════════════════════════════════════
    print()
    print("═" * 62)
    print("  STEP 1 — Component Analysis  (no layer limit)")
    print("═" * 62)
    components = await analyze_components(image)

    if not components:
        print("ERROR: No components detected"); sys.exit(1)

    # Wrap components with metadata including original image dimensions
    # so the assembler can use them without needing the image file
    components_data = {
        "metadata": {
            "original_width": image.width,
            "original_height": image.height,
        },
        "components": components,
    }
    (out_dir / "components.json").write_text(json.dumps(components_data, indent=2))
    print(f"\n  Detected {len(components)} components — API decided the count.")

    # Classify
    svg_components  = [c for c in components if c.get("type", "") in SVG_TYPES]
    png_components  = components  # all get PNG
    print(f"  → {len(png_components)} components get PNG isolation")
    print(f"  → {len(svg_components)} components also get SVG  "
          f"({', '.join(c.get('type') for c in svg_components)})")

    # ═════════════════════════════════════════════════════
    print()
    print("═" * 62)
    print(f"  STEP 2 — PNG + SVG (parallel per-component)")
    print("═" * 62)
    print()

    # Semaphore: max concurrent Gemini calls (avoid rate-limit 429s)
    MAX_CONCURRENT = 6
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async def process_component(comp: dict, i: int):
        """Get PNG then immediately generate SVG (if needed) — pipelined per component."""
        async with sem:
            png = await isolate_component_png(comp, components, image, i)
        svg = None
        if comp.get("type", "") in SVG_TYPES:
            async with sem:
                svg = await generate_svg(comp, i, png)
        return i, png, svg

    if args.parallel:
        logger.info(f"Running all components in parallel (semaphore={MAX_CONCURRENT})…")
        component_results = await asyncio.gather(
            *[process_component(comp, i) for i, comp in enumerate(components)]
        )
    else:
        component_results = []
        for i, comp in enumerate(components):
            component_results.append(await process_component(comp, i))

    # Unpack ordered results
    component_results = sorted(component_results, key=lambda x: x[0])
    png_bytes_list = [r[1] for r in component_results]
    svg_results: dict[int, str | None] = {r[0]: r[2] for r in component_results}

    # ═════════════════════════════════════════════════════
    print()
    print("═" * 62)
    print("  STEP 3 — Saving Results")
    print("═" * 62)
    print()

    results = []
    png_ok = 0
    svg_ok = 0

    for i, (comp, png_bytes) in enumerate(zip(components, png_bytes_list)):
        comp_type = comp.get("type", "unknown")
        comp_desc = comp.get("description", f"component_{i}")
        safe = "".join(
            c if c.isalnum() or c in " _-" else ""
            for c in comp_desc[:40]
        ).strip().replace(" ", "_")

        png_filename = f"layer_{i:02d}_{comp_type}_{safe}.png"
        svg_filename = f"layer_{i:02d}_{comp_type}_{safe}.svg"
        entry = {"index": i, "type": comp_type, "description": comp_desc}

        # Save PNG
        if png_bytes:
            (out_dir / png_filename).write_bytes(png_bytes)
            sz = (out_dir / png_filename).stat().st_size // 1024
            print(f"  ✓ PNG  [{i:02d}] {png_filename}  ({sz} KB)")
            entry["png"] = png_filename
            png_ok += 1
        else:
            print(f"  ✗ PNG  [{i:02d}] FAILED — {comp_desc[:45]}")
            entry["png"] = None

        # Save SVG (only for eligible types)
        svg_text = svg_results.get(i)
        if comp_type in SVG_TYPES:
            if svg_text:
                (out_dir / svg_filename).write_text(svg_text, encoding="utf-8")
                sz = (out_dir / svg_filename).stat().st_size // 1024
                print(f"  ✓ SVG  [{i:02d}] {svg_filename}  ({sz} KB)")
                entry["svg"] = svg_filename
                svg_ok += 1
            else:
                print(f"  ✗ SVG  [{i:02d}] FAILED — {comp_desc[:45]}")
                entry["svg"] = None

        results.append(entry)

    (out_dir / "results.json").write_text(json.dumps(results, indent=2))

    print()
    print("═" * 62)
    print(f"  PNG: {png_ok}/{len(components)}  |  SVG: {svg_ok}/{len(svg_components)}")
    print(f"  Output: {out_dir}")
    print("═" * 62)

    os.system(f'open "{out_dir}"')


if __name__ == "__main__":
    asyncio.run(main())
