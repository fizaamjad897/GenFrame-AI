"""
qms_dimensions.py — Per-dimension layout profiles for QMS banner recomposition.

Every QMS dimension gets a profile that is injected into the main recompose prompt
and the fallback layout-planner prompt via placeholders. Nothing is hardcoded in the
prompt templates — all orientation-specific language comes from here.

Profile keys
────────────
label               Human-readable format name (for logging).
canvas_description  Sentence describing the canvas shape/format, injected where
                    "ultra-wide horizontal banner (8:1)" was hardcoded.
ratio_str           Numeric ratio string, e.g. "3:1", "1:2". Injected in dimension
                    rule line.
orientation         One of: landscape_extreme | landscape_wide | landscape_moderate |
                    portrait_tall | portrait_moderate
layout_direction    Primary reading direction: "left-to-right" | "top-to-bottom"
arrangement_order   Ordered list of component types describing placement priority.
element_max_height  Max element height as fraction of canvas height (0.0–1.0).
                    Used to generate "Primary text max height ~Xpx" guidance.
element_guidance    Plain-English scaling/sizing note injected into Rule 4 (SCALING).
fill_direction      How to extend background: "horizontally" | "vertically" |
                    "horizontally and vertically"
fill_description    One sentence injected into Rule 2 (NO DUPLICATION) describing
                    exactly how to fill empty space.
layout_rules        List of dimension-specific layout rules injected as numbered
                    bullets in the layout-planner prompt.
dimension_warnings  List of must-not-do items specific to this format, injected as
                    a WARNING block in the recompose prompt.
"""

from __future__ import annotations
from typing import TypedDict, List


class DimProfile(TypedDict):
    label: str
    canvas_description: str
    ratio_str: str
    orientation: str
    layout_direction: str
    arrangement_order: List[str]
    element_max_height: float
    element_guidance: str
    fill_direction: str
    fill_description: str
    layout_rules: List[str]
    dimension_warnings: List[str]


# ── Profile definitions ────────────────────────────────────────────────────────

QMS_PROFILES: dict[tuple[int, int], DimProfile] = {

    # ── 2640 × 288 ── AR 9.17:1  ULTRA-EXTREME THIN STRIP ────────────────────
    (2640, 288): DimProfile(
        label="Ultra-extreme thin strip (2640×288)",
        canvas_description=(
            "an ultra-extreme thin, ultra-wide horizontal strip banner (2640×288 px, ~9.2:1 ratio). "
            "This canvas is 9.2 times WIDER than it is tall. "
            "ALL elements MUST be spread across the FULL 2640 px width — left edge to right edge. "
            "Nothing may be clustered on one side leaving empty space on the other."
        ),
        ratio_str="9.2:1",
        orientation="landscape_extreme",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "CRITICAL — FULL WIDTH USAGE: The canvas is 2640 px wide. You MUST use ALL of it. "
            "The output image MUST span from x=0 to x=2640 continuously — no white zones, no grey borders, no empty bars on either side. "
            "ZONE ASSIGNMENT (MANDATORY): Divide the 2640 px canvas into four horizontal zones: "
            "Zone A (x: 0–500) — logo and/or person anchor; "
            "Zone B (x: 500–1200) — primary headline text; "
            "Zone C (x: 1200–2100) — subheading/body text; "
            "Zone D (x: 2100–2640) — CTA, secondary element, or extended background. "
            "EVERY zone MUST contain visible content — leaving any zone entirely empty is a FAILURE. "
            "FOR ADVERTISING IMAGES: Logo top-left (Zone A) → headline text (Zone B) → subheading text (Zone C) → CTA or person (Zone D), or mirrored layout. "
            "Scale all text to be legible at 288 px height — text must be large enough to read. "
            "DO NOT wrap text into multiple narrow lines. Keep each text element on ONE wide horizontal line, scaled to fill height. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically and extend the background as a seamless panorama across all 2640 px. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Never generate, render, or composite the person into a new scene. Paste the EXACT provided crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill all remaining horizontal space with a seamless background extension. "
            "The background MUST cover x: 0 to x: 2640 px continuously — no white/empty zones. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "CRITICAL — USE THE FULL 2640 PX WIDTH: Elements must span from near x=0 to near x=2640. Leaving more than 400 px of empty space on either side is a layout failure.",
            "CRITICAL — NO LEFT-CLUSTERING: Do NOT place all elements within the left 600 px. Distribute across the entire canvas.",
            "CRITICAL — NO VERTICAL TEXT WRAPPING: Do NOT wrap text into a narrow vertical column. Each text block should be wide and horizontally laid out.",
            "LAYOUT FOR ADVERTISING IMAGES: Place logo at far left → headline text in centre-left zone → subheading in centre-right zone → person or CTA at far right. Use x-zones: [0–500], [500–1200], [1200–2000], [2000–2640].",
            "LAYOUT FOR GENERIC IMAGES: Fill the entire 2640×288 with a seamless panoramic scene.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–288 px (hard limit).",
            "Minimum 12 px padding between elements and canvas edges.",
            "NO vertical stacking — single horizontal row only.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: The person's face MUST be identical to the provided photo crop — same skin tone, same facial features, same expression. ANY change in face appearance is a failure.",
            "CRITICAL — NO POSE CHANGE: The person's body pose, gesture, and arm/hand position MUST be identical to the reference crop.",
            "CRITICAL — PASTE DO NOT BLEND: The human photo layer must be pasted as a discrete image crop. Do NOT blend, redraw, or composite the person into the background.",
            "CRITICAL — FILL THE FULL WIDTH: The output MUST use all 2640 px. Do NOT leave a large empty white or background-only zone on either side of the canvas. An output with grey bars on the left and right is a FAILURE.",
            "CRITICAL — NO LEFT-SIDE CLUSTERING: All elements placed only in the left 30% of the canvas is a FAILURE. Spread elements across the full width.",
            "CRITICAL — NO VERTICAL TEXT COLUMNS: Do NOT wrap text into tall narrow columns. Text must be laid out horizontally in wide blocks.",
            "CRITICAL — NO EMPTY ZONES: The canvas is divided into four zones (0–500, 500–1200, 1200–2100, 2100–2640). Every zone MUST contain visible content. An output where any zone is empty is a layout failure.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Visually scan from x=0 to x=2640 and confirm: (1) No zone is empty. (2) Elements are spread across all 2640 px. (3) No grey/white bars exist on either side. If any check fails, your layout is wrong — redo it.",
            "DO NOT stretch primary subjects to fill the 9.2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements that do not exist in the source image.",
            "DO NOT stack elements vertically; the 288 px height demands a single horizontal row.",
            "Output must be exactly 2640×288 px — not square, not portrait, not any other size.",
        ],
    ),

    # ── 1824 × 432 ── AR 4.22:1  SUPER WIDE BILLBOARD ────────────────────────
    (1824, 432): DimProfile(
        label="Super wide billboard (1824×432)",
        canvas_description=(
            "a super-wide horizontal billboard banner (1824×432 px, ~4.2:1 ratio). "
            "Generous width requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="4.2:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1824×432 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilise the large 4.2:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "(headlines, body, CTA) intelligently across the remaining clear space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1824x432 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side or anchor point, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–432 px.",
            "Minimum 22 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the large 4.2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the centre — spread organically across the full 1824 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1824×432 px — not square, not portrait.",
        ],
    ),

    # ── 1728 × 432 ── AR 4.0:1  WIDE BILLBOARD ───────────────────────────────
    (1728, 432): DimProfile(
        label="Wide billboard (1728×432)",
        canvas_description=(
            "a wide horizontal billboard banner (1728×432 px, 4:1 ratio). "
            "Classic landscape billboard format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="4:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1728×432 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 4:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "(headlines, body, CTA) intelligently across the remaining space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1728x432 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side or anchor point, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–432 px.",
            "Minimum 22 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 4:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the centre — spread organically across the full 1728 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1728×432 px — not square, not portrait.",
        ],
    ),

    # ── 1440 × 360 ── AR 4.0:1  WIDE BILLBOARD ───────────────────────────────
    (1440, 360): DimProfile(
        label="Wide billboard (1440×360)",
        canvas_description=(
            "a wide horizontal billboard banner (1440×360 px, 4:1 ratio). "
            "Classic 4:1 billboard format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="4:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1440×360 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — do NOT redraw, regenerate, or envision it; simply drop it in at the correct position. "
            "Distribute text and logo elements intelligently across the remaining space. Do NOT cluster elements in the middle — spread across the full 1440 px width. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Never generate, render, or composite the person into a new scene. Paste the EXACT provided crop, unchanged, against the SAME plain/white background it already has."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1440x360 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Place the photo/hero as the visual anchor on one side, with text and logos in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–360 px.",
            "Minimum 20 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: The person's face in the output MUST be identical to the provided photo crop — same skin tone, same facial features, same expression, same facial structure. ANY deviation in face appearance is a failure.",
            "CRITICAL — NO POSE CHANGE: The person's body pose, gesture, and arm/hand position MUST be identical to the reference crop. Do NOT change standing to seated, do NOT alter gestures.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add a desk, table, chair, or any object not visible in the reference photo crop. If the person appears against a plain background, keep it plain.",
            "CRITICAL — PASTE DO NOT BLEND: The human photo layer must be pasted as a discrete image crop. Do NOT blend, redraw, or composite the person into the background. Treat the person exactly like a logo — drop it in, do not regenerate it.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: If the person's reference crop shows them against a plain/white/clean background, that plain background MUST stay plain in the output. You are FORBIDDEN from drawing an office, room, studio, desk scene, or any environmental context around the person. Plain in = plain out.",
            "CRITICAL — STANDING PERSON STAYS STANDING: If the reference shows a standing person, they MUST be standing in the output. Rendering a seated or differently-posed version is a failure.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Before finalising, confirm: (1) The person's face is pixel-identical to the reference crop. (2) No desk, chair, table, or furniture was added. (3) The person's pose has not changed. If any check fails, your output is wrong — restart.",
            "DO NOT stretch primary subjects to fill the 4:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the centre — spread organically across the full 1440 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1440×360 px — not square, not portrait.",
        ],
    ),

    # ── 1120 × 320 ── AR 3.5:1  WIDE STRIP BILLBOARD ─────────────────────────
    (1120, 320): DimProfile(
        label="Wide strip billboard (1120×320)",
        canvas_description=(
            "a wide horizontal strip billboard banner (1120×320 px, ~3.5:1 ratio). "
            "Wide format with moderate vertical space requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3.5:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1120×320 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilise the 3.5:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1120x320 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–320 px.",
            "Minimum 16 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 3.5:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the horizontal space organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1120×320 px — not square, not portrait.",
        ],
    ),

    # ── 760 × 240 ── AR 3.17:1  WIDE STRIP ───────────────────────────────────
    # ── 760 × 240 ── AR 3.2:1  WIDE STRIP ────────────────────────────────────
    (760, 240): DimProfile(
        label="Wide strip (760×240)",
        canvas_description=(
            "a wide horizontal strip banner (760×240 px, ~3.2:1 ratio). "
            "Compact wide format with limited vertical space, requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3.2:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 760×240 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 3.2:1 width by positioning the photo/hero as a visual anchor and distributing text elements in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "DONOT CHANGE OR REGENERATE THE GIVEN COMPONENETS",
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 760x240 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–240 px.",
            "Minimum 12 px padding between distinct advertising elements and canvas edges.",
            "NO vertical stacking — horizontal distribution only.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: The person's face in the output MUST be identical to the provided photo crop — same skin tone, same facial features, same expression, same facial structure. ANY deviation in face appearance is a failure.",
            "CRITICAL — NO POSE CHANGE: The person's body pose, gesture, and arm/hand position MUST be identical to the reference crop. Do NOT change standing to seated, do NOT alter gestures.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add a desk, table, chair, or any object not visible in the reference photo crop. If the person appears against a plain background, keep it plain.",
            "CRITICAL — PASTE DO NOT BLEND: The human photo layer must be pasted as a discrete image crop. Do NOT blend, redraw, or composite the person into the background. Treat the person exactly like a logo — drop it in, do not regenerate it.",
            "DO NOT stretch primary subjects to fill the 3.2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the limited 240 px height for a single horizontal row.",
            "DO NOT cluster content in the center — spread organically across the 760 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 760×240 px — not square, not portrait.",
        ],
    ),

    # ── 1472 × 480 ── AR 3.07:1  WIDE BILLBOARD ──────────────────────────────
    (1472, 480): DimProfile(
        label="Wide billboard (1472×480)",
        canvas_description=(
            "a wide horizontal billboard banner (1472×480 px, ~3.1:1 ratio). "
            "Classic outdoor billboard format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3.1:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1472×480 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 3.1:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1472x480 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–480 px.",
            "Minimum 20 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 3.1:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the center — spread organically across the 1472 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1472×480 px — not square, not portrait.",
        ],
    ),

    # ── 1296 × 432 ── AR 3.0:1  WIDE BILLBOARD ───────────────────────────────
    (1296, 432): DimProfile(
        label="Wide billboard (1296×432)",
        canvas_description=(
            "a wide horizontal billboard banner (1296×432 px, 3:1 ratio). "
            "Classic 3:1 billboard format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1296×432 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilise the 3:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1296x432 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–432 px.",
            "Minimum 20 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the centre — spread organically across the full 1296 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1296×432 px — not square, not portrait.",
        ],
    ),

    # ── 1200 × 400 ── AR 3.0:1  WIDE BILLBOARD ───────────────────────────────
    (1200, 400): DimProfile(
        label="Wide billboard (1200×400)",
        canvas_description=(
            "a wide horizontal billboard banner (1200×400 px, 3:1 ratio). "
            "Classic 3:1 format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1200×400 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 3:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1200x400 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–400 px.",
            "Minimum 20 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the center — spread organically across the 1200 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1200×400 px — not square, not portrait.",
        ],
    ),

    # ── 1188 × 396 ── AR 3.0:1  WIDE BILLBOARD ───────────────────────────────
    (1188, 396): DimProfile(
        label="Wide billboard (1188×396)",
        canvas_description=(
            "a wide horizontal billboard banner (1188×396 px, 3:1 ratio). "
            "Classic 3:1 billboard format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1188×396 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 3:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1188x396 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–396 px.",
            "Minimum 20 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the centre — spread organically across the full 1188 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1188×396 px — not square, not portrait.",
        ],
    ),

    # ── 1184 × 384 ── AR 3.08:1  WIDE BILLBOARD ──────────────────────────────
    (1184, 384): DimProfile(
        label="Wide billboard (1184×384)",
        canvas_description=(
            "a wide horizontal billboard banner (1184×384 px, ~3.1:1 ratio). "
            "Classic outdoor billboard format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3.1:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1184×384 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — do NOT redraw, regenerate, or envision it; simply drop it in at the correct position. "
            "Distribute text and logo elements intelligently in the adjacent or opposing clear space. Do NOT cluster elements in the middle. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Never generate, render, or composite the person into a new scene. Paste the EXACT provided crop, unchanged, against the SAME plain/white background it already has."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1184x384 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–384 px.",
            "Minimum 18 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: The person's face in the output MUST be identical to the provided photo crop — same skin tone, same facial features, same expression, same facial structure. ANY deviation in face appearance is a failure.",
            "CRITICAL — NO POSE CHANGE: The person's body pose, gesture, and arm/hand position MUST be identical to the reference crop. Do NOT change standing to seated, do NOT alter gestures.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add a desk, table, chair, or any object not visible in the reference photo crop. If the person appears against a plain background, keep it plain.",
            "CRITICAL — PASTE DO NOT BLEND: The human photo layer must be pasted as a discrete image crop. Do NOT blend, redraw, or composite the person into the background. Treat the person exactly like a logo — drop it in, do not regenerate it.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: If the person's reference crop shows them against a plain/white/clean background, that plain background MUST stay plain in the output. You are FORBIDDEN from drawing an office, room, studio, desk scene, or any environmental context around the person. Plain in = plain out.",
            "CRITICAL — STANDING PERSON STAYS STANDING: If the reference shows a standing person, they MUST be standing in the output. Rendering a seated or differently-posed version is a failure.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Before finalising, confirm: (1) The person's face is pixel-identical to the reference crop. (2) No desk, chair, table, or furniture was added. (3) The person's pose has not changed. If any check fails, your output is wrong — restart.",
            "DO NOT stretch primary subjects to fill the 3.1:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the center — spread organically across the 1184 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1184×384 px — not square, not portrait.",
        ],
    ),

    # ── 1440 × 480 ── AR 3.00:1  WIDE BILLBOARD ───────────────────────────────
    (1440, 480): DimProfile(
        label="Wide billboard (1440×480)",
        canvas_description=(
            "a wide horizontal billboard banner (1440×480 px, 3:1 ratio). "
            "Wide format with strong horizontal presence and enough height for clear, readable layout."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1440×480 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 3:1 width by placing the photo/hero as a strong anchor and distributing text, logos and CTA across the remaining horizontal space. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Never generate, render, or composite the person into a new scene. Paste the EXACT provided crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1440x480 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–480 px.",
            "Minimum 20 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "DONOT CHANGE OR REGENERATE THE GIVEN COMPONENETS",
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in a small central zone — spread organically across the full 1440 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1440×480 px — not square, not portrait.",
        ],
    ),

    # ── 1152 × 384 ── AR 3.00:1  WIDE BILLBOARD ───────────────────────────────
    (1152, 384): DimProfile(
        label="Wide billboard (1152×384)",
        canvas_description=(
            "a wide horizontal billboard banner (1152×384 px, 3:1 ratio). "
            "Balanced wide format with a classic horizontal storytelling layout."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1152×384 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 3:1 width by placing the photo/hero in an anchor zone and distributing text and logos in the remaining horizontal space. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1152x384 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–384 px.",
            "Minimum 18 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in a small central zone — spread organically across the full 1152 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1152×384 px — not square, not portrait.",
        ],
    ),

    # ── 945 × 315 ── AR 3.00:1  WIDE STRIP BILLBOARD ──────────────────────────
    (945, 315): DimProfile(
        label="Wide strip billboard (945×315)",
        canvas_description=(
            "a wide horizontal banner (945×315 px, 3:1 ratio). "
            "Compact wide format with limited height requiring a clean horizontal visual flow."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 945×315 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 3:1 width by placing the hero/photo as a compact anchor and distributing text and logos along the remaining width. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 945x315 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual on one side, with text and logos in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–315 px.",
            "Minimum 16 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the limited 315 px height for a single horizontal flow.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 945×315 px — not square, not portrait.",
        ],
    ),

    # ── 864 × 288 ── AR 3.00:1  WIDE STRIP ───────────────────────────────────
    (864, 288): DimProfile(
        label="Wide strip (864×288)",
        canvas_description=(
            "a wide horizontal strip banner (864×288 px, 3:1 ratio). "
            "Compact wide format with very limited vertical space requiring a continuous horizontal layout."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 864×288 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 3:1 width by positioning the hero/photo as a compact anchor and distributing text and logo elements in the horizontal clear space. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 864x288 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width in a single horizontal row. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–288 px (hard limit).",
            "Minimum 12 px padding between distinct advertising elements and canvas edges.",
            "NO vertical stacking — horizontal distribution only.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the limited 288 px height for a single horizontal row.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 864×288 px — not square, not portrait.",
        ],
    ),

    # ── 648 × 216 ── AR 3.00:1  WIDE STRIP ───────────────────────────────────
    (648, 216): DimProfile(
        label="Wide strip (648×216)",
        canvas_description=(
            "a wide horizontal strip banner (648×216 px, 3:1 ratio). "
            "Very compact wide format with extremely limited vertical space requiring a clean, continuous horizontal layout."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 648×216 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 3:1 width by positioning the hero/photo as a compact anchor and distributing text and logo elements across the remaining horizontal space. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 648x216 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width in a single horizontal row. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–216 px (hard limit).",
            "Minimum 12 px padding between distinct advertising elements and canvas edges.",
            "NO vertical stacking — horizontal distribution only.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the limited 216 px height for a single horizontal row.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 648×216 px — not square, not portrait.",
        ],
    ),

    # ── 1152 × 576 ── AR 2.00:1  WIDE BILLBOARD ──────────────────────────────
    (1152, 576): DimProfile(
        label="Wide billboard (1152×576)",
        canvas_description=(
            "a wide horizontal billboard banner (1152×576 px, 2:1 ratio). "
            "Balanced wide format with solid vertical room for legible text and photographic detail."
        ),
        ratio_str="2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.90,
        element_guidance=(
            "Fill the 1152×576 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically within the frame. "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing photo/hero in a strong anchor zone and distributing text and logos across the remaining canvas. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1152x576 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–576 px.",
            "Minimum 20 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in a small central zone — spread organically across the full 1152 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1152×576 px — not square, not portrait.",
        ],
    ),

    # ── 768 × 384 ── AR 2.00:1  WIDE BANNER ────────────────────────────────
    (768, 384): DimProfile(
        label="Wide banner (768×384)",
        canvas_description=(
            "a wide horizontal banner (768×384 px, 2:1 ratio). "
            "Moderate wide format with balanced height for clear visuals and text."
        ),
        ratio_str="2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.90,
        element_guidance=(
            "Fill the 768×384 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically within the frame. "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing the photo/hero in a strong anchor zone and distributing text and logo elements across the remaining width. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 768x384 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–384 px.",
            "Minimum 16 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in a small central zone — spread organically across the full 768 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 768×384 px — not square, not portrait.",
        ],
    ),

    # ── 720 × 360 ── AR 2.00:1  WIDE BANNER ────────────────────────────────
    (720, 360): DimProfile(
        label="Wide banner (720×360)",
        canvas_description=(
            "a wide horizontal banner (720×360 px, 2:1 ratio). "
            "Balanced wide format with compact height and clear horizontal structure."
        ),
        ratio_str="2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.90,
        element_guidance=(
            "Fill the 720×360 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically within the frame. "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing photo/hero on one side and distributing text and logo elements across the remaining horizontal space. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 720x360 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–360 px.",
            "Minimum 16 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in a small central zone — spread organically across the full 720 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 720×360 px — not square, not portrait.",
        ],
    ),

    # ── 576 × 288 ── AR 2.00:1  WIDE STRIP BANNER ───────────────────────────
    (576, 288): DimProfile(
        label="Wide strip banner (576×288)",
        canvas_description=(
            "a wide horizontal strip banner (576×288 px, 2:1 ratio). "
            "Compact wide format with limited height requiring a clean, uninterrupted horizontal flow."
        ),
        ratio_str="2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.90,
        element_guidance=(
            "Fill the 576×288 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically within the frame. "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing the hero/photo as a compact anchor and distributing text and logo elements across the remaining horizontal space. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 576x288 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–288 px (hard limit).",
            "Minimum 12 px padding between distinct advertising elements and canvas edges.",
            "NO vertical stacking — horizontal distribution only.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects to fill the 2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the limited 288 px height for a single horizontal row.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 576×288 px — not square, not portrait.",
        ],
    ),

    # ── 576 × 1152 ── AR 1:2  PORTRAIT TALL ─────────────────────────────────
    (576, 1152): DimProfile(
        label="Portrait tall (576×1152)",
        canvas_description=(
            "a tall portrait banner (576×1152 px, 1:2 ratio). "
            "Vertical portrait format requiring top-to-bottom stacking and strong center alignment."
        ),
        ratio_str="1:2",
        orientation="portrait_tall",
        layout_direction="top-to-bottom",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 576×1152 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "Scale all components to fit within 576 px width. Stack elements vertically top-to-bottom. "
            "FOR ADVERTISING IMAGES: Place the hero/photo in the central vertical zone, with headlines, body text, and CTA above or below. "
            "FOR GENERIC IMAGES: Place the main subject/scene naturally in a vertical composition, no invented text or logos. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "For non-advertising images (no logo, headline, or CTA detected), place only the detected visual components: background, scene, subject, or photo.",
            "TOP-TO-BOTTOM: logo/headline → photo → body text → CTA → fine print.",
            "ALL elements must remain within x: 0–576 px.",
            "20 px vertical padding between stacked elements.",
            "Center elements horizontally: x = (576 - element_width) / 2.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "DO NOT place elements side by side.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "Output must be exactly 576×1152 px — NOT landscape.",
        ],
    ),

    # ── 704 × 1408 ── AR 1:2  PORTRAIT TALL ─────────────────────────────────
    (704, 1408): DimProfile(
        label="Portrait tall (704×1408)",
        canvas_description=(
            "a tall portrait banner (704×1408 px, 1:2 ratio). "
            "Vertical portrait format with strong top-to-bottom composition and generous vertical room."
        ),
        ratio_str="1:2",
        orientation="portrait_tall",
        layout_direction="top-to-bottom",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 704×1408 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "Scale all components to fit within 704 px width. Stack elements vertically top-to-bottom. "
            "FOR ADVERTISING IMAGES: Place the hero/photo in the central vertical zone, with headlines, body text, and CTA arranged above or below. "
            "FOR GENERIC IMAGES: Place the main subject/scene naturally in a vertical composition, no invented text or logos. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background or scene environment extension. "
            "Maintain perspective, lighting, and continuous flow. Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "For non-advertising images (no logo, headline, or CTA detected), place only the detected visual components: background, scene, subject, or photo.",
            "TOP-TO-BOTTOM: logo/headline → photo → body text → CTA → fine print.",
            "ALL elements must remain within x: 0–704 px.",
            "20 px vertical padding between stacked elements.",
            "Center elements horizontally: x = (704 - element_width) / 2.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "DO NOT place elements side by side.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "Output must be exactly 704×1408 px — NOT landscape.",
        ],
    ),

    # ═══════════════════════════════════════════════════════════════════════════
    # NEW DIMENSIONS — BATCH 2
    # ═══════════════════════════════════════════════════════════════════════════

    # ── LANDSCAPE WIDE (AR 2.5:1 – 5:1) ──────────────────────────────────────

    # ── 4530 × 990 ── AR 4.58:1  SUPER WIDE BILLBOARD ───────────────────────
    (4530, 990): DimProfile(
        label="Super wide billboard (4530×990)",
        canvas_description=(
            "a super-wide horizontal billboard banner (4530×990 px, ~4.6:1 ratio). "
            "Extremely wide format requiring full-width element distribution from edge to edge."
        ),
        ratio_str="4.6:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 4530×990 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — do NOT redraw, regenerate, or envision it; simply drop it in at the correct position. "
            "Distribute elements across the full 4530 px: logo far-left zone → headline centre-left → subheading centre-right → person or CTA far-right. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Never generate, render, or composite the person into a new scene. Paste the EXACT provided crop, unchanged, against the SAME plain background it already has. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background as a seamless panorama."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Distribute elements across the full 4530 px — no clustering on one side.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–990 px.",
            "Minimum 24 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "CRITICAL — FACE INTEGRITY: The person's face MUST be identical to the provided photo crop — same skin tone, same facial features, same expression. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: The person's body pose, gesture, and arm/hand position MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add a desk, table, chair, or any object not visible in the reference photo crop.",
            "CRITICAL — PASTE DO NOT BLEND: The human photo layer must be pasted as a discrete image crop. Do NOT blend, redraw, or composite the person into the background.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: If the person's reference crop shows them against a plain/white/clean background, keep it plain. Do NOT add office, room, or environmental context.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm: (1) face pixel-identical to reference; (2) no furniture added; (3) pose unchanged. If any fails, restart.",
            "DO NOT stretch primary subjects to fill the 4.6:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements not in the source image.",
            "Output must be exactly 4530×990 px — not square, not portrait.",
        ],
    ),

    # ── 1728 × 576 ── AR 3.0:1  WIDE BILLBOARD ───────────────────────────────
    (1728, 576): DimProfile(
        label="Wide billboard (1728×576)",
        canvas_description=(
            "a wide horizontal billboard banner (1728×576 px, 3:1 ratio). "
            "Classic 3:1 wide billboard with balanced height for clear, readable layouts."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 1728×576 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — do NOT redraw, regenerate, or envision it; simply drop it in at the correct position. "
            "Position the photo/hero on one side and distribute text and logo elements in the complementary zone across the full 1728 px width. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT provided crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background seamlessly."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Photo/person anchor one side, text/logo zones distributed across remaining width.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–576 px.",
            "Minimum 20 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: The person's face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose, gesture, and arm/hand position MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference crop.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out. No environmental additions.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture added, pose unchanged.",
            "DO NOT stretch primary subjects; only extend the background/environment.",
            "Output must be exactly 1728×576 px.",
        ],
    ),

    # ── 1280 × 448 ── AR 2.857:1  WIDE BILLBOARD ─────────────────────────────
    (1280, 448): DimProfile(
        label="Wide billboard (1280×448)",
        canvas_description=(
            "a wide horizontal billboard banner (1280×448 px, ~2.9:1 ratio). "
            "Wide format with enough height for multi-line text and clear visual hierarchy."
        ),
        ratio_str="2.9:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 1280×448 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without any modification. "
            "Use the 2.9:1 width by placing the photo/person as one anchor and distributing text and logos in the remaining horizontal space. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background seamlessly."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Photo anchor one side, text/logos spread across remaining width.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–448 px.",
            "Minimum 18 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch primary subjects; only extend background/environment.",
            "Output must be exactly 1280×448 px.",
        ],
    ),

    # ── 1152 × 288 ── AR 4.0:1  WIDE BILLBOARD ───────────────────────────────
    (1152, 288): DimProfile(
        label="Wide billboard (1152×288)",
        canvas_description=(
            "a wide horizontal billboard banner (1152×288 px, 4:1 ratio). "
            "Wide 4:1 format with limited height demanding single-row horizontal layout."
        ),
        ratio_str="4:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 1152×288 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 4:1 width by spreading logo, headline, subheading, and person across the full 1152 px. "
            "Scale all text to be legible at 288 px height. Do NOT wrap text into multiple narrow lines. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background seamlessly."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "NO vertical stacking — single horizontal row only.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–288 px.",
            "Minimum 14 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stack elements vertically; the 288 px height demands a single horizontal row.",
            "Output must be exactly 1152×288 px.",
        ],
    ),

    # ── 816 × 288 ── AR 2.83:1  WIDE STRIP ───────────────────────────────────
    (816, 288): DimProfile(
        label="Wide strip (816×288)",
        canvas_description=(
            "a wide horizontal strip banner (816×288 px, ~2.8:1 ratio). "
            "Compact wide format requiring a clean single-row horizontal layout."
        ),
        ratio_str="2.8:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 816×288 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Position the photo/person on one side and distribute text/logo in the remaining zone. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background seamlessly."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "NO vertical stacking — single horizontal row only.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–288 px.",
            "Minimum 12 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stack elements vertically; the 288 px height demands a single horizontal row.",
            "Output must be exactly 816×288 px.",
        ],
    ),

    # ── 768 × 288 ── AR 2.67:1  WIDE STRIP ───────────────────────────────────
    (768, 288): DimProfile(
        label="Wide strip (768×288)",
        canvas_description=(
            "a wide horizontal strip banner (768×288 px, ~2.7:1 ratio). "
            "Compact wide format requiring a clean single-row horizontal layout."
        ),
        ratio_str="2.7:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 768×288 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Position the photo/person on one side and distribute text/logo in the remaining zone. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background seamlessly."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "NO vertical stacking — single horizontal row only.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–288 px.",
            "Minimum 12 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stack elements vertically; the 288 px height demands a single horizontal row.",
            "Output must be exactly 768×288 px.",
        ],
    ),

    # ── 736 × 256 ── AR 2.875:1  WIDE STRIP ──────────────────────────────────
    (736, 256): DimProfile(
        label="Wide strip (736×256)",
        canvas_description=(
            "a wide horizontal strip banner (736×256 px, ~2.9:1 ratio). "
            "Very shallow wide format demanding compact single-row layout with legible text."
        ),
        ratio_str="2.9:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 736×256 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Scale all text to be legible at 256 px height. Do NOT wrap text into narrow vertical columns. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background seamlessly."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "NO vertical stacking — single horizontal row only.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–256 px.",
            "Minimum 10 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stack elements vertically; the 256 px height demands a single horizontal row.",
            "Output must be exactly 736×256 px.",
        ],
    ),

    # ── LANDSCAPE MODERATE (AR 1:1 – 2.5:1) ──────────────────────────────────

    # ── 3840 × 2160 ── AR 1.78:1  16:9 4K BANNER ────────────────────────────
    (3840, 2160): DimProfile(
        label="16:9 4K banner (3840×2160)",
        canvas_description=(
            "a standard 16:9 ultra-high-definition banner (3840×2160 px, 16:9 ratio). "
            "Full 4K resolution canvas with natural 16:9 proportions for cinematic, editorial, or advertising layouts."
        ),
        ratio_str="16:9",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 3840×2160 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the natural 16:9 proportions to create a balanced layout: hero/person on one third, headline and supporting text on remaining two thirds (or mirrored). "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged against the SAME background it already has. "
            "FOR GENERIC IMAGES: Place the main subject/scene in a natural 16:9 cinematic composition."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining space with a seamless background extension matching the original scene. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Balanced left-right layout respecting the 16:9 natural proportions.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within the 3840×2160 canvas bounds.",
            "Minimum 40 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT stretch or squash primary subjects.",
            "Output must be exactly 3840×2160 px.",
        ],
    ),

    # ── 1680 × 810 ── AR 2.07:1  MODERATE LANDSCAPE BANNER ───────────────────
    (1680, 810): DimProfile(
        label="Moderate landscape banner (1680×810)",
        canvas_description=(
            "a moderate-wide horizontal banner (1680×810 px, ~2.1:1 ratio). "
            "Near-widescreen format with generous height for multi-element advertising layouts."
        ),
        ratio_str="2.1:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 1680×810 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 2.1:1 proportions to create a well-balanced layout — hero/person on one side, headline and text on the other. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically and extend background seamlessly."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Balanced left/right zones with natural visual hierarchy.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–810 px.",
            "Minimum 24 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "Output must be exactly 1680×810 px.",
        ],
    ),

    # ── 1152 × 640 ── AR 1.8:1  MODERATE LANDSCAPE BANNER ────────────────────
    (1152, 640): DimProfile(
        label="Moderate landscape banner (1152×640)",
        canvas_description=(
            "a moderate-wide horizontal banner (1152×640 px, ~1.8:1 ratio). "
            "Near-HD widescreen proportions with balanced horizontal and vertical space."
        ),
        ratio_str="1.8:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 1152×640 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the balanced 1.8:1 proportions for a clean split layout — hero on one side, text hierarchy on the other. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Balanced left/right zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–640 px.",
            "Minimum 20 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "Output must be exactly 1152×640 px.",
        ],
    ),

    # ── 864 × 720 ── AR 1.2:1  NEAR-SQUARE LANDSCAPE BANNER ─────────────────
    (864, 720): DimProfile(
        label="Near-square landscape banner (864×720)",
        canvas_description=(
            "a near-square landscape banner (864×720 px, ~1.2:1 ratio). "
            "Compact almost-square canvas with balanced proportions for centered or split layouts."
        ),
        ratio_str="1.2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 864×720 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the near-square proportions for a centered or split composition — person/hero in one half, text and logo in the other. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene naturally in a near-square composition."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Balanced split or centered composition.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within the 864×720 canvas bounds.",
            "Minimum 18 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "Output must be exactly 864×720 px.",
        ],
    ),

    # ── 864 × 480 ── AR 1.8:1  MODERATE LANDSCAPE BANNER ────────────────────
    (864, 480): DimProfile(
        label="Moderate landscape banner (864×480)",
        canvas_description=(
            "a moderate-wide horizontal banner (864×480 px, ~1.8:1 ratio). "
            "Near-HD proportions with balanced space for advertising or scene layouts."
        ),
        ratio_str="1.8:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 864×480 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 1.8:1 proportions for a balanced split — hero/person on one side, text hierarchy on the other. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene organically."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Balanced left/right zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–480 px.",
            "Minimum 16 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "Output must be exactly 864×480 px.",
        ],
    ),

    # ── 608 × 304 ── AR 2.0:1  STANDARD BANNER ───────────────────────────────
    (608, 304): DimProfile(
        label="Standard 2:1 banner (608×304)",
        canvas_description=(
            "a standard 2:1 horizontal banner (608×304 px). "
            "Classic equal-proportion banner format suitable for balanced layouts."
        ),
        ratio_str="2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 608×304 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 2:1 proportions for a clean split — person/hero left, headline and text right (or mirrored). "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene naturally."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Person/hero one side, text/logo other side.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–304 px.",
            "Minimum 12 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "Output must be exactly 608×304 px.",
        ],
    ),

    # ── 600 × 320 ── AR 1.875:1  MODERATE BANNER ─────────────────────────────
    (600, 320): DimProfile(
        label="Moderate banner (600×320)",
        canvas_description=(
            "a moderate-wide horizontal banner (600×320 px, ~1.9:1 ratio). "
            "Compact web banner format with balanced proportions."
        ),
        ratio_str="1.9:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 600×320 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 1.9:1 proportions for a clean balanced layout. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene naturally."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Balanced split layout.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–320 px.",
            "Minimum 12 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "Output must be exactly 600×320 px.",
        ],
    ),

    # ── 600 × 280 ── AR 2.14:1  MODERATE BANNER ──────────────────────────────
    (600, 280): DimProfile(
        label="Moderate banner (600×280)",
        canvas_description=(
            "a moderate-wide horizontal banner (600×280 px, ~2.1:1 ratio). "
            "Compact web banner format with slightly wider proportions."
        ),
        ratio_str="2.1:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            "Fill the 600×280 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 2.1:1 proportions for a clean layout with person one side and text/logo the other. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Place the main subject/scene naturally."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Person/hero one side, text/logo other side.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–280 px.",
            "Minimum 12 px padding between elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "Output must be exactly 600×280 px.",
        ],
    ),

    # ── PORTRAIT TALL (AR < 0.45:1) ───────────────────────────────────────────

    # ── 224 × 832 ── AR 1:3.71  ULTRA-TALL PORTRAIT STRIP ────────────────────
    (224, 832): DimProfile(
        label="Ultra-tall portrait strip (224×832)",
        canvas_description=(
            "an ultra-tall portrait strip banner (224×832 px, ~1:3.7 ratio). "
            "Extremely narrow vertical format — nearly 4× taller than wide — requiring strict top-to-bottom stacking."
        ),
        ratio_str="1:3.7",
        orientation="portrait_tall",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.35,
        element_guidance=(
            "Fill the 224×832 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 832 px height seamlessly. "
            "Scale ALL components to fit within 224 px width — elements may NOT overflow horizontally. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom: logo → hero image → headline → body text → CTA. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Compose the scene vertically top-to-bottom. No invented text or logos."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM stack: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–224 px (hard limit — no horizontal overflow).",
            "Center elements horizontally: x = (224 - element_width) / 2.",
            "20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is an ultra-tall portrait strip.",
            "DO NOT place elements side by side — strictly vertical stacking only.",
            "Output must be exactly 224×832 px — NOT landscape.",
        ],
    ),

    # ── 288 × 768 ── AR 1:2.67  TALL PORTRAIT BANNER ─────────────────────────
    (288, 768): DimProfile(
        label="Tall portrait banner (288×768)",
        canvas_description=(
            "a tall portrait banner (288×768 px, ~1:2.7 ratio). "
            "Narrow vertical format requiring top-to-bottom stacking."
        ),
        ratio_str="1:2.7",
        orientation="portrait_tall",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.40,
        element_guidance=(
            "Fill the 288×768 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 768 px height seamlessly. "
            "Scale ALL components to fit within 288 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom: logo → hero image → headline → body text → CTA. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Compose the scene vertically. No invented text or logos."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–288 px.",
            "Center elements horizontally: x = (288 - element_width) / 2.",
            "20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a tall portrait format.",
            "DO NOT place elements side by side.",
            "Output must be exactly 288×768 px — NOT landscape.",
        ],
    ),

    # ── 432 × 1008 ── AR 1:2.33  TALL PORTRAIT BANNER ────────────────────────
    (432, 1008): DimProfile(
        label="Tall portrait banner (432×1008)",
        canvas_description=(
            "a tall portrait banner (432×1008 px, ~1:2.3 ratio). "
            "Vertical format with substantial height for multi-section advertising layouts."
        ),
        ratio_str="1:2.3",
        orientation="portrait_tall",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.42,
        element_guidance=(
            "Fill the 432×1008 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 1008 px height seamlessly. "
            "Scale ALL components to fit within 432 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom: logo → hero image → headline → body text → CTA. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Compose the scene vertically. No invented text or logos."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–432 px.",
            "Center elements horizontally: x = (432 - element_width) / 2.",
            "20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a tall portrait format.",
            "DO NOT place elements side by side.",
            "Output must be exactly 432×1008 px — NOT landscape.",
        ],
    ),

    # ── 504 × 1152 ── AR 1:2.29  TALL PORTRAIT BANNER ────────────────────────
    (504, 1152): DimProfile(
        label="Tall portrait banner (504×1152)",
        canvas_description=(
            "a tall portrait banner (504×1152 px, ~1:2.3 ratio). "
            "Vertical format with generous height for stacked advertising or scenic layouts."
        ),
        ratio_str="1:2.3",
        orientation="portrait_tall",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.42,
        element_guidance=(
            "Fill the 504×1152 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 1152 px height seamlessly. "
            "Scale ALL components to fit within 504 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom: logo → hero image → headline → body text → CTA. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Compose the scene vertically. No invented text or logos."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–504 px.",
            "Center elements horizontally: x = (504 - element_width) / 2.",
            "20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a tall portrait format.",
            "DO NOT place elements side by side.",
            "Output must be exactly 504×1152 px — NOT landscape.",
        ],
    ),

    # ── PORTRAIT MODERATE (AR 0.45:1 – 0.75:1) ───────────────────────────────

    # ── 2160 × 3840 ── AR 9:16  4K PORTRAIT ──────────────────────────────────
    (2160, 3840): DimProfile(
        label="4K portrait (2160×3840)",
        canvas_description=(
            "a 9:16 ultra-high-definition portrait canvas (2160×3840 px). "
            "Standard 9:16 vertical format at 4K resolution for full-screen digital signage or video assets."
        ),
        ratio_str="9:16",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 2160×3840 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 9:16 vertical proportions: logo/headline near top, hero image in centre, body text and CTA below. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Full-screen vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo/headline → photo/hero → body text → CTA.",
            "ALL elements must remain within x: 0–2160 px.",
            "Center elements horizontally: x = (2160 - element_width) / 2.",
            "40 px vertical padding between stacked elements.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a 9:16 portrait format.",
            "Output must be exactly 2160×3840 px — NOT landscape.",
        ],
    ),

    # ── 1080 × 1920 ── AR 9:16  FULL HD PORTRAIT ─────────────────────────────
    (1080, 1920): DimProfile(
        label="Full HD portrait (1080×1920)",
        canvas_description=(
            "a 9:16 full-HD portrait canvas (1080×1920 px). "
            "Standard mobile/story 9:16 vertical format for digital signage and social media."
        ),
        ratio_str="9:16",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 1080×1920 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Use the 9:16 vertical proportions: logo/headline near top, hero image in centre, body text and CTA below. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Full-screen vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo/headline → photo/hero → body text → CTA.",
            "ALL elements must remain within x: 0–1080 px.",
            "Center elements horizontally: x = (1080 - element_width) / 2.",
            "30 px vertical padding between stacked elements.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a 9:16 portrait format.",
            "Output must be exactly 1080×1920 px — NOT landscape.",
        ],
    ),

    # ── 990 × 1620 ── AR 1:1.636  PORTRAIT BANNER ────────────────────────────
    (990, 1620): DimProfile(
        label="Portrait banner (990×1620)",
        canvas_description=(
            "a portrait banner (990×1620 px, ~1:1.6 ratio). "
            "Moderate portrait format with generous width for balanced vertical layouts."
        ),
        ratio_str="1:1.6",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.48,
        element_guidance=(
            "Fill the 990×1620 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full canvas seamlessly. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom: logo/headline at top, hero in centre, body text and CTA below. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo/headline → photo/hero → body text → CTA.",
            "ALL elements must remain within x: 0–990 px.",
            "Center elements horizontally: x = (990 - element_width) / 2.",
            "24 px vertical padding between stacked elements.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 990×1620 px — NOT landscape.",
        ],
    ),

    # ── 684 × 1368 ── AR 1:2  PORTRAIT BANNER ────────────────────────────────
    (684, 1368): DimProfile(
        label="Portrait banner (684×1368)",
        canvas_description=(
            "a tall portrait banner (684×1368 px, 1:2 ratio). "
            "Standard 1:2 vertical format for digital signage and large-format portrait displays."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 684×1368 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 1368 px height seamlessly. "
            "Scale ALL components to fit within 684 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom: logo → hero image → headline → body text → CTA. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Vertical scene composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–684 px.",
            "Center elements horizontally: x = (684 - element_width) / 2.",
            "20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "DO NOT place elements side by side.",
            "Output must be exactly 684×1368 px — NOT landscape.",
        ],
    ),

    # ── 648 × 1296 ── AR 1:2  PORTRAIT BANNER ────────────────────────────────
    (648, 1296): DimProfile(
        label="Portrait banner (648×1296)",
        canvas_description=(
            "a tall portrait banner (648×1296 px, 1:2 ratio). "
            "Standard 1:2 vertical format for portrait digital displays."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 648×1296 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 1296 px height seamlessly. "
            "Scale ALL components to fit within 648 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Vertical scene composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–648 px.",
            "Center elements horizontally. 20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 648×1296 px — NOT landscape.",
        ],
    ),

    # ── 576 × 1080 ── AR 8:15 (~9:16)  PORTRAIT BANNER ───────────────────────
    (576, 1080): DimProfile(
        label="Portrait banner (576×1080)",
        canvas_description=(
            "a portrait banner (576×1080 px, ~9:16 ratio). "
            "Near-standard 9:16 vertical format for portrait digital screens."
        ),
        ratio_str="8:15",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 576×1080 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 1080 px height seamlessly. "
            "Scale ALL components to fit within 576 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–576 px.",
            "Center elements horizontally. 20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 576×1080 px — NOT landscape.",
        ],
    ),

    # ── 504 × 1008 ── AR 1:2  PORTRAIT BANNER ────────────────────────────────
    (504, 1008): DimProfile(
        label="Portrait banner (504×1008)",
        canvas_description=(
            "a tall portrait banner (504×1008 px, 1:2 ratio). "
            "Standard 1:2 vertical format for portrait digital signage."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 504×1008 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 1008 px height seamlessly. "
            "Scale ALL components to fit within 504 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–504 px.",
            "Center elements horizontally. 20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 504×1008 px — NOT landscape.",
        ],
    ),

    # ── 480 × 960 ── AR 1:2  PORTRAIT BANNER ─────────────────────────────────
    (480, 960): DimProfile(
        label="Portrait banner (480×960)",
        canvas_description=(
            "a tall portrait banner (480×960 px, 1:2 ratio). "
            "Standard 1:2 vertical format for portrait digital screens."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 480×960 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 960 px height seamlessly. "
            "Scale ALL components to fit within 480 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–480 px.",
            "Center elements horizontally. 20 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 480×960 px — NOT landscape.",
        ],
    ),

    # ── 432 × 864 ── AR 1:2  PORTRAIT BANNER ─────────────────────────────────
    (432, 864): DimProfile(
        label="Portrait banner (432×864)",
        canvas_description=(
            "a tall portrait banner (432×864 px, 1:2 ratio). "
            "Standard 1:2 vertical format for QMS portrait screens."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 432×864 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 864 px height seamlessly. "
            "Scale ALL components to fit within 432 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–432 px.",
            "Center elements horizontally. 18 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 432×864 px — NOT landscape.",
        ],
    ),

    # ── 432 × 768 ── AR 9:16  PORTRAIT BANNER ────────────────────────────────
    (432, 768): DimProfile(
        label="Portrait banner (432×768)",
        canvas_description=(
            "a 9:16 portrait banner (432×768 px). "
            "Standard 9:16 vertical format for QMS portrait screens."
        ),
        ratio_str="9:16",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 432×768 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 768 px height seamlessly. "
            "Scale ALL components to fit within 432 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom: logo → hero → headline → body text → CTA. "
            "CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–432 px.",
            "Center elements horizontally. 18 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a 9:16 portrait format.",
            "Output must be exactly 432×768 px — NOT landscape.",
        ],
    ),

    # ── 396 × 792 ── AR 1:2  PORTRAIT BANNER ─────────────────────────────────
    (396, 792): DimProfile(
        label="Portrait banner (396×792)",
        canvas_description=(
            "a tall portrait banner (396×792 px, 1:2 ratio). "
            "Standard 1:2 vertical format for QMS portrait screens."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 396×792 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 792 px height seamlessly. "
            "Scale ALL components to fit within 396 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–396 px.",
            "Center elements horizontally. 16 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 396×792 px — NOT landscape.",
        ],
    ),

    # ── 384 × 768 ── AR 1:2  PORTRAIT BANNER ─────────────────────────────────
    (384, 768): DimProfile(
        label="Portrait banner (384×768)",
        canvas_description=(
            "a tall portrait banner (384×768 px, 1:2 ratio). "
            "Standard 1:2 vertical format for QMS portrait screens."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 384×768 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 768 px height seamlessly. "
            "Scale ALL components to fit within 384 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–384 px.",
            "Center elements horizontally. 16 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 384×768 px — NOT landscape.",
        ],
    ),

    # ── 360 × 720 ── AR 1:2  PORTRAIT BANNER ─────────────────────────────────
    (360, 720): DimProfile(
        label="Portrait banner (360×720)",
        canvas_description=(
            "a tall portrait banner (360×720 px, 1:2 ratio). "
            "Standard 1:2 vertical format for QMS portrait screens."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 360×720 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 720 px height seamlessly. "
            "Scale ALL components to fit within 360 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–360 px.",
            "Center elements horizontally. 16 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 360×720 px — NOT landscape.",
        ],
    ),

    # ── 352 × 704 ── AR 1:2  PORTRAIT BANNER ─────────────────────────────────
    (352, 704): DimProfile(
        label="Portrait banner (352×704)",
        canvas_description=(
            "a tall portrait banner (352×704 px, 1:2 ratio). "
            "Standard 1:2 vertical format for QMS portrait screens."
        ),
        ratio_str="1:2",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            "Fill the 352×704 pixel space completely, edge-to-edge. "
            "CRITICAL: The background MUST paint the full 704 px height seamlessly. "
            "Scale ALL components to fit within 352 px width. "
            "FOR ADVERTISING IMAGES: Treat the person photo as a SEALED PNG STICKER — drop it in at the correct position without modification. "
            "Stack elements top-to-bottom. CRITICAL — PERSON IS A STICKER NOT A DRAWING: Paste the EXACT crop unchanged. "
            "FOR GENERIC IMAGES: Natural vertical composition."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background extension. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "TOP-TO-BOTTOM: logo → photo → headline → body text → CTA.",
            "ALL elements must remain within x: 0–352 px.",
            "Center elements horizontally. 14 px vertical padding between stacked elements.",
            "DO NOT place elements side by side.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy only.",
            "CRITICAL — FACE INTEGRITY: Face MUST be identical to the provided photo crop. ANY deviation is a failure.",
            "CRITICAL — NO POSE CHANGE: Pose and gestures MUST be identical to the reference crop.",
            "CRITICAL — NO INVENTED FURNITURE: Do NOT add desk, table, chair, or any object not in the reference.",
            "CRITICAL — PASTE DO NOT BLEND: Paste the human photo as a discrete crop — do NOT blend or redraw.",
            "CRITICAL — BACKGROUND CONTEXT BANNED: Plain background in = plain background out.",
            "CRITICAL — SELF-VERIFICATION BEFORE OUTPUT: Confirm face identical, no furniture, pose unchanged.",
            "DO NOT use a horizontal layout — this is a portrait format.",
            "Output must be exactly 352×704 px — NOT landscape.",
        ],
    ),
}


# ── Lookup helper ──────────────────────────────────────────────────────────────

def get_profile(target_w: int, target_h: int) -> DimProfile:
    """
    Return the DimProfile for the given QMS dimensions.
    Falls back to a generic landscape profile if the exact dimension is not
    in the dictionary.
    """
    profile = QMS_PROFILES.get((target_w, target_h))
    if profile:
        return profile

    # Generic fallback based on aspect ratio
    ar = target_w / max(target_h, 1)
    if ar >= 6.0:
        return _generic_extreme_wide(target_w, target_h, ar)
    elif ar >= 2.5:
        return _generic_wide(target_w, target_h, ar)
    elif ar >= 1.2:
        return _generic_moderate(target_w, target_h, ar)
    elif ar <= 0.75:
        return _generic_portrait(target_w, target_h, ar)
    else:
        return _generic_moderate(target_w, target_h, ar)


def _generic_extreme_wide(w: int, h: int, ar: float) -> DimProfile:
    return DimProfile(
        label=f"Extreme wide (custom {w}×{h})",
        canvas_description=f"an extremely wide horizontal strip banner ({w}×{h} px, {ar:.1f}:1 ratio)",
        ratio_str=f"{ar:.1f}:1",
        orientation="landscape_extreme",
        layout_direction="left-to-right",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.85,
        element_guidance=(
            f"Fill the {w}×{h} pixel space completely, edge-to-edge. "
            f"Scale all components to fit within {h} px height. "
            "For advertising images — Photos: head/torso crop only at this height. "
            "For generic images — place the main subject/scene filling the canvas naturally, no invented text or logos."
        ),
        fill_direction="horizontally",
        fill_description="Fill empty horizontal space with background extension only — no new scene content.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "For non-advertising images (no logo, headline, or CTA detected), place only the detected visual components: background, scene, subject, or photo.",
            f"The background component fills the entire {w}×{h} canvas",
            "Single horizontal row: left-to-right arrangement",
            f"ALL elements within y: 0–{h} px",
            "16 px horizontal padding between elements",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image — if an element was not detected, leave it out entirely.",
            f"DO NOT make any element taller than {h} px",
            "DO NOT stack elements vertically",
            f"Output must be {w} px wide × {h} px tall",
        ],
    )


def _generic_wide(w: int, h: int, ar: float) -> DimProfile:
    return DimProfile(
        label=f"Wide billboard (custom {w}×{h})",
        canvas_description=f"a wide horizontal billboard banner ({w}×{h} px, {ar:.1f}:1 ratio)",
        ratio_str=f"{ar:.1f}:1",
        orientation="landscape_wide",
        layout_direction="left-to-right",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.90,
        element_guidance=(
            f"Fill the {w}×{h} pixel space completely, edge-to-edge. "
            f"Scale all components to fit within {h} px height. "
            "For advertising images — place photo left, text and logos right. "
            "For generic images — place the main subject/scene filling the canvas naturally, no invented text or logos."
        ),
        fill_direction="horizontally",
        fill_description="Fill empty horizontal space with background extension — no new imagery.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "For non-advertising images (no logo, headline, or CTA detected), place only the detected visual components: background, scene, subject, or photo.",
            f"The background component fills the entire {w}×{h} canvas",
            "Photo left zone, text/logos right zone",
            f"ALL elements within y: 0–{h} px",
            "20 px horizontal padding",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image — if an element was not detected, leave it out entirely.",
            "DO NOT use a portrait layout",
            "Background extension only — no new scene content",
            f"Output must be {w}×{h} px",
        ],
    )


def _generic_moderate(w: int, h: int, ar: float) -> DimProfile:
    return DimProfile(
        label=f"Moderate landscape (custom {w}×{h})",
        canvas_description=f"a landscape banner ({w}×{h} px, {ar:.1f}:1 ratio)",
        ratio_str=f"{ar:.1f}:1",
        orientation="landscape_moderate",
        layout_direction="left-to-right",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.90,
        element_guidance=(
            f"Fill the {w}×{h} pixel space completely, edge-to-edge. "
            f"Scale all components to fit within {h} px height. "
            "For advertising images — place photo left, text right. "
            "For generic images — place the main subject/scene filling the canvas naturally, no invented text or logos."
        ),
        fill_direction="horizontally",
        fill_description="Fill remaining horizontal space with background extension only.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "For non-advertising images (no logo, headline, or CTA detected), place only the detected visual components: background, scene, subject, or photo.",
            f"The background component fills the entire {w}×{h} canvas",
            "Photo left, text right",
            f"ALL elements within y: 0–{h} px",
            "18 px horizontal padding",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image — if an element was not detected, leave it out entirely.",
            "Background fill only for empty space",
            f"Output must be {w}×{h} px",
        ],
    )


def _generic_portrait(w: int, h: int, ar: float) -> DimProfile:
    return DimProfile(
        label=f"Portrait (custom {w}×{h})",
        canvas_description=f"a portrait banner ({w}×{h} px, 1:{1/ar:.1f} ratio)",
        ratio_str=f"1:{1/ar:.1f}",
        orientation="portrait_tall",
        layout_direction="top-to-bottom",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.45,
        element_guidance=(
            f"Fill the {w}×{h} pixel space completely, edge-to-edge. "
            f"Scale all components to fit within {w} px width. Stack elements top-to-bottom. "
            "For advertising images — logo top, photo center, text above/below. "
            "For generic images — place the main subject/scene filling the canvas naturally, no invented text or logos."
        ),
        fill_direction="vertically",
        fill_description="Fill empty vertical space with background extension only — no new imagery.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "For non-advertising images (no logo, headline, or CTA detected), place only the detected visual components: background, scene, subject, or photo.",
            f"The background component fills the entire {w}×{h} canvas",
            "TOP-TO-BOTTOM: logo → headline → photo → body text → CTA → fine print",
            f"ALL elements within x: 0–{w} px",
            "20 px vertical padding between stacked elements",
            f"Center elements horizontally: x = ({w} - element_width) / 2",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image — if an element was not detected, leave it out entirely.",
            "DO NOT use a horizontal layout — this is a portrait format",
            "DO NOT place elements side by side",
            f"Output must be {w} px wide × {h} px tall — NOT landscape",
        ],
    )
