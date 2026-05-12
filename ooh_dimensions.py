"""
ooh_dimensions.py — Per-dimension layout profiles for OOH banner recomposition.

Every OOH dimension gets a profile that is injected into the main recompose prompt
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

OOH_PROFILES: dict[tuple[int, int], DimProfile] = {

    # ── 2072 × 252 ── handled by banner_2072x252.py — disabled here ─────────────
    # This dimension is routed to banner_2072x252.py in main.py.
    # The profile below is intentionally commented out.
    #
    # (2072, 252): DimProfile(
    #     label="Extreme thin wide strip (2072×252)",
    #     canvas_description=("an extremely thin, ultra-wide horizontal strip banner..."),
    #     ratio_str="8:1",
    #     orientation="landscape_extreme",
    #     layout_direction="left-to-right",
    #     arrangement_order=["background", "logo", "photo", "headline", "body_text", "cta", "fine_print"],
    #     element_max_height=0.95,
    #     element_guidance=("..."),
    #     fill_direction="horizontally",
    #     fill_description=("..."),
    #     layout_rules=[],
    #     dimension_warnings=[],
    # ),

    # ── 792 × 216 ── AR 3.67:1  THIN WIDE STRIP ──────────────────────────────
   (792, 216): DimProfile(
        label="Thin wide strip (792×216)",
        canvas_description=(
            "a very short wide strip (792×216 px, ~3.7:1): only 216 px tall — "
            "one horizontal band of content; widen by extending background only."
        ),
        ratio_str="3.7:1",
        orientation="landscape_extreme",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Edge-to-edge 792×216. Lay every element in a single horizontal row (left→right). "
            "Scale subjects and text to fit inside 216 px height without squashing faces. "
            "Widen empty areas by continuing the background sideways — do not stretch people or logos wide."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Extend background or scene horizontally into gaps. "
            "Do not clone people, products, or text to fill width."
        ),
        layout_rules=[
            "Use only layers from the source; paste each once, unchanged.",
            "People and logos: same pixels as the supplied crops — no redraw, no new faces.",
            "y must stay 0–216; keep natural aspect ratios (no vertical squash).",
            "Ads: hero on one side, text/logo on the other; generics: subject + extended background.",
            "12 px minimum margin from edges between separate elements.",
        ],
        dimension_warnings=[
            "No vertical stacks — one row only for 216 px height.",
            "No duplicated subjects or logos to pad width.",
            "No invented text or marks not in the source.",
            "Exact output 792×216 px landscape strip.",
        ],
    ),

    # ── 1344 × 432 ── AR 3.1:1  WIDE BILLBOARD ───────────────────────────────
   (1344, 432): DimProfile(
        label="Wide billboard (1344×432)",
        canvas_description=(
            "a wide horizontal billboard banner (1344×432 px, ~3:1 ratio). "
            "Classic outdoor billboard format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1344×432 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 3:1 width by positioning the photo/hero as a visual anchor and distributing text elements in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1344x432 canvas without stretching the subject or creating visible seams.",
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
            "DO NOT cluster content in the center — spread organically across the 1344 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1344×432 px — not square, not portrait.",
        ],
    ),

    # ── 1836 × 432 ── AR 4.25:1  SUPER WIDE BILLBOARD ────────────────────────
    (1836, 432): DimProfile(
        label="Super wide billboard (1836×432)",
        canvas_description=(
            "a super-wide horizontal billboard banner (1836×432 px, ~4.25:1 ratio). "
            "Extreme width requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="4.25:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1836×432 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the massive 4.25:1 width by positioning the photo/hero as a visual anchor and distributing text elements (headlines, body, CTA) intelligently across the remaining space. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1836x432 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side or anchor point, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–432 px.",
            "Minimum 24 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the massive 4.25:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the center — spread organically across the 1836 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 1836×432 px — not square, not portrait.",
        ],
    ),

    # ── 1060 × 360 ── AR 2.94:1  WIDE BILLBOARD ──────────────────────────────
   (1060, 360): DimProfile(
        label="Wide billboard (1060×360)",
        canvas_description=(
            "a wide horizontal billboard banner (1060×360 px, ~3:1 ratio). "
            "Requires a single, unified background stretching across the entire width."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1060×360 pixel space edge-to-edge as a SINGLE unified image. "
            "CRITICAL ERROR AVOIDANCE: Do NOT create a 'split-screen' effect. There must be NO visible vertical seams, harsh lines, or borders between the original photo and the extended background space. "
            "The background (whether extended scenery, soft gradient, or solid color) MUST blend flawlessly and continuously behind the text. "
            "Position the photo/hero as the visual anchor and place text neatly in the smoothly extended clear zone."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Extend the background environment horizontally. The transition from the original photo's edge into the newly filled area MUST be a perfect, seamless blend. "
            "Use feathering, edge-blending, or continuous lighting to absolutely prevent any harsh vertical lines or stitching artifacts."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component or subject.",
            "CRITICAL: Human faces, bodies, and clothing must stay exactly as they are.",
            "Rule 1: UNIFIED CANVAS. The background must flow continuously across the entire 1060px width. Completely erase or blend any seams.",
            "Rule 2: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR ADVERTISING IMAGES: Position the main visual on one side, and ensure the background flows organically into the other side to create a clean bed for the text.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–360 px."
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT CREATE A SPLIT-SCREEN OR VISIBLE SEAM. The final output must look like one continuous, unstitched photograph.",
            "CRITICAL: DO NOT leave a harsh vertical line where the original image ends and the extension begins.",
            "CRITICAL: DO NOT alter, redraw, or reinvent the human subjects.",
            "CRITICAL: DO NOT duplicate any component to fill empty space.",
            "DO NOT stretch primary subjects to fill the 3:1 width.",
            "Output must be exactly 1060 px wide × 360 px tall."
        ],
    ),

    # ── 1280 × 384 ── AR 3.33:1  WIDE STRIP BILLBOARD ────────────────────────
    (1280, 384): DimProfile(
        label="Wide strip billboard (1280×384)",
        canvas_description=(
            "a wide horizontal strip billboard banner (1280×384 px, ~3.3:1 ratio). "
            "Wide format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3.3:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1280×384 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 3.3:1 width by positioning the photo/hero as a visual anchor and distributing text elements in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1280x384 canvas without stretching the subject or creating visible seams.",
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
            "DO NOT stretch primary subjects to fill the 3.3:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the center — spread organically across the 1280 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
        ],
    ),

    # ── 1024 × 320 ── AR 3.2:1  WIDE STRIP ───────────────────────────────────
    (1024, 320): DimProfile(
        label="Wide strip (1024×320)",
        canvas_description=(
            "a wide horizontal strip banner (1024×320 px, ~3.2:1 ratio). "
            "Wide format with limited vertical space, requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3.2:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1024×320 pixel space completely, edge-to-edge. "
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
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1024x320 canvas without stretching the subject or creating visible seams.",
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
            "DO NOT stretch primary subjects to fill the 3.2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the horizontal space organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
        ],
    ),

    # ── 3924 × 972 ── AR 4.04:1  LARGE WIDE BILLBOARD ───────────────────────
    (3924, 972): DimProfile(
        label="Large wide billboard (3924×972)",
        canvas_description=(
            "a very large wide horizontal banner (3924×972 px, ~4:1 ratio). "
            "High resolution with generous height, requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="4:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 3924×972 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene naturally (centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Spread elements across the ENTIRE 3924 pixel width. Photos/persons can be full-body. Scale headlines and body text proportionally. Do NOT cluster elements in the middle."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Large horizontal zones must be filled with a seamless background or scene extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, foreground elements, or unique objects to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human faces, bodies, and clothing must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically. Extend the background/environment seamlessly to fill the 3924x972 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the 4:1 width. Place the photo/hero in a left or right anchor zone. Place text/headlines adjacent to the subject. Place CTA/QR in the opposing anchor zone.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–972 px."
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component or subject.",
            "CRITICAL: DO NOT stretch primary subjects to fill the massive 4:1 width; only extend the background/environment.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs) that do not exist in the source image.",
            "DO NOT cluster all content in a small central zone; utilize the full 3924 px width organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended horizontal background is completely seamless."
        ],
    ),
    # ── 840 × 360 ── AR 2.33:1  MODERATE WIDE ────────────────────────────────
    (840, 360): DimProfile(
        label="Moderate wide banner (840×360)",
        canvas_description=(
            "a moderate-width horizontal banner (840×360 px, ~2.3:1 ratio). "
            "Balanced proportions requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="2.3:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 840×360 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 2.3:1 width by positioning the photo/hero as a visual anchor and distributing text elements in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 840x360 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–360 px.",
            "Minimum 16 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT use a rigid vertical/portrait layout stack; utilize the horizontal 2.3:1 space organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
        ],
    ),

    # ── 1232 × 672 ── AR 1.83:1  MODERATE LANDSCAPE ──────────────────────────
   (1232, 672): DimProfile(
        label="Moderate landscape banner (1232×672)",
        canvas_description=(
            "a moderate landscape banner (1232×672 px, ~1.8:1 ratio). "
            "Generous height, requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="1.8:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1232×672 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene naturally (e.g., rule of thirds or organically composed). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the width by positioning the photo/hero as an anchor and distributing text elements (headlines, body) adjacent or in complementary zones. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1232x672 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side or central-adjacent, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–672 px.",
            "Minimum 20 px padding between distinct advertising elements (text, logo, CTA).",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT use a rigid portrait layout stack or leave large empty voids on the sides; utilize the horizontal space organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended horizontal background is completely seamless.",
        ],
    ),
    # ── 1952 × 896 ── AR 2.18:1  WIDE LANDSCAPE ──────────────────────────────
    (1952, 896): DimProfile(
        label="Wide landscape banner (1952×896)",
        canvas_description=(
            "a wide landscape banner (1952×896 px, ~2.2:1 ratio). "
            "Large format requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="2.2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 1952×896 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 2.2:1 width by positioning the photo/hero as a visual anchor and distributing text elements in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 1952x896 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–896 px.",
            "Minimum 24 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the center — spread organically across the 1952 px width.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
        ],
    ),
    # ── 960 × 576 ── AR 1.67:1  NEAR 16:9 ────────────────────────────────────
    (960, 576): DimProfile(
        label="Near 16:9 banner (960×576)",
        canvas_description=(
            "a near-widescreen banner (960×576 px, ~1.67:1 / close to 16:9 ratio). "
            "Balanced, screen-like proportions requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="1.67:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 960×576 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 1.67:1 width by positioning the photo/hero as a visual anchor and distributing text elements in the adjacent or opposing clear space. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 960x576 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width. Position the main visual (subject/product) on one side, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–576 px.",
            "Minimum 18 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 1.67:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the center — utilize the 960 px width organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
        ],
    ),

    # ── 800 × 400 ── AR 2:1  STANDARD LANDSCAPE ──────────────────────────────
   (800, 400): DimProfile(
        label="Standard 2:1 banner (800×400)",
        canvas_description=(
            "a standard landscape banner (800×400 px, 2:1 ratio). "
            "Requires a natural, unbroken horizontal visual flow across the standard widescreen format."
        ),
        ratio_str="2:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            "Fill the 800×400 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or rule of thirds). Extend the background environment horizontally without stretching the subject or breaking visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 2:1 width by positioning the photo/hero as a visual anchor (e.g., left or right) and distributing text elements in the opposing or adjacent clear space."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with a seamless background or scene environment extension. "
            "Maintain natural perspective, lighting, and continuous flow. "
            "Strictly NO duplication of primary subjects or unique foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background seamlessly to fill the 800x400 canvas without stretching the subject.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner. Position the main visual (subject/product) on one side, with text and logos placed in the complementary space.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–400 px.",
            "Minimum 16 px padding between distinct advertising elements and canvas edges.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT use a rigid vertical/portrait layout stack; utilize the horizontal 2:1 space organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
        ],
    ),

    # ── 504 × 1008 ── AR 1:2  TALL PORTRAIT ──────────────────────────────────
   (504, 1008): DimProfile(
        label="Tall portrait banner (504×1008)",
        canvas_description=(
            "a tall vertical portrait banner (504×1008 px, 1:2 ratio). "
            "Vertical format requiring a natural, unbroken vertical visual flow."
        ),
        ratio_str="1:2",
        orientation="portrait_tall",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95, 
        element_guidance=(
            "Fill the 504×1008 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered vertically or following the rule of thirds). Extend the background environment vertically without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 1:2 height by positioning the photo/hero as a visual anchor and distributing text elements intelligently in the clear vertical space (above and/or below). Do NOT cluster elements tightly."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 504x1008 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner height. Position the main visual (subject/product) as a central or offset anchor, with text and logos placed in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain strictly within x: 0–504 px.",
            "Minimum 20 px vertical padding between distinct advertising elements and canvas edges."
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects vertically to fill the 1:2 height; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT place ad elements side by side if they require full width; utilize the vertical stack organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended vertical background is completely seamless.",
            "Output must be exactly 504 px wide × 1008 px tall."
        ],
    ),

    # ── 768 × 1152 ── AR 1:1.5  PORTRAIT ─────────────────────────────────────
   (768, 1152): DimProfile(
        label="Portrait banner (768×1152)",
        canvas_description=(
            "a portrait banner (768×1152 px, 2:3 ratio). "
            "Vertical format requiring a natural, unbroken vertical visual flow."
        ),
        ratio_str="2:3",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 768×1152 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered vertically or following the rule of thirds). Extend the background environment vertically without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilize the 2:3 height by positioning the photo/hero as a visual anchor and distributing text elements in the adjacent clear vertical space (above and/or below). Do NOT cluster elements tightly."
        ),
        fill_direction="vertically",
        fill_description=(
            "Fill any remaining vertical space with a seamless background or scene environment extension. "
            "Maintain the natural perspective, lighting, and continuous flow of the original image. "
            "Strictly NO duplication of primary subjects, unique objects, or foreground elements to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any original component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Human person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "Only render components detected in the source image — skip any element type not present.",
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 768x1152 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner height. Position the main visual (subject/product) as a central or offset anchor, with text and logos placed in complementary clear zones (top or bottom).",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain strictly within x: 0–768 px.",
            "Minimum 24 px vertical padding between distinct advertising elements and canvas edges."
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects vertically to fill the 2:3 height; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT place ad elements side by side if they require full width; utilize the vertical stack organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended vertical background is completely seamless.",
            "Output must be exactly 768 px wide × 1152 px tall."
        ],
    ),
}


# ── Lookup helper ──────────────────────────────────────────────────────────────

def get_profile(target_w: int, target_h: int) -> DimProfile:
    """
    Return the DimProfile for the given dimensions.
    Falls back to a generic landscape or portrait profile if the exact
    dimension is not in the dictionary.
    """
    profile = OOH_PROFILES.get((target_w, target_h))
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
            f"Photo left zone, text/logos right zone",
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
