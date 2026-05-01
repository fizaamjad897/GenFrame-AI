"""
server.py — Standalone FastAPI server for image decomposition + AI canvas editing.

Integrates Recreative AI wrappers:
  - Vertex AI: Text generation, image analysis
  - FAL AI: Text-to-image generation

Endpoints:
    POST /api/decompose       — Upload image → decompose → return Template4 JSON
    POST /api/edit-template   — AI-powered template editing via natural language
    POST /api/generate/prompt — Generate image from text prompt
    GET  /                    — Serve demo.html frontend

Run:
    python -m gemini_decomposition.server
    # or
    cd gemini_decomposition && python server.py
"""

import os
import io
import re
import sys
import json
import time
import copy
import uuid
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import quote, unquote

from fastapi import FastAPI, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from PIL import Image
import httpx

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
THIS_DIR = Path(__file__).parent

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(title="Design Automation Studio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ══════════════════════════════════════════════════════════════════════════════
# Error sanitisation — strip vendor / provider names from client-facing messages
# ══════════════════════════════════════════════════════════════════════════════

_VENDOR_PATTERN = re.compile(
    r'gemini|vertex[\s\-]?ai|google|googleapis|generativelanguage|'
    r'openai|anthropic|fal[\s\-]?ai|'
    r'api[\s\-]?key|service[\s\-]?account|oauth|bearer|'
    r'https?://\S+|models/\S+',
    re.IGNORECASE,
)

def _sanitize_error(exc: Exception, fallback: str = "An unexpected error occurred. Please try again.") -> str:
    """Return a client-safe error message with no vendor/provider references."""
    msg = str(exc)
    if _VENDOR_PATTERN.search(msg):
        return fallback
    # Strip raw HTTP status lines like "404 Not Found for url '...'"
    msg = re.sub(r'\d{3}\s+\w[\w\s]*for url\s+\S+', '', msg).strip()
    return msg or fallback


# ══════════════════════════════════════════════════════════════════════════════
# Health Check Route
# ══════════════════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Simple health check endpoint."""
    return JSONResponse(content={
        "status": "online",
        "service": "Visual Engine Backend API",
        "endpoints": ["/api/decompose", "/api/generate/prompt", "/api/edit-template"]
    })


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/generate/prompt — Generate image from text prompt
# Uses FAL AI for image generation + Vertex AI for commentary
# ══════════════════════════════════════════════════════════════════════════════

VALID_ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"]
ASPECT_RATIO_ALIASES = {
    "landscape": "16:9", "square": "1:1", "portrait": "9:16",
    "mobile": "9:16", "desktop": "16:9",
}



def _validate_aspect_ratio(ratio: str) -> str:
    if ratio in VALID_ASPECT_RATIOS:
        return ratio
    return ASPECT_RATIO_ALIASES.get(ratio.lower(), "1:1")


def _aspect_ratio_to_pixels(ratio: str, base: int = 1024) -> tuple[int, int]:
    """Convert an aspect ratio string like '16:9' to pixel dimensions."""
    try:
        w, h = ratio.split(":")
        w, h = int(w), int(h)
        if w >= h:
            return base, int(base * h / w)
        else:
            return int(base * w / h), base
    except Exception:
        return base, base


@app.post("/api/generate/prompt", response_class=JSONResponse)
async def generate_from_prompt(request: Request):
    """Generate image from text prompt using Gemini image generation (Vertex AI)."""
    from api_client import gemini_edit_image
    from gemini_assembler import upload_to_cdn

    body = await request.json()
    prompt = body.get("prompt", "").strip()
    aspect_ratio = body.get("aspect_ratio", "1:1")

    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    validated_ratio = _validate_aspect_ratio(aspect_ratio)

    try:
        logger.info(f"Generating image via Gemini image model: {prompt[:80]}…")

        # Gemini image generation: pass empty 1x1 white PNG as source (text-to-image via edit)
        from PIL import Image as _PILImage
        import io as _io
        blank_w, blank_h = _aspect_ratio_to_pixels(validated_ratio)
        blank = _PILImage.new("RGB", (blank_w, blank_h), (255, 255, 255))
        buf = _io.BytesIO()
        blank.save(buf, format="PNG")
        blank_bytes = buf.getvalue()

        image_data = await gemini_edit_image(
            blank_bytes,
            f"Generate a photorealistic image: {prompt}",
            timeout=120,
        )

        if not image_data:
            raise HTTPException(status_code=500, detail="Image generation failed. Please try again.")

        logger.info(f"Image generated successfully")

        # Upload to CDN
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"generated_{timestamp}_{unique_id}.png"
        cdn_url = upload_to_cdn(image_data, filename, "image/png")

        # Generate creative director commentary via Vertex AI
        text_response = "Image generated successfully."
        try:
            commentary_prompt = (
                f"You are a professional Creative Director. A user has just generated an image "
                f"based on the prompt: '{prompt}'. Provide a grounded, insightful, and "
                f"natural-sounding comment on the result. Focus on elements like composition, "
                f"lighting, or how well the aesthetic matches the intent. Avoid being overly "
                f"enthusiastic or using robotic praise. Be concise (2 sentences)."
            )
            from api_client import vertex_ai_generate
            text_response = await vertex_ai_generate(commentary_prompt, model="gemini-2.5-flash", timeout=15)
        except Exception as e:
            logger.warning(f"Commentary generation failed: {e}")

        logger.info(f"Generated image: {cdn_url} (ratio={validated_ratio})")

        return JSONResponse(content={
            "url": cdn_url,
            "name": filename,
            "text": text_response,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation error: {e}")
        raise HTTPException(status_code=500, detail=_sanitize_error(e, "Image generation failed. Please try again."))


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/decompose — Full pipeline: image → Template4 JSON
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/decompose")
async def decompose(
    image_url: str = Form(None),
    image_file: UploadFile = File(None),
    parallel: bool = Form(True),  # Enable parallel processing by default
    temperature: float = Form(0.05), # Expose creativity control to frontend
    target_width: int = Form(2070), # Expose banner width
    target_height: int = Form(253) # Expose banner height
):
    """
    Decompose an image and generate an 8:1 panoramic banner.
    Takes 2-4 minutes depending on component count.
    """
    if not image_url and not image_file:
        raise HTTPException(status_code=400, detail="Provide image_url or image_file")

    try:
        from wrapper import process_ad_to_banner

        if image_file:
            source = await image_file.read()
        else:
            source = image_url

        # Run the entire pipeline (Isolation -> Banner)
        result = await process_ad_to_banner(
            image_source=source,
            target_width=target_width,
            target_height=target_height,
            temperature=temperature
        )

        if result["status"] == "error":
            raise RuntimeError(result["error_message"])

        return JSONResponse(content={
            "banner_url": result.get("banner_image_path", ""),
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Decompose error: {e}")
        raise HTTPException(status_code=500, detail=_sanitize_error(e, "Image processing failed. Please try again."))


# ══════════════════════════════════════════════════════════════════════════════
# AI Template Editing — copied from Canvas-AI-Editor/main.py (no auth/credits)
# ══════════════════════════════════════════════════════════════════════════════

def resize_large_image(pil_image, max_pixels=89_000_000):
    """Resize image if it exceeds the maximum pixel limit."""
    width, height = pil_image.size
    total_pixels = width * height
    if total_pixels <= max_pixels:
        return pil_image
    scale_factor = (max_pixels / total_pixels) ** 0.5
    new_width = int(width * scale_factor)
    new_height = int(height * scale_factor)
    return pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def _get_plain_text(obj: dict) -> str:
    """Extract plain text from a text object's Value field."""
    value = obj.get("Value", "")
    if not value:
        return obj.get("Text", "")
    decoded = unquote(value)
    plain = re.sub(r'<[^>]+>', '', decoded).strip()
    return re.sub(r'\s+', ' ', plain)


def _assign_semantic_roles(object_list: list, canvas_w: int, canvas_h: int) -> dict:
    """
    Assign a semantic role to each object index so Gemini can map natural
    language ("the headline", "the background", "the logo") to exact objects.
    """
    roles = {}

    # Collect text objects sorted by font size desc, then Y position asc
    text_objs = [
        (i, obj) for i, obj in enumerate(object_list) if obj.get("type") == "text"
    ]
    text_objs_sorted = sorted(
        text_objs,
        key=lambda t: (-t[1].get("fontSize", 0), t[1].get("Y", 0))
    )
    for rank, (i, _) in enumerate(text_objs_sorted):
        if rank == 0:
            roles[i] = "HEADLINE"
        elif rank == 1:
            roles[i] = "SUBHEADLINE"
        elif rank == 2:
            roles[i] = "BODY-TEXT"
        else:
            roles[i] = f"TEXT-{rank+1}"

    # Collect image/shape objects
    canvas_area = canvas_w * canvas_h
    for i, obj in enumerate(object_list):
        obj_type = obj.get("type", "")
        w, h = obj.get("Width", 0), obj.get("Height", 0)
        locked = obj.get("locked", False)
        svg_prop = obj.get("SvgProperty")
        sort_order = obj.get("SortOrder", 99)
        obj_area = w * h
        is_full_canvas = obj_area >= canvas_area * 0.85

        if obj_type == "image":
            if is_full_canvas and locked:
                roles[i] = "BASE-BACKGROUND"
            elif is_full_canvas and not locked:
                roles[i] = "BACKGROUND-PHOTO"
            elif svg_prop and svg_prop.get("content"):
                name_lower = obj.get("Name", "").lower()
                if any(k in name_lower for k in ("logo", "icon", "brand")):
                    roles[i] = "LOGO"
                else:
                    roles[i] = "SVG-SHAPE"
            else:
                # Use position to describe image
                x, y = obj.get("X", 0), obj.get("Y", 0)
                vert = "top" if y < canvas_h * 0.33 else ("middle" if y < canvas_h * 0.66 else "bottom")
                horiz = "left" if x < canvas_w * 0.33 else ("center" if x < canvas_w * 0.66 else "right")
                roles[i] = f"IMAGE-{vert}-{horiz}"

        elif obj_type == "shape":
            roles[i] = "SHAPE"

    return roles


def generate_template_summary(template_json: dict) -> str:
    """Generate a compact summary of template objects for AI context.

    Each object gets a semantic role label (HEADLINE, SUBHEADLINE, BACKGROUND, LOGO, etc.)
    so the AI can map natural-language references to exact objects without selection.
    """
    pages = template_json.get("pages", [])
    if not pages:
        return "Empty template with no objects."

    canvas_w = template_json.get("PageWidths", {}).get("double", 1024)
    canvas_h = template_json.get("PageHeights", {}).get("double", 512)
    summary_lines = [
        f"Canvas: {canvas_w}x{canvas_h}px",
        "NOTE: Target objects by [index], Name, Id prefix, text content, OR semantic role (e.g. HEADLINE, BACKGROUND-PHOTO, LOGO).",
    ]

    object_list = pages[0].get("objectList", [])
    roles = _assign_semantic_roles(object_list, canvas_w, canvas_h)

    for i, obj in enumerate(object_list):
        obj_type = obj.get("type", "unknown")
        name = obj.get("Name", f"Object {i}")
        obj_id = obj.get("Id", "")
        x, y = obj.get("X", 0), obj.get("Y", 0)
        w, h = obj.get("Width", 0), obj.get("Height", 0)
        rotation = obj.get("RotateDegree", 0)
        visible = obj.get("IsVisible", True)
        locked = obj.get("locked", False)
        role = roles.get(i, "")

        # Role tag makes natural language matching reliable
        role_tag = f" [{role}]" if role else ""
        line = f'[{i}]{role_tag} {obj_type} "{name}" (id:{obj_id[:8]}) pos:({x},{y}) size:{w}x{h}'

        if rotation:
            line += f" rot:{rotation}deg"
        if not visible:
            line += " [HIDDEN]"
        if locked:
            line += " [LOCKED]"

        if obj_type == "text":
            plain = _get_plain_text(obj)
            if plain:
                display = plain[:80] + ("..." if len(plain) > 80 else "")
                line += f' text:"{display}"'
            font = obj.get("fontFamily", "")
            size = obj.get("fontSize", "")
            color = obj.get("color", "")
            if font: line += f" font:{font}"
            if size: line += f" size:{size}px"
            if color: line += f" color:{color}"
            if obj.get("isJustifyCenter"): line += " align:center"
            elif obj.get("isJustifyRight"): line += " align:right"
            elif obj.get("isJustifyLeft"): line += " align:left"
            if obj.get("isBold"): line += " bold"
            if obj.get("isItalic"): line += " italic"

        elif obj_type == "image":
            img_type = obj.get("ImageType", "")
            if img_type: line += f" imgType:{img_type}"
            img_url = obj.get("DefaultImageUrl", "")
            if img_url:
                short_url = img_url.split("/")[-1][:30]
                line += f" url:...{short_url}"
            svg_prop = obj.get("SvgProperty")
            img_url_check = obj.get("DefaultImageUrl", "")
            is_svg = (svg_prop and svg_prop.get("content")) or img_url_check.lower().endswith(".svg") or obj.get("ImageExtension", "").lower() == "svg"
            if is_svg:
                svg_color = svg_prop.get("DefaultColor", "") if svg_prop else ""
                line += f" hasSVG svgColor:{svg_color}"
            if obj.get("IsHFlipped"): line += " hFlipped"
            if obj.get("IsVFlipped"): line += " vFlipped"

        elif obj_type == "shape":
            shape_type = obj.get("shapeType", "rectangle")
            color = obj.get("DefaultColor", "")
            line += f" shape:{shape_type} color:{color}"
            stroke_w = obj.get("StrokeWidth", 0)
            if stroke_w:
                stroke_c = obj.get("StrokeColor", "#000")
                line += f" stroke:{stroke_w}px {stroke_c}"

        effects = obj.get("effects", {})
        if effects:
            non_default = []
            for eff_name, eff_val in effects.items():
                if isinstance(eff_val, dict):
                    v = eff_val.get("value", 50 if eff_name in ["brightness", "contrast", "saturation"] else 0)
                    default = 50 if eff_name in ["brightness", "contrast", "saturation"] else (100 if eff_name == "transparency" else 0)
                    if v != default:
                        non_default.append(f"{eff_name}:{v}")
            if non_default:
                line += f" effects:[{','.join(non_default)}]"

        summary_lines.append(line)

    return "\n".join(summary_lines)


TEMPLATE_EDITOR_OPERATIONS_SCHEMA = """Available operations (return as JSON array):

1. edit_text: Change text content
   {"op": "edit_text", "target": "<Name or Id>", "text": "<new plain text>"}

2. change_color: Change text color or shape color
   {"op": "change_color", "target": "<Name or Id>", "color": "#RRGGBB"}

3. change_font: Change font family and/or size
   {"op": "change_font", "target": "<Name or Id>", "fontFamily": "<name>", "fontSize": <number>}

4. move: Move object — either absolute (x,y) or relative (dx,dy). Use relative when user says "move right/left/up/down by N pixels"
   Absolute: {"op": "move", "target": "<Name or Id>", "x": <number>, "y": <number>}
   Relative: {"op": "move", "target": "<Name or Id>", "dx": <number>, "dy": <number>}
   Combined: {"op": "move", "target": "<Name or Id>", "dx": <number>, "dy": <number>}

5. resize: Resize object
   {"op": "resize", "target": "<Name or Id>", "width": <number>, "height": <number>}

6. rotate: Rotate object
   {"op": "rotate", "target": "<Name or Id>", "degree": <number>}

7. remove: Remove object from template
   {"op": "remove", "target": "<Name or Id>"}

8. add_text: Add a new text element
   {"op": "add_text", "name": "<name>", "text": "<content>", "x": <num>, "y": <num>, "width": <num>, "height": <num>, "fontFamily": "<font>", "fontSize": <num>, "color": "#RRGGBB", "isBold": false, "align": "left|center|right"}

9. add_shape: Add a new shape
   {"op": "add_shape", "name": "<name>", "shapeType": "rectangle", "x": <num>, "y": <num>, "width": <num>, "height": <num>, "color": "rgba(R,G,B,A)"}

10. add_image: Add a new image layer from a URL
    {"op": "add_image", "name": "<name>", "url": "<image URL>", "x": <num>, "y": <num>, "width": <num>, "height": <num>}

11. change_image: Replace an image URL on an existing image layer (ONLY when user explicitly provides a URL)
    {"op": "change_image", "target": "<Name or Id>", "url": "<new image URL>"}
    WARNING: Do NOT use this with invented/placeholder URLs. Use edit_image_with_ai instead when user describes image content.

12. flip: Flip an object
    {"op": "flip", "target": "<Name or Id>", "direction": "horizontal|vertical"}

13. change_opacity: Change object transparency (0=invisible, 100=fully opaque)
    {"op": "change_opacity", "target": "<Name or Id>", "value": <0-100>}

14. change_visibility: Show/hide an object
    {"op": "change_visibility", "target": "<Name or Id>", "visible": true|false}

15. change_effect: Modify visual effects (brightness/contrast/saturation range 0-100, default 50; blur range 0-20)
    {"op": "change_effect", "target": "<Name or Id>", "effect": "brightness|contrast|saturation|blur|tint|vignette", "value": <number>}

16. change_svg_color: Change SVG element color (applies to both fill and stroke)
    {"op": "change_svg_color", "target": "<Name or Id>", "color": "#RRGGBB"}

17. change_text_style: Bold, italic, underline
    {"op": "change_text_style", "target": "<Name or Id>", "isBold": true|false, "isItalic": true|false, "isUnderline": true|false}

18. change_alignment: Change text alignment
    {"op": "change_alignment", "target": "<Name or Id>", "align": "left|center|right|justify"}

19. change_text_shadow: Add/modify text shadow
    {"op": "change_text_shadow", "target": "<Name or Id>", "shadowColor": "#HEX", "shadowBlur": <num>, "shadowOffsetX": <num>, "shadowOffsetY": <num>}

20. change_outline: Add/modify text outline
    {"op": "change_outline", "target": "<Name or Id>", "strokeWidth": <num>, "strokeColor": "#HEX"}

21. duplicate: Duplicate an object
    {"op": "duplicate", "target": "<Name or Id>", "offsetX": <num>, "offsetY": <num>}

22. reorder: Change layer order (higher sortOrder = on top)
    {"op": "reorder", "target": "<Name or Id>", "sortOrder": <number>}

23. edit_image_with_ai: Use AI to edit a raster image with a text prompt (do NOT use on SVG objects)
    {"op": "edit_image_with_ai", "target": "<Name or Id>", "prompt": "<editing instruction>"}

24. change_line_spacing: Change text line spacing
    {"op": "change_line_spacing", "target": "<Name or Id>", "lineSpacing": "<number like 1.4>"}

25. lock: Lock/unlock an object
    {"op": "lock", "target": "<Name or Id>", "locked": true|false}

26. change_gradient: Enable/disable gradient
    {"op": "change_gradient", "target": "<Name or Id>", "enabled": true|false, "angle": <num>, "colors": [{"position": <0-100>, "rgba": "rgba(R,G,B,A)"}]}

27. regenerate_svg: Regenerate SVG code for an icon/logo/shape based on a new prompt (AI rewrites the SVG from scratch)
    {"op": "regenerate_svg", "target": "<Name or Id>", "prompt": "<describe the new design or changes>"}
"""

TEMPLATE_EDITOR_SYSTEM_PROMPT = """You are an AI template editor for a design canvas system. You receive a compact summary of objects on a canvas and a user's editing request. You must return ONLY a JSON array of operations to perform.

TEMPLATE SUMMARY:
{summary}

AVAILABLE OPERATIONS:
{operations}

═══ OBJECT IDENTIFICATION (critical — read carefully) ═══

Each object in the summary has a semantic role tag like [HEADLINE], [SUBHEADLINE], [BACKGROUND-PHOTO], [LOGO], [SVG-SHAPE], etc.
Use these roles to resolve natural-language references with NO explicit selection:

  Natural language → Semantic role → Use as "target" value
  ─────────────────────────────────────────────────────────
  "the headline" / "the title" / "the main text"      → HEADLINE        → use the Name of that object
  "the subtitle" / "the tagline" / "the subheading"   → SUBHEADLINE     → use the Name of that object
  "the body text" / "the description"                 → BODY-TEXT       → use the Name of that object
  "the background" / "the canvas bg" / "the base"     → BASE-BACKGROUND → use the Name of that object
  "the background photo" / "the scene" / "the photo"  → BACKGROUND-PHOTO→ use the Name of that object
  "the logo" / "the brand mark" / "the icon"          → LOGO            → use the Name of that object
  "the shape" / "the frame" / "the sign" / "the box"  → SVG-SHAPE or SHAPE → use the Name of that object
  "the image on the left/right/top/bottom"            → IMAGE-top-left / IMAGE-middle-center / etc → use the Name of that object
  "all text" / "every text element"                   → apply to ALL text objects individually

You may also target by:
  - Index number: use "[3]" format — e.g. target: "3"
  - Exact Name from summary — e.g. target: "Text: COCA-COLA."
  - Text content: if user says "change 'COCA-COLA' to blue", find the text object containing "COCA-COLA"
  - Id prefix: first 8 chars of the id field

═══ GENERAL RULES ═══

1. Return ONLY a valid JSON array of operations. No explanations, no markdown, no code blocks.
2. Always use the object's Name as the target (most reliable). Fall back to id prefix or index number.
3. For text editing, provide plain text only — HTML is generated automatically.
4. Keep positions within canvas bounds (canvas size listed first in summary).
5. Colors: use hex (#RRGGBB), rgb(), or rgba() formats.
6. Include ALL needed operations in one response — don't split across calls.
7. For ambiguous requests, use the semantic roles and canvas layout to make the best choice.
8. "Change all text colors" → apply change_color to EACH text object separately.
9. Font sizes are in pixels.
10. Canvas origin (0,0) is top-left. X increases right, Y increases down.
11. Relative moves ("move right 50px"): use dx/dy. Absolute ("center it"): compute x/y from canvas size.
12. CENTER horizontally: x = (canvas_width - object_width) / 2. CENTER vertically: y = (canvas_height - object_height) / 2.
13. When increasing font size significantly, also include a resize operation to expand the text box height.
14. SVG objects (marked hasSVG):
    - Color change → change_svg_color
    - Redesign → regenerate_svg
    - NEVER use edit_image_with_ai on SVG objects
15. Raster images (no hasSVG): use edit_image_with_ai for AI edits, change_image ONLY when the user explicitly provides a direct image URL.
    - NEVER invent, guess, or fabricate image URLs (no unsplash, placeholder, or example.com URLs).
    - If the user describes what they want in the image (e.g. "robot in a bank"), always use edit_image_with_ai, not change_image.
16. New elements (add_text, add_shape, add_image): position sensibly, avoid unintentional overlaps.
17. If prompt starts with [TARGET: ...], that is the pre-selected object — prioritise it for all ops.

USER REQUEST: {user_prompt}

Return ONLY the JSON array:"""


# ── Helper functions ──────────────────────────────────────────────────────────

def find_object_by_target(object_list: list, target: str) -> tuple:
    """
    Find an object by target string. Resolution order:
    1. Exact Name match (case-insensitive)
    2. Exact Id or Id prefix match
    3. Index number ("[3]" or "3")
    4. Partial Name match
    5. Text content match (searches actual text inside text objects)
    6. Semantic role keyword match (headline, background, logo, etc.)
    """
    if not target:
        return -1, None

    t = target.strip().lower()

    # 1. Exact Name match
    for i, obj in enumerate(object_list):
        if obj.get("Name", "").lower() == t:
            return i, obj

    # 2. Id match (exact or prefix)
    for i, obj in enumerate(object_list):
        obj_id = obj.get("Id", "")
        if obj_id == target or obj_id.lower().startswith(t):
            return i, obj

    # 3. Index number — support "[3]" and "3"
    index_str = t.strip("[]")
    if index_str.isdigit():
        idx = int(index_str)
        if 0 <= idx < len(object_list):
            return idx, object_list[idx]

    # 4. Partial Name match
    for i, obj in enumerate(object_list):
        if t in obj.get("Name", "").lower():
            return i, obj

    # 5. Text content match — find text object whose actual text contains the target
    for i, obj in enumerate(object_list):
        if obj.get("type") == "text":
            plain = _get_plain_text(obj).lower()
            if t in plain or plain in t:
                return i, obj

    # 6. Semantic role keyword mapping
    # Infer canvas size from the largest object (background always fills the canvas)
    inferred_w = max((obj.get("Width", 0) for obj in object_list), default=1000)
    inferred_h = max((obj.get("Height", 0) for obj in object_list), default=1000)
    roles = _assign_semantic_roles(object_list, inferred_w, inferred_h)
    role_keywords = {
        "headline":        ["HEADLINE"],
        "title":           ["HEADLINE"],
        "main text":       ["HEADLINE"],
        "header":          ["HEADLINE"],
        "subheadline":     ["SUBHEADLINE"],
        "subtitle":        ["SUBHEADLINE"],
        "tagline":         ["SUBHEADLINE"],
        "subheading":      ["SUBHEADLINE"],
        "body":            ["BODY-TEXT"],
        "description":     ["BODY-TEXT"],
        "paragraph":       ["BODY-TEXT"],
        "background":      ["BASE-BACKGROUND", "BACKGROUND-PHOTO"],
        "background photo":["BACKGROUND-PHOTO"],
        "scene":           ["BACKGROUND-PHOTO"],
        "base":            ["BASE-BACKGROUND"],
        "canvas":          ["BASE-BACKGROUND"],
        "logo":            ["LOGO"],
        "brand":           ["LOGO"],
        "icon":            ["LOGO"],
        "shape":           ["SVG-SHAPE", "SHAPE"],
        "frame":           ["SVG-SHAPE", "SHAPE"],
        "sign":            ["SVG-SHAPE", "SHAPE"],
        "box":             ["SVG-SHAPE", "SHAPE"],
        "button":          ["SHAPE"],
        "image":           ["IMAGE-top-left", "IMAGE-top-center", "IMAGE-top-right",
                            "IMAGE-middle-left", "IMAGE-middle-center", "IMAGE-middle-right",
                            "IMAGE-bottom-left", "IMAGE-bottom-center", "IMAGE-bottom-right"],
        "photo":           ["BACKGROUND-PHOTO", "IMAGE-top-left", "IMAGE-top-center",
                            "IMAGE-top-right", "IMAGE-middle-left", "IMAGE-middle-center",
                            "IMAGE-middle-right", "IMAGE-bottom-left", "IMAGE-bottom-center",
                            "IMAGE-bottom-right"],
    }
    for keyword, target_roles in role_keywords.items():
        if keyword in t:
            for i, obj in enumerate(object_list):
                if roles.get(i, "") in target_roles:
                    return i, obj

    return -1, None


def build_text_html_value(text: str, font_family: str = "Arial", font_size: int = 28,
                           color: str = "#000000", align: str = "left",
                           is_bold: bool = False, is_italic: bool = False) -> str:
    """Build URL-encoded HTML Value field for a text object."""
    inner_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    inner_text = inner_text.replace("\n", "<br>\n")
    bold_open = "<strong>" if is_bold else ""
    bold_close = "</strong>" if is_bold else ""
    italic_open = "<em>" if is_italic else ""
    italic_close = "</em>" if is_italic else ""
    html = (
        f'<div><div style="text-align: {align}; font-family: {font_family}; font-size: {font_size}px;">'
        f'{bold_open}{italic_open}'
        f'<span face="{font_family}" style="font-family:{font_family};">'
        f'<span fontsize="{font_size}" style="font-size: {font_size}px; font-family: inherit;">'
        f'{inner_text}'
        f'</span></span>'
        f'{italic_close}{bold_close}'
        f'</div>\n</div>'
    )
    return quote(html, safe='')


def rgb_to_hex(rgb_str: str) -> str:
    match = re.match(r'rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', rgb_str)
    if match:
        r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return f"#{r:02x}{g:02x}{b:02x}"
    return rgb_str


def hex_to_rgb(hex_str: str) -> str:
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r, g, b = int(hex_str[:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
        return f"rgb({r},{g},{b})"
    return hex_str


def _get_text_align(obj: dict) -> str:
    if obj.get("isJustifyCenter"): return "center"
    elif obj.get("isJustifyRight"): return "right"
    elif obj.get("isJustify"): return "justify"
    return "left"


def _rebuild_text_html(obj: dict, plain_text: str = None):
    """Rebuild Value and modifiedHtml from object's current properties."""
    if plain_text is None:
        value = obj.get("Value", "")
        if not value:
            return
        decoded = unquote(value)
        plain_text = re.sub(r'<[^>]+>', '', decoded).strip()
        plain_text = re.sub(r'\s+', ' ', plain_text)
    font = obj.get("fontFamily", "Arial")
    size = obj.get("fontSize", 28)
    color = obj.get("color", "#000000")
    is_bold = obj.get("isBold", False)
    is_italic = obj.get("isItalic", False)
    align = _get_text_align(obj)
    encoded = build_text_html_value(plain_text, font, size, color, align, is_bold, is_italic)
    obj["Value"] = encoded
    obj["modifiedHtml"] = encoded
    obj["Text"] = plain_text


async def generate_svg_from_prompt(prompt: str, obj_type: str = "icon", width: int = 200, height: int = 200) -> str | None:
    """
    Generate SVG code from a text prompt using Vertex AI.
    Returns raw SVG string or None on failure.
    """
    svg_prompt = f"""You are an SVG expert. Generate a clean, valid SVG based on this request:

Request: {prompt}
Type: {obj_type}
Target size: {width} x {height} pixels

Rules:
- Output ONLY raw SVG code starting with <svg and ending with </svg> — no markdown, no explanation
- Use viewBox="0 0 {width} {height}"
- Background MUST be transparent — do NOT add any background rectangle
- Use geometric paths, shapes, and fills to create the design
- Use descriptive colors (white=#FFFFFF, black=#000000, etc.)
- Center and scale to fill the viewBox nicely
- For text: use font-family="Montserrat, Arial, sans-serif", center with text-anchor="middle"
- Minimal code — only what's needed for the design

Generate the SVG now:"""

    try:
        from api_client import vertex_ai_generate
        svg_text = (await vertex_ai_generate(svg_prompt, timeout=60)).strip()

        # Strip markdown fences if present
        svg_text = re.sub(r"^```[a-z]*\n?", "", svg_text)
        svg_text = re.sub(r"\n?```$", "", svg_text).strip()

        if "<svg" in svg_text and "</svg>" in svg_text:
            start = svg_text.index("<svg")
            end = svg_text.rindex("</svg>") + len("</svg>")
            svg_clean = svg_text[start:end]
            
            # Ensure viewBox and proper attributes
            if 'viewBox=' not in svg_clean:
                svg_clean = svg_clean.replace('<svg', f'<svg viewBox="0 0 {width} {height}"', 1)
            if 'overflow="visible"' not in svg_clean:
                svg_clean = svg_clean.replace('<svg', f'<svg overflow="visible"', 1)
            
            logger.info(f"SVG generated from prompt: {len(svg_clean)} chars")
            return svg_clean
        else:
            logger.warning("SVG generation: Response missing <svg> tags")
            return None

    except Exception as e:
        logger.error(f"SVG generation error: {e}")
        return None


async def apply_template_operations(template_json: dict, operations: list) -> dict:
    """Apply a list of AI-generated operations to the template JSON surgically."""
    template = copy.deepcopy(template_json)
    object_list = template["pages"][0]["objectList"]
    applied = []
    errors = []
    image_edits_needed = []

    for op in operations:
        op_type = op.get("op", "")
        target = op.get("target", "")

        try:
            if op_type == "edit_text":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"edit_text: Object '{target}' not found"); continue
                old_text = _get_plain_text(obj)
                new_text = op.get("text", "")
                _rebuild_text_html(obj, new_text)
                logger.info(f"[edit_text] idx={idx} name='{obj.get('Name')}' old='{old_text[:60]}' → new='{new_text[:60]}'")
                logger.info(f"[edit_text] obj.Text after rebuild: '{obj.get('Text', '')[:60]}'")
                applied.append(f"edit_text: Changed text of '{obj.get('Name')}'")

            elif op_type == "change_color":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_color: Object '{target}' not found"); continue
                new_color = op.get("color", "#000000")
                if obj.get("type") == "text":
                    obj["color"] = hex_to_rgb(new_color) if new_color.startswith("#") else new_color
                    obj["Color"] = hex_to_rgb(new_color) if new_color.startswith("#") else new_color
                    if "valuesForLeftPanel" in obj:
                        obj["valuesForLeftPanel"]["color"] = new_color if new_color.startswith("#") else rgb_to_hex(new_color)
                    _rebuild_text_html(obj)
                elif obj.get("type") == "shape":
                    obj["DefaultColor"] = new_color
                applied.append(f"change_color: Changed color of '{obj.get('Name')}' to {new_color}")

            elif op_type == "change_font":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_font: Object '{target}' not found"); continue
                if "fontFamily" in op:
                    obj["fontFamily"] = op["fontFamily"]
                    obj["FontFamily"] = op["fontFamily"]
                    if "valuesForLeftPanel" in obj:
                        obj["valuesForLeftPanel"]["fontFamily"] = op["fontFamily"]
                if "fontSize" in op:
                    new_size = op["fontSize"]
                    obj["fontSize"] = new_size
                    obj["FontSize"] = new_size
                    if "valuesForLeftPanel" in obj:
                        obj["valuesForLeftPanel"]["fontSize"] = new_size
                    obj["isTextAdjustmentsNeeded"] = False
                    line_spacing = float(obj.get("lineSpacing", 1.4))
                    plain = obj.get("Text", "")
                    if not plain:
                        val = obj.get("Value", "")
                        if val:
                            decoded = unquote(val)
                            plain = re.sub(r'<[^>]+>', '', decoded).strip()
                            plain = re.sub(r'\s+', ' ', plain)
                        else:
                            plain = "Text"
                    line_h = new_size * line_spacing
                    approx_char_width = new_size * 0.55
                    box_width = obj.get("Width", 300)
                    chars_per_line = max(1, int(box_width / approx_char_width))
                    num_lines = max(1, -(-len(plain) // chars_per_line))
                    needed_height = int(num_lines * line_h + 10)
                    if needed_height > obj.get("Height", 100):
                        obj["Height"] = needed_height
                _rebuild_text_html(obj)
                applied.append(f"change_font: Changed font of '{obj.get('Name')}'")

            elif op_type == "move":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"move: Object '{target}' not found"); continue
                # Support both absolute (x/y) and relative (dx/dy) positioning
                if "dx" in op: obj["X"] = obj.get("X", 0) + op["dx"]
                if "dy" in op: obj["Y"] = obj.get("Y", 0) + op["dy"]
                if "x" in op: obj["X"] = op["x"]
                if "y" in op: obj["Y"] = op["y"]
                applied.append(f"move: Moved '{obj.get('Name')}' to ({obj['X']},{obj['Y']})")

            elif op_type == "resize":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"resize: Object '{target}' not found"); continue
                if "width" in op: obj["Width"] = op["width"]
                if "height" in op: obj["Height"] = op["height"]
                applied.append(f"resize: Resized '{obj.get('Name')}' to {obj['Width']}x{obj['Height']}")

            elif op_type == "rotate":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"rotate: Object '{target}' not found"); continue
                obj["RotateDegree"] = op.get("degree", 0)
                applied.append(f"rotate: Rotated '{obj.get('Name')}' to {op.get('degree')}deg")

            elif op_type == "remove":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"remove: Object '{target}' not found"); continue
                name = obj.get("Name")
                object_list.pop(idx)
                for j, o in enumerate(object_list):
                    o["elementIndex"] = j
                applied.append(f"remove: Removed '{name}'")

            elif op_type == "add_text":
                new_text = op.get("text", "New Text")
                font = op.get("fontFamily", "Arial")
                size = op.get("fontSize", 28)
                color = op.get("color", "#000000")
                is_bold = op.get("isBold", False)
                align = op.get("align", "left")
                encoded_html = build_text_html_value(new_text, font, size, color, align, is_bold)
                new_obj = {
                    "AllowMove": "true", "AllowResize": "true", "AllowRotate": "true",
                    "ColorSystem": "RGB", "DefaultColor": "cmyk(0% 0% 0% 0%)",
                    "Height": op.get("height", 100), "Id": str(uuid.uuid4()),
                    "IsHtml": True, "IsVisible": True,
                    "Name": op.get("name", f"Text {len(object_list)+1}"),
                    "PageNo": 0, "PdfSortOrder": len(object_list) + 1,
                    "RotateDegree": 0, "RotateX": 0, "RotateY": 0,
                    "SortOrder": len(object_list) + 1,
                    "Value": encoded_html, "modifiedHtml": encoded_html,
                    "Width": op.get("width", 300), "X": op.get("x", 50), "Y": op.get("y", 50),
                    "elementIndex": len(object_list), "locked": False, "type": "text",
                    "scaleX": 1, "scaleY": 1,
                    "isEditableForRightPanel": False, "isSelected": False,
                    "fontFamily": font, "VerticalAlign": "Middle",
                    "fontSize": size, "lineSpacing": "1.4",
                    "color": hex_to_rgb(color) if color.startswith("#") else color,
                    "isBold": is_bold, "isItalic": False, "isUnderline": False,
                    "isJustifyCenter": align == "center", "isJustifyLeft": align == "left",
                    "isJustifyRight": align == "right", "isJustify": align == "justify",
                    "isBulletList": False, "isNumberList": False,
                    "isSubScript": False, "isSupperScript": False,
                    "isTextAdjustmentsNeeded": True,
                    "valuesForLeftPanel": {
                        "fontFamily": font, "fontSize": size, "lineSpacing": "1.4",
                        "color": color if color.startswith("#") else rgb_to_hex(color),
                        "isBold": is_bold, "isItalic": False, "isUnderline": False,
                        "isJustifyCenter": align == "center", "isJustifyLeft": align == "left",
                        "isJustifyRight": align == "right", "isJustify": align == "justify",
                    },
                    "animation": {"speed": 50, "style": "", "startTime": 0, "duration": 0, "onEnter": False, "onExit": False, "distance": 50},
                    "textShadow": {"textEffect": "none", "angle": 0, "distance": 0, "shadowBlur": 0, "shadowColor": "rgb(252,252,252)", "transparency": 0, "shadowOffsetX": 0, "shadowOffsetY": 0},
                    "outLine": {"textEffect": "none", "strokeWidth": 0, "strokeColor": "#000000"},
                    "isAnimated": False,
                }
                object_list.append(new_obj)
                applied.append(f"add_text: Added '{op.get('name', 'New Text')}'")

            elif op_type == "add_shape":
                new_obj = {
                    "AllowMove": "true", "AllowResize": "true", "AllowRotate": "true",
                    "Alpha": "100", "ColorSystem": "RGB",
                    "DefaultColor": op.get("color", "rgba(255,255,255,1)"),
                    "StrokeWidth": op.get("strokeWidth", 0), "StrokeColor": op.get("strokeColor", "#000000"),
                    "Height": op.get("height", 100), "Id": str(uuid.uuid4()),
                    "IsVisible": True, "Name": op.get("name", f"Shape {len(object_list)+1}"),
                    "PageNo": 0, "PdfSortOrder": len(object_list) + 1,
                    "RotateDegree": 0, "SortOrder": len(object_list) + 1, "UseRgb": True,
                    "Width": op.get("width", 200), "X": op.get("x", 50), "Y": op.get("y", 50),
                    "type": "shape", "scaleX": 1, "scaleY": 1, "locked": False,
                    "shapeType": op.get("shapeType", "rectangle"),
                    "elementIndex": len(object_list), "isGradient": False,
                    "gradient": {"angle": 0, "colors": []},
                    "animation": {"speed": 1, "style": "", "startTime": 0, "duration": 0, "onEnter": False, "onExit": False},
                    "isAnimated": False,
                }
                object_list.append(new_obj)
                applied.append(f"add_shape: Added '{op.get('name', 'New Shape')}'")

            elif op_type == "add_image":
                new_obj = {
                    "AllowMove": "true", "AllowResize": "true", "AllowRotate": "true",
                    "Alpha": "100", "ColorSystem": "RGB",
                    "DefaultImageUrl": op.get("url", ""),
                    "originalSrc": op.get("url", ""),
                    "Height": op.get("height", 200), "Id": str(uuid.uuid4()),
                    "IsVisible": True,
                    "Name": op.get("name", f"Image {len(object_list)+1}"),
                    "PageNo": 0, "PdfSortOrder": len(object_list) + 1,
                    "RotateDegree": 0, "SortOrder": len(object_list) + 1,
                    "Width": op.get("width", 200), "X": op.get("x", 50), "Y": op.get("y", 50),
                    "type": "image", "scaleX": 1, "scaleY": 1, "locked": False,
                    "elementIndex": len(object_list),
                    "IsHFlipped": False, "IsVFlipped": False,
                    "isEditableForRightPanel": False,
                    "SvgProperty": {},
                    "opacity": 100,
                    "effects": {
                        "brightness": {"value": 50}, "contrast": {"value": 50},
                        "saturation": {"value": 50}, "blur": {"value": 0},
                        "tint": {"value": 0, "color": "#000000"}, "vignette": {"value": 0},
                        "transparency": {"value": 100}
                    },
                    "animation": {"speed": 50, "style": "", "startTime": 0, "duration": 0, "onEnter": False, "onExit": False, "distance": 50},
                    "isAnimated": False,
                }
                object_list.append(new_obj)
                applied.append(f"add_image: Added image '{op.get('name', 'New Image')}' from URL")

            elif op_type == "change_image":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_image: Object '{target}' not found"); continue
                obj["DefaultImageUrl"] = op.get("url", obj.get("DefaultImageUrl", ""))
                applied.append(f"change_image: Changed image of '{obj.get('Name')}'")

            elif op_type == "flip":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"flip: Object '{target}' not found"); continue
                direction = op.get("direction", "horizontal")
                if direction == "horizontal":
                    obj["IsHFlipped"] = not obj.get("IsHFlipped", False)
                else:
                    obj["IsVFlipped"] = not obj.get("IsVFlipped", False)
                applied.append(f"flip: Flipped '{obj.get('Name')}' {direction}")

            elif op_type == "change_opacity":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_opacity: Object '{target}' not found"); continue
                value = op.get("value", 100)
                obj.setdefault("effects", {})["transparency"] = {"value": value}
                applied.append(f"change_opacity: Set '{obj.get('Name')}' to {value}%")

            elif op_type == "change_visibility":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_visibility: Object '{target}' not found"); continue
                obj["IsVisible"] = op.get("visible", True)
                applied.append(f"change_visibility: '{obj.get('Name')}' visible={op.get('visible')}")

            elif op_type == "change_effect":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_effect: Object '{target}' not found"); continue
                obj.setdefault("effects", {})
                effect = op.get("effect", "")
                value = op.get("value", 50)
                if effect == "tint":
                    obj["effects"]["tint"] = {"value": value, "color": op.get("color", "#000")}
                else:
                    obj["effects"][effect] = {"value": value}
                applied.append(f"change_effect: {effect}={value} on '{obj.get('Name')}'")

            elif op_type == "change_svg_color":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_svg_color: Object '{target}' not found"); continue
                svg_prop = obj.get("SvgProperty")
                if svg_prop:
                    new_color = op.get("color", "#000000")
                    svg_prop["DefaultColor"] = new_color
                    if svg_prop.get("content"):
                        decoded_svg = unquote(svg_prop["content"])
                        # Replace fill attributes (skip fill="none" and fill="currentColor")
                        decoded_svg = re.sub(
                            r'fill="(?!none|currentColor)([^"]+)"',
                            f'fill="{new_color}"',
                            decoded_svg
                        )
                        # Replace stroke attributes (skip stroke="none" and stroke="currentColor")
                        decoded_svg = re.sub(
                            r'stroke="(?!none|currentColor)([^"]+)"',
                            f'stroke="{new_color}"',
                            decoded_svg
                        )
                        # Replace inline style fill: values
                        decoded_svg = re.sub(
                            r'(fill:\s*)(?!none|currentColor)([^;"}\'\n]+)',
                            f'\\g<1>{new_color}',
                            decoded_svg
                        )
                        # Replace inline style stroke: values
                        decoded_svg = re.sub(
                            r'(stroke:\s*)(?!none|currentColor)([^;"}\'\n]+)',
                            f'\\g<1>{new_color}',
                            decoded_svg
                        )
                        svg_prop["content"] = quote(decoded_svg, safe='')
                        # Refresh the colors array so the frontend UI pickers stay in sync
                        color_pattern = re.compile(
                            r'#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|rgba\([^)]+\)'
                        )
                        found_colors = list(dict.fromkeys(color_pattern.findall(decoded_svg)))
                        svg_prop["colors"] = [
                            {"original": c, "replacement": c}
                            for c in found_colors[:20]
                        ]
                applied.append(f"change_svg_color: SVG color of '{obj.get('Name')}' to {op.get('color')}")

            elif op_type == "regenerate_svg":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"regenerate_svg: Object '{target}' not found"); continue
                
                # Only SVG objects can be regenerated
                svg_prop = obj.get("SvgProperty")
                if not svg_prop:
                    errors.append(f"regenerate_svg: '{obj.get('Name')}' is not an SVG object")
                    continue
                
                prompt = op.get("prompt", f"Recreate {obj.get('Name')} with improvements")
                obj_type = obj.get("type", "icon")
                obj_width = obj.get("Width", 200)
                obj_height = obj.get("Height", 200)
                
                logger.info(f"SVG Regen: '{obj.get('Name')}' type={obj_type} size={obj_width}x{obj_height}")
                logger.info(f"SVG Regen Prompt: {prompt[:100]}...")
                
                # Generate new SVG using Vertex AI
                new_svg = await generate_svg_from_prompt(prompt, obj_type, int(obj_width), int(obj_height))
                if new_svg:
                    logger.info(f"SVG Generated: {len(new_svg)} chars")
                    svg_prop["content"] = quote(new_svg, safe='')
                    # Reset colors to preserve new SVG's original colors
                    if "DefaultColor" in svg_prop:
                        del svg_prop["DefaultColor"]
                    applied.append(f"regenerate_svg: Regenerated SVG for '{obj.get('Name')}' from prompt")
                    logger.info(f"SVG Regenerated for '{obj.get('Name')}'")
                else:
                    logger.error(f"SVG generation failed for '{obj.get('Name')}'")
                    errors.append(f"regenerate_svg: Failed to generate SVG for '{obj.get('Name')}'")

            elif op_type == "change_text_style":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_text_style: Object '{target}' not found"); continue
                for prop in ["isBold", "isItalic", "isUnderline"]:
                    if prop in op:
                        obj[prop] = op[prop]
                        if "valuesForLeftPanel" in obj:
                            obj["valuesForLeftPanel"][prop] = op[prop]
                if "isBold" in op: obj["FontWeight"] = "bold" if op["isBold"] else "normal"
                if "isItalic" in op: obj["FontStyle"] = "italic" if op["isItalic"] else "normal"
                if "isUnderline" in op: obj["TextDecoration"] = "underline" if op["isUnderline"] else "none"
                _rebuild_text_html(obj)
                applied.append(f"change_text_style: Updated style of '{obj.get('Name')}'")

            elif op_type == "change_alignment":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_alignment: Object '{target}' not found"); continue
                align = op.get("align", "left")
                obj["isJustifyLeft"] = align == "left"
                obj["isJustifyCenter"] = align == "center"
                obj["isJustifyRight"] = align == "right"
                obj["isJustify"] = align == "justify"
                obj["TextAlign"] = align
                if "valuesForLeftPanel" in obj:
                    for k in ["isJustifyLeft", "isJustifyCenter", "isJustifyRight", "isJustify"]:
                        obj["valuesForLeftPanel"][k] = obj[k]
                _rebuild_text_html(obj)
                applied.append(f"change_alignment: '{obj.get('Name')}' to {align}")

            elif op_type == "change_text_shadow":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_text_shadow: Object '{target}' not found"); continue
                shadow = obj.get("textShadow", {})
                for key in ["shadowColor", "shadowBlur", "shadowOffsetX", "shadowOffsetY"]:
                    if key in op: shadow[key] = op[key]
                shadow["textEffect"] = "shadow"
                obj["textShadow"] = shadow
                applied.append(f"change_text_shadow: Updated shadow on '{obj.get('Name')}'")

            elif op_type == "change_outline":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_outline: Object '{target}' not found"); continue
                outline = obj.get("outLine", {})
                for key in ["strokeWidth", "strokeColor"]:
                    if key in op: outline[key] = op[key]
                outline["textEffect"] = "outline"
                obj["outLine"] = outline
                applied.append(f"change_outline: Updated outline on '{obj.get('Name')}'")

            elif op_type == "duplicate":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"duplicate: Object '{target}' not found"); continue
                new_obj = copy.deepcopy(obj)
                new_obj["Id"] = str(uuid.uuid4())
                new_obj["Name"] = f"{obj.get('Name', 'Object')} Copy"
                new_obj["X"] = obj.get("X", 0) + op.get("offsetX", 20)
                new_obj["Y"] = obj.get("Y", 0) + op.get("offsetY", 20)
                new_obj["elementIndex"] = len(object_list)
                new_obj["isSelected"] = False
                object_list.append(new_obj)
                applied.append(f"duplicate: Duplicated '{obj.get('Name')}'")

            elif op_type == "reorder":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"reorder: Object '{target}' not found"); continue
                new_order = op.get("sortOrder", obj.get("SortOrder", 0))
                obj["SortOrder"] = new_order
                obj["PdfSortOrder"] = new_order
                applied.append(f"reorder: '{obj.get('Name')}' order to {new_order}")

            elif op_type == "change_line_spacing":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_line_spacing: Object '{target}' not found"); continue
                obj["lineSpacing"] = str(op.get("lineSpacing", "1.4"))
                obj["LineHeight"] = float(op.get("lineSpacing", 1.4))
                if "valuesForLeftPanel" in obj:
                    obj["valuesForLeftPanel"]["lineSpacing"] = obj["lineSpacing"]
                applied.append(f"change_line_spacing: '{obj.get('Name')}' to {op.get('lineSpacing')}")

            elif op_type == "lock":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"lock: Object '{target}' not found"); continue
                obj["locked"] = op.get("locked", True)
                applied.append(f"lock: '{obj.get('Name')}' locked={op.get('locked')}")

            elif op_type == "change_gradient":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"change_gradient: Object '{target}' not found"); continue
                obj["isGradient"] = op.get("enabled", False)
                if "angle" in op: obj.setdefault("gradient", {})["angle"] = op["angle"]
                if "colors" in op:
                    grad_colors = []
                    for ci, c in enumerate(op["colors"]):
                        grad_colors.append({
                            "id": str(ci + 1), "position": c.get("position", ci * 100),
                            "color": c.get("color", "red"), "isSelected": ci == 0,
                            "rgba": c.get("rgba", c.get("color", "rgba(255,0,0,1)"))
                        })
                    obj.setdefault("gradient", {})["colors"] = grad_colors
                applied.append(f"change_gradient: Updated gradient on '{obj.get('Name')}'")

            elif op_type == "edit_image_with_ai":
                idx, obj = find_object_by_target(object_list, target)
                if idx == -1: errors.append(f"edit_image_with_ai: Object '{target}' not found"); continue
                svg_prop = obj.get("SvgProperty")
                obj_url = obj.get("DefaultImageUrl", "")
                is_svg_obj = (svg_prop and svg_prop.get("content")) or obj_url.lower().endswith(".svg") or obj.get("ImageExtension", "").lower() == "svg"
                if is_svg_obj:
                    errors.append(f"edit_image_with_ai: '{obj.get('Name')}' is SVG — use change_svg_color instead")
                    continue
                img_url = obj.get("DefaultImageUrl", "")
                if not img_url:
                    errors.append(f"edit_image_with_ai: No image URL for '{obj.get('Name')}'")
                    continue
                image_edits_needed.append({
                    "index": idx, "object": obj,
                    "prompt": op.get("prompt", ""), "name": obj.get("Name", "")
                })
                applied.append(f"edit_image_with_ai: Queued AI edit for '{obj.get('Name')}'")

            else:
                errors.append(f"Unknown operation: {op_type}")

        except Exception as e:
            errors.append(f"Could not apply '{op_type}': {_sanitize_error(e, 'operation failed')}")

    return {"template": template, "applied": applied, "errors": errors, "image_edits_needed": image_edits_needed}


CHROMA_KEY_COLOR = (0, 255, 128)   # bright green — unlikely in real content
CHROMA_KEY_TOLERANCE = 60          # euclidean distance threshold for removal


def _has_transparency(pil_image: Image.Image) -> bool:
    """Return True if image has meaningful transparent pixels."""
    if pil_image.mode not in ("RGBA", "LA"):
        return False
    alpha = pil_image.split()[-1]
    import numpy as np
    return bool(np.array(alpha).min() < 200)


def _apply_chroma_key_bg(pil_image: Image.Image) -> tuple[Image.Image, bool]:
    """
    Composite transparent image onto a chroma-key background colour.
    Returns (composited_rgb_image, had_transparency).
    """
    had = _has_transparency(pil_image)
    if not had:
        return pil_image.convert("RGB"), False
    bg = Image.new("RGBA", pil_image.size, CHROMA_KEY_COLOR + (255,))
    bg.paste(pil_image.convert("RGBA"), mask=pil_image.convert("RGBA").split()[3])
    return bg.convert("RGB"), True


def _remove_chroma_key(pil_image: Image.Image) -> Image.Image:
    """
    Remove chroma-key background from a Gemini-returned RGB image.
    Pixels within CHROMA_KEY_TOLERANCE of CHROMA_KEY_COLOR become transparent.
    Then erodes alpha by 1px to eliminate green fringe/spill on edges.
    """
    import numpy as np
    from PIL import ImageFilter

    data = np.array(pil_image.convert("RGB")).astype(np.float32)
    cr, cg, cb = CHROMA_KEY_COLOR
    dist = np.sqrt(
        (data[..., 0] - cr) ** 2 +
        (data[..., 1] - cg) ** 2 +
        (data[..., 2] - cb) ** 2
    )
    alpha = np.where(dist < CHROMA_KEY_TOLERANCE, 0, 255).astype(np.uint8)
    rgba = np.concatenate([data.astype(np.uint8), alpha[..., np.newaxis]], axis=2)
    result = Image.fromarray(rgba, "RGBA")

    # Erode alpha by 1px: MinFilter shrinks opaque regions, removing green-tinted edge pixels
    alpha_ch = result.split()[3].filter(ImageFilter.MinFilter(3))
    result.putalpha(alpha_ch)
    return result


def _remove_corner_bg(pil_image: Image.Image, tolerance: int = 30) -> Image.Image:
    """
    Sample all 4 corners to estimate background colour, then make similar pixels transparent.
    Used when original image had no transparency (Option B fallback).
    """
    import numpy as np
    rgb = np.array(pil_image.convert("RGB")).astype(np.float32)
    h, w = rgb.shape[:2]

    corner_pixels = [
        rgb[0, 0], rgb[0, w - 1],
        rgb[h - 1, 0], rgb[h - 1, w - 1],
    ]
    bg = np.median(corner_pixels, axis=0)  # median of 4 corners

    dist = np.sqrt(np.sum((rgb - bg) ** 2, axis=2))
    rgba = np.concatenate([rgb.astype(np.uint8), np.full((h, w, 1), 255, dtype=np.uint8)], axis=2)
    rgba[dist < tolerance, 3] = 0
    return Image.fromarray(rgba, "RGBA")


async def process_ai_image_edit(image_url: str, edit_prompt: str) -> str:
    """Download an image, edit it with Gemini image editing, upload to CDN. Returns new URL."""
    from api_client import gemini_edit_image
    from gemini_assembler import upload_to_cdn

    if image_url.lower().endswith(".svg") or "/svg" in image_url.lower():
        raise Exception("SVG images cannot be edited with AI. Use change_svg_color instead.")

    # Download image
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(image_url)
        resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    if "svg" in content_type.lower():
        raise Exception("SVG content cannot be raster-edited.")

    logger.info("AI image edit [1/4] opening image...")
    pil_image = Image.open(io.BytesIO(resp.content))
    logger.info(f"AI image edit [2/4] resizing {pil_image.width}x{pil_image.height}...")
    pil_image = resize_large_image(pil_image, max_pixels=2_000_000)

    logger.info(f"AI image edit [3/4] preparing {pil_image.width}x{pil_image.height}...")
    composited, had_transparency = _apply_chroma_key_bg(pil_image)
    buf = io.BytesIO()
    composited.save(buf, format="PNG")
    img_bytes = buf.getvalue()

    wrapped_prompt = (
        f"{edit_prompt}\n\n"
        "IMPORTANT RULES:\n"
        "1. Edit ONLY the specific element described above — do NOT change, move, or alter any other part of the image\n"
        "2. Keep all other elements exactly as they are in the original image\n"
        "3. Do NOT add any background, backdrop, or solid color fill behind anything\n"
        "4. Do NOT add black, white, or any color as a background — preserve the existing background as-is\n"
        "5. If removing something, replace it with the natural surrounding background from the original image (content-aware fill), not a solid color"
    )

    logger.info(f"AI image edit [4/4] sending {len(img_bytes)//1024}KB to model — prompt: {edit_prompt[:60]}")
    image_data = await gemini_edit_image(img_bytes, wrapped_prompt, timeout=60)
    logger.info(f"AI image edit complete — result: {len(image_data)//1024 if image_data else 0}KB")

    if not image_data:
        raise Exception("Image edit failed. Please try again.")

    # ── Post-process: restore transparency ────────────────────────────────────
    result_img = Image.open(io.BytesIO(image_data))

    if had_transparency:
        # Option A: remove chroma-key colour Gemini preserved (or re-added)
        logger.info("AI Image Edit: removing chroma-key background (had transparency)")
        result_img = _remove_chroma_key(result_img)
    else:
        # Option B: corner-sampled removal for images that had a solid/white bg added
        corners = [result_img.getpixel((0, 0)), result_img.getpixel((result_img.width - 1, 0)),
                   result_img.getpixel((0, result_img.height - 1)), result_img.getpixel((result_img.width - 1, result_img.height - 1))]
        # Only apply if all corners are very similar (uniform background was added)
        import numpy as np
        corner_arr = np.array([c[:3] for c in corners], dtype=np.float32)
        if np.std(corner_arr) < 20:
            logger.info("AI Image Edit: removing uniform corner background (Option B)")
            result_img = _remove_corner_bg(result_img)

    out_buf = io.BytesIO()
    result_img.save(out_buf, format="PNG")
    final_bytes = out_buf.getvalue()

    filename = f"ai_edited_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}.png"
    cdn_url = upload_to_cdn(final_bytes, filename, "image/png")

    logger.info(f"AI Image Edit complete: {cdn_url}")
    return cdn_url


# ══════════════════════════════════════════════════════════════════════════════
# POST /api/edit-template — AI-powered template editing
# ══════════════════════════════════════════════════════════════════════════════

@app.post("/api/edit-template")
async def edit_template(request: Request):
    """
    AI-Powered JSON Template Editor using Vertex AI.

    Request body: {"template_json": {...}, "prompt": "..."}
    Returns: {"template_json": {...}, "operations_applied": [...], "errors": [...]}
    """
    try:
        body = await request.json()
        template_json = body.get("template_json")
        prompt = body.get("prompt", "")

        if not template_json or not prompt:
            raise HTTPException(status_code=400, detail="Both 'template_json' and 'prompt' are required")

        if "pages" not in template_json or not template_json["pages"]:
            raise HTTPException(status_code=400, detail="Invalid template: missing 'pages'")
        if "objectList" not in template_json["pages"][0]:
            raise HTTPException(status_code=400, detail="Invalid template: missing 'objectList'")

        # Step 1: Compact summary
        summary = generate_template_summary(template_json)

        # Step 2: Build AI prompt
        ai_prompt = TEMPLATE_EDITOR_SYSTEM_PROMPT.format(
            summary=summary,
            operations=TEMPLATE_EDITOR_OPERATIONS_SCHEMA,
            user_prompt=prompt
        )

        # Step 3: Call Vertex AI directly
        from api_client import vertex_ai_generate
        ai_response_text = (await vertex_ai_generate(ai_prompt, model="gemini-2.5-flash", timeout=30)).strip()

        logger.info(f"[edit-template] AI raw response: {ai_response_text[:500]}")

        # Step 4: Parse operations
        cleaned = ai_response_text
        if cleaned.startswith("```"):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)

        try:
            operations = json.loads(cleaned)
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="AI returned invalid operations. Try rephrasing.")

        if not isinstance(operations, list):
            operations = [operations]

        logger.info(f"[edit-template] Parsed {len(operations)} operation(s): {operations}")

        # Step 5: Apply operations
        result = await apply_template_operations(template_json, operations)
        logger.info(f"[edit-template] Applied: {result['applied']}")
        logger.info(f"[edit-template] Errors: {result['errors']}")

        # Step 6: Handle AI image edits
        image_edit_results = []
        for edit in result["image_edits_needed"]:
            try:
                obj = edit["object"]
                current_url = obj.get("DefaultImageUrl", "")
                if not current_url:
                    result["errors"].append(f"No image URL for '{edit['name']}'")
                    continue
                new_url = await process_ai_image_edit(current_url, edit["prompt"])
                obj["DefaultImageUrl"] = new_url
                image_edit_results.append({"name": edit["name"], "old_url": current_url, "new_url": new_url})
            except Exception as e:
                result["errors"].append(f"Image edit failed for '{edit['name']}': {_sanitize_error(e, 'processing failed')}")

        # Generate AI comment using Vertex AI
        edit_comment = f"Applied {len(result['applied'])} edit(s) successfully."
        try:
            comment_prompt = (
                f"You are a design assistant. A user edited a template with: '{prompt}'. "
                f"Operations: {', '.join(result['applied'][:5])}. "
                f"Give a brief 1-sentence confirmation. Be concise."
            )

            edit_comment = (await vertex_ai_generate(comment_prompt, model="gemini-2.5-flash", timeout=15)).strip()
        except Exception:
            pass

        return JSONResponse(content={
            "template_json": result["template"],
            "operations_applied": result["applied"],
            "errors": result["errors"],
            "image_edits": image_edit_results,
            "summary": summary,
            "text": edit_comment,
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template edit error: {e}")
        raise HTTPException(status_code=500, detail=_sanitize_error(e, "Failed to apply edits. Please try again."))


# ══════════════════════════════════════════════════════════════════════════════
# Static mounts (MUST be after all route definitions to avoid shadowing)
# ══════════════════════════════════════════════════════════════════════════════

if (THIS_DIR / "visual-engine").exists():
    app.mount(
        "/visual-engine",
        StaticFiles(directory=str(THIS_DIR / "visual-engine")),
        name="visual-engine",
    )


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    print(f"\n  Design Automation Studio Server")
    print(f"  http://localhost:8080\n")
    uvicorn.run(app, host="0.0.0.0", port=8080)
