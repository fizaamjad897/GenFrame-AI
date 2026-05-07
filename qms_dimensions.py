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
            "Severely limited vertical space — every pixel of height is precious. "
            "Requires a single, seamless, unbroken horizontal visual flow across the full width."
        ),
        ratio_str="9.2:1",
        orientation="landscape_extreme",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 2640×288 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilise the massive 9.2:1 width by positioning the photo/hero as a compact visual anchor "
            "(head/torso crop only — 288 px height forces this) and distributing text and logo elements across the remaining horizontal clear space. "
            "DO NOT cluster elements in the centre. Spread across the full 2640 px width."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 2640x288 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the full 2640 px width in a single horizontal row. Place the hero/photo on one side and spread text, logos, and CTAs across the remaining clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–288 px (hard limit).",
            "Minimum 12 px padding between distinct advertising elements and canvas edges.",
            "NO vertical stacking — single horizontal row only.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the massive 9.2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; the 288 px height demands a single horizontal row of elements.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
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
            "FOR ADVERTISING IMAGES: Utilise the 4:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "intelligently across the remaining horizontal space. Photos/persons can be full-body at this height. Do NOT cluster elements in the middle."
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
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the 4:1 width. Place the photo/hero in a left or right anchor zone. Place text/headlines adjacent to the subject. Place CTA in the opposing zone.",
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
            "DO NOT cluster all content in a small central zone; utilise the full 1728 px width organically.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended horizontal background is completely seamless.",
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
            "FOR ADVERTISING IMAGES: Utilise the 4:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
            "intelligently across the remaining space. Do NOT cluster elements in the middle — spread across the full 1440 px width."
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
    (760, 240): DimProfile(
        label="Wide strip (760×240)",
        canvas_description=(
            "a wide horizontal strip banner (760×240 px, ~3.2:1 ratio). "
            "Compact wide format with limited vertical space requiring a natural, unbroken horizontal visual flow."
        ),
        ratio_str="3.2:1",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.95,
        element_guidance=(
            "Fill the 760×240 pixel space completely, edge-to-edge. "
            "CRITICAL: The background or scene environment MUST paint the outer edges of the canvas seamlessly. "
            "FOR GENERIC/NORMAL IMAGES: Place the main subject/scene organically (e.g., centered or following the rule of thirds). "
            "Extend the background environment horizontally without stretching the subject or breaking the visual flow. No invented text or logos. "
            "FOR ADVERTISING IMAGES: Utilise the 3.2:1 width by positioning the photo/hero as a compact visual anchor "
            "(head/torso crop works well at 240 px height) and distributing text and logo elements in the adjacent or opposing clear space. "
            "Do NOT cluster elements in the middle."
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
            "LAYOUT FOR GENERIC IMAGES (No text/logos): Position the main subject organically within the frame. Extend the background/environment seamlessly to fill the 760x240 canvas without stretching the subject or creating visible seams.",
            "LAYOUT FOR ADVERTISING IMAGES (Contains text/logos): Distribute elements intelligently across the banner width in a single horizontal flow. Position the main visual (subject/product) on one side, with text and logos in complementary clear zones.",
            "ALL elements must maintain their original aspect ratios.",
            "ALL elements must remain within y: 0–240 px (hard limit).",
            "Minimum 12 px padding between distinct advertising elements and canvas edges.",
            "NO vertical stacking — horizontal distribution only.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT stretch primary subjects to fill the 3.2:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT stack elements vertically; use the limited 240 px height for a single horizontal row.",
            "DO NOT break the image flow: ensure the transition between the main subject and the extended background is completely seamless.",
            "Output must be exactly 760×240 px — not square, not portrait.",
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
            "FOR ADVERTISING IMAGES: Utilise the 3.1:1 width by positioning the photo/hero as a visual anchor and distributing text elements "
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
            "DO NOT stretch primary subjects to fill the 3.1:1 width; only extend the background/environment.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "DO NOT cluster content in the centre — spread organically across the full 1184 px width.",
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
            "FOR ADVERTISING IMAGES: Use the 3:1 width by placing the photo/hero as a strong anchor and distributing text, logos and CTA across the remaining horizontal space."
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
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY core component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos) to fill empty space.",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
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
            "FOR ADVERTISING IMAGES: Use the 3:1 width by placing the photo/hero in an anchor zone and distributing text and logos in the remaining horizontal space."
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
            "FOR ADVERTISING IMAGES: Use the 3:1 width by placing the hero/photo as a compact anchor and distributing text and logos along the remaining width."
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
            "FOR ADVERTISING IMAGES: Use the 3:1 width by positioning the hero/photo as a compact anchor and distributing text and logo elements in the horizontal clear space."
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
            "FOR ADVERTISING IMAGES: Use the 3:1 width by positioning the hero/photo as a compact anchor and distributing text and logo elements across the remaining horizontal space."
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
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing photo/hero in a strong anchor zone and distributing text and logos across the remaining canvas."
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
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing the photo/hero in a strong anchor zone and distributing text and logo elements across the remaining width."
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
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing photo/hero on one side and distributing text and logo elements across the remaining horizontal space."
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
            "FOR ADVERTISING IMAGES: Use the 2:1 width by placing the hero/photo as a compact anchor and distributing text and logo elements across the remaining horizontal space."
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
            "FOR GENERIC IMAGES: Place the main subject/scene naturally in a vertical composition, no invented text or logos."
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
            "FOR GENERIC IMAGES: Place the main subject/scene naturally in a vertical composition, no invented text or logos."
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
            "DO NOT use a horizontal layout — this is a portrait format.",
            "DO NOT place elements side by side.",
            "DO NOT invent or hallucinate advertising elements (logos, headlines, CTAs, body text) that do not exist in the source image.",
            "Output must be exactly 704×1408 px — NOT landscape.",
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
