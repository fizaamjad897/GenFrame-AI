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
            "a thin, wide horizontal strip banner (792×216 px, ~3.7:1 ratio). "
            "The canvas is 216 px tall — extremely limited vertical space."
        ),
        ratio_str="3.7:1",
        orientation="landscape_extreme",
        layout_direction="left-to-right",
        arrangement_order=["background", "logo", "photo", "headline", "body_text", "cta"],
        element_max_height=0.85,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Empty horizontal space must be seamlessly filled with the background — "
            "solid color or gradient extension only, no new imagery."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 792×216 canvas",
            "Arrange left-to-right: logo → photo → headline → body text → CTA",
            "ALL elements must fit within y: 0–216 px (hard limit)",
            "Primary text: max 140 px tall. Secondary text: max 70 px",
            "12 px horizontal padding between elements",
            "Center all elements vertically: y = (216 - element_height) / 2",
            "NO vertical stacking — single horizontal row only",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT make any element taller than 216 px",
            "DO NOT stack elements vertically",
            "DO NOT show full-body photos — head/shoulders crop only",
            "DO NOT output a portrait or square image",
        ],
    ),

    # ── 1344 × 432 ── AR 3.1:1  WIDE BILLBOARD ───────────────────────────────
    (1344, 432): DimProfile(
        label="Wide billboard (1344×432)",
        canvas_description=(
            "a wide horizontal billboard banner (1344×432 px, ~3:1 ratio). "
            "This is a classic outdoor billboard format with decent height."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "logo", "headline", "body_text", "cta", "qr", "fine_print"],
        element_max_height=0.90,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Empty horizontal space must be filled by extending the background seamlessly — "
            "match the existing solid color, gradient, or texture. Never add buildings, sky, or new scene content."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 1344×432 canvas",
            "Photo/hero image: place on LEFT side (x: 0–500 px range)",
            "Brand logo: top-left or top-right corner",
            "Headline and body text: center or right zone (x: 450–1200 px)",
            "CTA and QR code: right zone (x: 1000–1300 px)",
            "Fine print: bottom-right, full width, ~32 px tall",
            "ALL elements must fit within y: 0–432 px",
            "20 px horizontal padding between elements",
            "Center elements vertically unless design suggests top/bottom alignment",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT center the photo in the middle and leave both sides empty",
            "DO NOT stack all text vertically like a portrait ad",
            "DO NOT extend the photo scene (building, sky) into the empty space — background fill only",
            "DO NOT output a portrait or square image — must be 1344 px wide × 432 px tall",
        ],
    ),

    # ── 1836 × 432 ── AR 4.25:1  SUPER WIDE BILLBOARD ────────────────────────
    (1836, 432): DimProfile(
        label="Super wide billboard (1836×432)",
        canvas_description=(
            "a super-wide horizontal billboard banner (1836×432 px, ~4.25:1 ratio). "
            "Much wider than tall — significant background extension needed on the sides."
        ),
        ratio_str="4.25:1",
        orientation="landscape_wide",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "logo", "headline", "body_text", "cta", "qr", "fine_print"],
        element_max_height=0.90,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Large horizontal areas on left and/or right must be filled with the background color/gradient — "
            "seamless extension, no new scene content, no duplicated elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 1836×432 canvas",
            "Photo/hero: left zone (x: 0–550 px). Do NOT center it",
            "Brand logo: immediately right of photo or top-left corner",
            "Headline: center zone (x: 500–1200 px)",
            "Body text: center-right (x: 600–1400 px)",
            "CTA + QR: right zone (x: 1400–1800 px)",
            "Fine print: bottom strip, full width, ~32 px tall",
            "24 px horizontal padding between major elements",
            "ALL elements within y: 0–432 px",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT cluster all elements in the center — spread them across the 1836 px width",
            "DO NOT extend the photo scene into empty zones — background fill only",
            "DO NOT duplicate the photo or any person to fill space",
            "Output must be exactly 1836×432 px — not square, not portrait",
        ],
    ),

    # ── 1060 × 360 ── AR 2.94:1  WIDE BILLBOARD ──────────────────────────────
    (1060, 360): DimProfile(
        label="Wide billboard (1060×360)",
        canvas_description=(
            "a wide horizontal billboard banner (1060×360 px, ~3:1 ratio)."
        ),
        ratio_str="3:1",
        orientation="landscape_wide",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "logo", "headline", "body_text", "cta", "fine_print"],
        element_max_height=0.90,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Fill empty horizontal space with background extension only — no new scene content."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 1060×360 canvas",
            "Photo/hero on left (x: 0–400 px), text/logos on right (x: 380–1020 px)",
            "Fine print: bottom strip across full width, ~30 px tall",
            "ALL elements within y: 0–360 px",
            "18 px horizontal padding between elements",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT stack elements vertically like a portrait layout",
            "DO NOT extend photo scene — background color/gradient only",
            "Output must be 1060 px wide × 360 px tall",
        ],
    ),

    # ── 1280 × 384 ── AR 3.33:1  WIDE STRIP BILLBOARD ────────────────────────
    (1280, 384): DimProfile(
        label="Wide strip billboard (1280×384)",
        canvas_description=(
            "a wide horizontal strip billboard banner (1280×384 px, ~3.3:1 ratio)."
        ),
        ratio_str="3.3:1",
        orientation="landscape_wide",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "logo", "headline", "body_text", "cta", "fine_print"],
        element_max_height=0.90,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Empty horizontal space filled with seamless background extension only."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 1280×384 canvas",
            "Photo left (x: 0–450 px), content right (x: 430–1240 px)",
            "Fine print: bottom strip, full width, ~30 px tall",
            "ALL elements within y: 0–384 px",
            "18 px horizontal padding between elements",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT make elements taller than 384 px",
            "DO NOT use a vertical/portrait layout",
            "Background extension only for empty space — no new scene content",
        ],
    ),

    # ── 1024 × 320 ── AR 3.2:1  WIDE STRIP ───────────────────────────────────
    (1024, 320): DimProfile(
        label="Wide strip (1024×320)",
        canvas_description=(
            "a wide horizontal strip banner (1024×320 px, ~3.2:1 ratio). "
            "Limited vertical space — 320 px tall."
        ),
        ratio_str="3.2:1",
        orientation="landscape_wide",
        layout_direction="left-to-right",
        arrangement_order=["background", "logo", "photo", "headline", "body_text", "cta"],
        element_max_height=0.88,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Fill empty horizontal zones with background color/gradient — no new imagery."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 1024×320 canvas",
            "Single horizontal row: logo → photo → headline → body text → CTA",
            "ALL elements within y: 0–320 px",
            "16 px horizontal padding between elements",
            "Center elements vertically: y = (320 - element_height) / 2",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT make elements taller than 320 px",
            "DO NOT stack elements — single horizontal row only",
            "DO NOT show full-body photos in 320 px height — crop to torso/head",
        ],
    ),

    # ── 3924 × 972 ── AR 4.04:1  LARGE WIDE BILLBOARD ───────────────────────
    (3924, 972): DimProfile(
        label="Large wide billboard (3924×972)",
        canvas_description=(
            "a very large wide horizontal billboard banner (3924×972 px, ~4:1 ratio). "
            "High resolution with generous height — full-body photos fit well."
        ),
        ratio_str="4:1",
        orientation="landscape_wide",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "logo", "headline", "body_text", "cta", "qr", "fine_print"],
        element_max_height=0.92,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Large horizontal zones must be filled with seamless background extension — "
            "match the existing palette. No new scene content, no duplicated foreground elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 3924×972 canvas",
            "Photo/hero: left zone (x: 0–1200 px), can be full-body at this height",
            "Brand logo: top-left area",
            "Headline: center zone (x: 1100–2600 px)",
            "Body text: center-right (x: 1200–2800 px)",
            "CTA + QR: right zone (x: 2800–3800 px)",
            "Fine print: bottom strip, full width, ~70 px tall",
            "30 px horizontal padding between major elements",
            "ALL elements within y: 0–972 px",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT cluster all content in a small central zone — use the full 3924 px width",
            "DO NOT duplicate any element to fill the wide canvas",
            "DO NOT extend the photo background scene — fill with brand background only",
        ],
    ),

    # ── 840 × 360 ── AR 2.33:1  MODERATE WIDE ────────────────────────────────
    (840, 360): DimProfile(
        label="Moderate wide banner (840×360)",
        canvas_description=(
            "a moderate-width horizontal banner (840×360 px, ~2.3:1 ratio). "
            "Balanced proportions — not extremely wide, not square."
        ),
        ratio_str="2.3:1",
        orientation="landscape_moderate",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "logo", "headline", "body_text", "cta"],
        element_max_height=0.90,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Fill remaining horizontal space with background color/gradient — seamless, no new content."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "EVERY component must appear — none omitted",
            "The background component fills the entire 840×360 canvas",
            "Photo left (x: 0–350 px), text/logo right (x: 320–800 px)",
            "ALL elements within y: 0–360 px",
            "16 px horizontal padding between elements",
            "Photo/person: ZERO artistic reinterpretation — render exactly as provided. "
            "Same face, body, clothing, skin tone, and pose. DO NOT regenerate or hallucinate any human.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — pixel-perfect copy from reference only.",
            "DO NOT change skin tone, facial features, clothing, body proportions, or pose of any person.",
            "DO NOT make elements taller than 360 px",
            "DO NOT use a portrait/vertical layout",
            "Background extension for empty space only",
        ],
    ),

    # ── 1232 × 672 ── AR 1.83:1  MODERATE LANDSCAPE ──────────────────────────
    (1232, 672): DimProfile(
        label="Moderate landscape banner (1232×672)",
        canvas_description=(
            "a moderate landscape banner (1232×672 px, ~1.8:1 ratio). "
            "Generous height — similar proportions to a widescreen display."
        ),
        ratio_str="1.8:1",
        orientation="landscape_moderate",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "headline", "body_text", "logo", "cta", "qr", "fine_print"],
        element_max_height=0.92,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Fill any remaining horizontal space with the background — "
            "solid color, gradient, or texture extension only."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "EVERY component must appear — none omitted",
            "The background component fills the entire 1232×672 canvas",
            "Photo: left half (x: 0–600 px) — maintain original proportions perfectly, "
            "DO NOT regenerate, reimagine, or alter any human body structure, face, or clothing",
            "Headline and body text: right half (x: 580–1180 px)",
            "Logo: top-right corner or above headline",
            "CTA + QR: bottom-right zone",
            "Fine print: bottom strip, full width, ~44 px tall",
            "ALL elements within y: 0–672 px",
            "20 px padding between elements",
            "Photo/person: ZERO tolerance for alteration — same face, body, clothing, skin tone, and pose as the reference.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — exact pixel-level copy from the reference only.",
            "DO NOT change skin tone, facial features, clothing, body proportions, or pose of any person.",
            "DO NOT stack all elements centrally and leave sides empty",
            "DO NOT use a portrait layout (top-to-bottom stack)",
            "Background extension only — no new photographic scenes",
        ],
    ),

    # ── 1952 × 896 ── AR 2.18:1  WIDE LANDSCAPE ──────────────────────────────
    (1952, 896): DimProfile(
        label="Wide landscape banner (1952×896)",
        canvas_description=(
            "a wide landscape banner (1952×896 px, ~2.2:1 ratio). "
            "Large format with significant width and good height."
        ),
        ratio_str="2.2:1",
        orientation="landscape_moderate",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "headline", "body_text", "logo", "cta", "qr", "fine_print"],
        element_max_height=0.93,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Fill extra horizontal space with seamless background extension — "
            "no new scene content, no duplicates."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 1952×896 canvas",
            "Photo: left zone (x: 0–800 px) — full body possible",
            "Headline + body: center zone (x: 750–1600 px)",
            "Logo: top area, aligned with brand side",
            "CTA + QR: right zone (x: 1550–1900 px)",
            "Fine print: bottom strip full width, ~55 px tall",
            "ALL elements within y: 0–896 px",
            "24 px horizontal padding between elements",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT cluster content in the center — spread across the 1952 px width",
            "DO NOT duplicate any element to fill horizontal space",
            "Background fill only for empty zones",
        ],
    ),

    # ── 960 × 576 ── AR 1.67:1  NEAR 16:9 ────────────────────────────────────
    (960, 576): DimProfile(
        label="Near 16:9 banner (960×576)",
        canvas_description=(
            "a near-widescreen banner (960×576 px, ~1.67:1 / close to 16:9 ratio). "
            "Balanced, screen-like proportions."
        ),
        ratio_str="1.67:1",
        orientation="landscape_moderate",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "headline", "body_text", "logo", "cta", "fine_print"],
        element_max_height=0.92,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Fill empty horizontal space with background color/gradient extension only."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 960×576 canvas",
            "Photo: left half (x: 0–480 px)",
            "Text and logo: right half (x: 440–920 px)",
            "Fine print: bottom strip full width, ~36 px tall",
            "ALL elements within y: 0–576 px",
            "18 px padding between elements",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT use a portrait layout",
            "Background extension only for empty space",
        ],
    ),

    # ── 800 × 400 ── AR 2:1  STANDARD LANDSCAPE ──────────────────────────────
    (800, 400): DimProfile(
        label="Standard 2:1 banner (800×400)",
        canvas_description=(
            "a standard landscape banner (800×400 px, 2:1 ratio)."
        ),
        ratio_str="2:1",
        orientation="landscape_moderate",
        layout_direction="left-to-right",
        arrangement_order=["background", "photo", "headline", "body_text", "logo", "cta"],
        element_max_height=0.90,
        element_guidance=(
            "The exact output image generated MUST be the 2072×252 banner itself. "
            "Fill the 2072×252 pixel space completely, edge-to-edge. "
            "SCALE ALL COMPONENTS LARGER. Spread them across the ENTIRE 2072 pixel width, touching the far left and right edges. "
            "CRITICAL: The background MUST paint the outer edges of the 2072×252 canvas. "
            "Photos/persons: pull them so large they are 220–252 px tall, filling the height of the banner. "
            "Headlines: scale up to 140–200 px tall. Body text: 60–90 px tall. "
            "Do NOT cluster elements in the middle. Spread them horizontally."),
        fill_direction="horizontally",
        fill_description=(
            "Fill remaining space with background extension — solid color or gradient only."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.",
            "EVERY component must appear — none omitted",
            "The background component fills the entire 800×400 canvas",
            "Photo: left side (x: 0–380 px). Text: right side (x: 360–760 px)",
            "ALL elements within y: 0–400 px",
            "16 px horizontal padding",
            "Photo/person: ZERO artistic reinterpretation — render exactly as provided. "
            "Same face, body, clothing, skin tone, and pose. DO NOT regenerate or hallucinate any human.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "CRITICAL: DO NOT redraw, reimagine, or regenerate any human person — pixel-perfect copy from reference only.",
            "DO NOT change skin tone, facial features, clothing, body proportions, or pose of any person.",
            "DO NOT use a portrait/vertical layout",
            "Background fill only for empty space",
        ],
    ),

    # ── 504 × 1008 ── AR 1:2  TALL PORTRAIT ──────────────────────────────────
   (800, 400): DimProfile(
    label="Tall portrait banner (504×1008)",
    canvas_description="A vertical portrait canvas (504×1008 px, 1:2 ratio) requiring a strict letterbox layout.",
    ratio_str="1:2",
    orientation="portrait_tall",
    layout_direction="top-to-bottom",
    arrangement_order=["background", "logo", "headline", "photo", "body_text", "cta", "fine_print"],
    element_max_height=1.0, 
    element_guidance=(
        "ABSOLUTE PRIORITY: Single instance presentation. "
        "Place the untouched original photo exactly ONCE in the vertical center of the canvas. "
        "The top 30% and bottom 30% of the canvas MUST be flat, solid color blocks (e.g., solid white or beige). "
        "Photographic elements (sky, grass, trees) must absolutely STOP at the top and bottom borders of the central photo. "
        "They must not bleed into or fill the top and bottom sections."
    ),
    fill_direction="vertically",
    fill_description=(
        "Use a flat, solid color block for the areas above and below the photo. "
        "NEVER use photographic textures, sky, or grass to fill the vertical space."
    ),
    layout_rules=[
        "Rule 1: SINGLE INSTANCE ONLY. The photo appears exactly one time. No stacking, no tiling, no copying.",
        "Rule 2: PIXEL-PERFECT ORIGINAL. Keep the original central image 100% untouched.",
        "Rule 3: Establish flat, solid color blocks for the top and bottom background areas.",
        "Rule 4: Place the logo, headline, body text, and CTA strictly within the solid color areas, not over the photo."
    ],
    dimension_warnings=[
        "CRITICAL: Do NOT stack, tile, mirror, or duplicate the photo to fill space. It must appear only ONE time.",
        "CRITICAL: The top and bottom sections of the canvas must be solid color blocks, completely devoid of any scenery."
    ],
),

    # ── 768 × 1152 ── AR 1:1.5  PORTRAIT ─────────────────────────────────────
    (768, 1152): DimProfile(
        label="Portrait banner (768×1152)",
        canvas_description=(
            "a portrait banner (768×1152 px, 2:3 ratio). "
            "Vertical format — content stacks top-to-bottom."
        ),
        ratio_str="2:3",
        orientation="portrait_moderate",
        layout_direction="top-to-bottom",
        arrangement_order=["background", "logo", "headline", "photo", "body_text", "cta", "fine_print"],
        element_max_height=0.50,
        element_guidance=(
            "Scale components to fit within 768 px width. "
            "Photo: 500–700 px tall (portrait crop). Logo: 80–120 px. "
            "Headline: 100–200 px. Body text: 70–120 px. Fine print: 36–48 px."
        ),
        fill_direction="vertically",
        fill_description=(
            "Empty vertical space must be filled with background color/gradient extension — "
            "no new imagery, no duplicated elements."
        ),
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            "The background component fills the entire 768×1152 canvas",
            "Arrange TOP-TO-BOTTOM: logo → headline → photo → body text → CTA → fine print",
            "ALL elements must fit within x: 0–768 px",
            "Logo: top-center, 20 px top margin",
            "Photo: centered in middle zone (y: 250–800 px)",
            "Text: above and below photo",
            "Fine print: bottom strip, ~42 px tall",
            "24 px vertical padding between stacked elements",
            "Center all elements horizontally: x = (768 - element_width) / 2",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
            "DO NOT use a horizontal/landscape layout — this is a portrait format",
            "DO NOT place elements side by side",
            "DO NOT extend photo scene vertically — background fill only",
            "Output must be 768 px wide × 1152 px tall",
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
        arrangement_order=["background", "logo", "photo", "headline", "body_text", "cta", "fine_print"],
        element_max_height=0.85,
        element_guidance=f"Scale all components to fit within {h} px height. Photos: head/torso crop only.",
        fill_direction="horizontally",
        fill_description="Fill empty horizontal space with background extension only — no new scene content.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            f"The background component fills the entire {w}×{h} canvas",
            "Single horizontal row: left-to-right arrangement",
            f"ALL elements within y: 0–{h} px",
            "16 px horizontal padding between elements",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
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
        arrangement_order=["background", "photo", "logo", "headline", "body_text", "cta", "fine_print"],
        element_max_height=0.90,
        element_guidance=f"Scale all components to fit within {h} px height.",
        fill_direction="horizontally",
        fill_description="Fill empty horizontal space with background extension — no new imagery.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            f"The background component fills the entire {w}×{h} canvas",
            f"Photo left zone, text/logos right zone",
            f"ALL elements within y: 0–{h} px",
            "20 px horizontal padding",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
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
        arrangement_order=["background", "photo", "headline", "body_text", "logo", "cta"],
        element_max_height=0.90,
        element_guidance=f"Scale all components to fit within {h} px height.",
        fill_direction="horizontally",
        fill_description="Fill remaining horizontal space with background extension only.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
            f"The background component fills the entire {w}×{h} canvas",
            "Photo left, text right",
            f"ALL elements within y: 0–{h} px",
            "18 px horizontal padding",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT alter, redraw, or reinvent ANY component.",
            "CRITICAL: Human faces, bodies, and clothing MUST remain 100% pixel-perfect identical to the reference.",
            "CRITICAL: DO NOT duplicate any component (humans, products, text, or logos).",
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
        arrangement_order=["background", "logo", "headline", "photo", "body_text", "cta", "fine_print"],
        element_max_height=0.45,
        element_guidance=f"Scale all components to fit within {w} px width. Stack elements top-to-bottom.",
        fill_direction="vertically",
        fill_description="Fill empty vertical space with background extension only — no new imagery.",
        layout_rules=[
            "CRITICAL: Never change, redraw, or reimagine any component.",
            "CRITICAL: Human images must stay exactly as they are without any modifications.",
            "CRITICAL: Every single component must appear exactly once — zero duplication.", 
            "EVERY component must appear — none omitted",
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
            "DO NOT use a horizontal layout — this is a portrait format",
            "DO NOT place elements side by side",
            f"Output must be {w} px wide × {h} px tall — NOT landscape",
        ],
    )
