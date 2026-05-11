"""
standard_dimensions.py — Layout profiles for standard /api/resize creation targets.

These dimensions correspond to CREATION_ALLOWED_ASPECT_RATIOS and
CREATION_ALLOWED_PRESET_NAMES in main.py (16:9, 9:16, 1:1, 3:4, 21:9 and
landscape / story / square / portrait / ultrawide), including both:
  • Gemini native resolutions when a ratio string maps with target_dims=None
  • Explicit pixel presets from validate_aspect_ratio() named_presets

Profiles follow the same DimProfile structure as ooh_dimensions.py and
qms_dimensions.py and are consumed by gemini_decomposition/banner_recomposer.py.
"""

from __future__ import annotations
from typing import FrozenSet, List, Optional, TypedDict


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


def _std_landscape_16_9(w: int, h: int) -> DimProfile:
    return DimProfile(
        label=f"Standard 16:9 ({w}×{h})",
        canvas_description=(
            f"a standard 16:9 widescreen canvas ({w}×{h} px). "
            "Typical for landscape video, horizontal feeds, and display creatives."
        ),
        ratio_str="16:9",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.92,
        element_guidance=(
            f"Fill the {w}×{h} pixel canvas edge-to-edge. "
            "The background or scene must reach all four edges seamlessly. "
            "FOR ADVERTISING: anchor photo or product on one side; place headline, "
            "supporting text, and logo in clear adjacent zones — do not stack duplicates. "
            "FOR GENERIC IMAGES: compose the subject with rule-of-thirds; extend environment "
            "horizontally without stretching the subject. "
            "Treat person crops like a LOGO — paste exactly; do not regenerate faces."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Extend background or scene horizontally into any empty margin. "
            "NO duplication of people, logos, or products to fill space."
        ),
        layout_rules=[
            "CRITICAL: Never redraw or reimagine any supplied component.",
            "CRITICAL: Humans — same face, skin tone, clothing, pose as the reference crop.",
            "CRITICAL: Each logo, text block, and product appears exactly once.",
            "Only use components present in the source decomposition.",
            f"All content within 0≤x≤{w}, 0≤y≤{h}; maintain original aspect ratios.",
            "Minimum 16 px padding from edges between distinct ad elements.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT duplicate subjects or text to pad the 16:9 frame.",
            "CRITICAL: DO NOT regenerate or beautify human faces — pixel-faithful paste only.",
            "DO NOT invent logos, headlines, or CTAs not in the source.",
            f"Output must be exactly {w}×{h} px — not portrait, not square.",
        ],
    )


def _std_portrait_9_16(w: int, h: int) -> DimProfile:
    return DimProfile(
        label=f"Standard 9:16 ({w}×{h})",
        canvas_description=(
            f"a standard 9:16 portrait / story canvas ({w}×{h} px). "
            "Vertical mobile and full-screen story format."
        ),
        ratio_str="9:16",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.48,
        element_guidance=(
            f"Fill the {w}×{h} pixel canvas edge-to-edge. "
            "FOR ADVERTISING: top-to-bottom flow — logo/headline upper, hero mid, "
            "body and CTA lower; centre blocks horizontally where appropriate. "
            "FOR GENERIC IMAGES: vertical composition with seamless background extension. "
            "⚠ PORTRAIT-TO-PORTRAIT: if source is already tall, assemble crops — do not "
            "regenerate the whole scene. Person = sealed sticker; paste unchanged."
        ),
        fill_direction="vertically",
        fill_description=(
            "Extend background vertically; never clone the hero or logo to fill height."
        ),
        layout_rules=[
            "CRITICAL: Never redraw or reimagine any supplied component.",
            "CRITICAL: Humans — identical face and pose to the reference.",
            "CRITICAL: Each component exactly once; vertical stack, not side-by-side columns.",
            f"All content within x: 0–{w} px; use vertical bands for hierarchy.",
            "24–40 px vertical gap between stacked elements where space allows.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT use a wide horizontal strip layout on this portrait canvas.",
            "CRITICAL: DO NOT duplicate the person or product vertically.",
            "CRITICAL: DO NOT regenerate the ad — composite provided crops.",
            f"Output must be exactly {w}×{h} px — NOT landscape.",
        ],
    )


def _std_square(w: int, h: int) -> DimProfile:
    return DimProfile(
        label=f"Standard 1:1 ({w}×{h})",
        canvas_description=(
            f"a square 1:1 canvas ({w}×{h} px). "
            "Balanced social and display format."
        ),
        ratio_str="1:1",
        orientation="landscape_moderate",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.88,
        element_guidance=(
            f"Fill the {w}×{h} square completely. "
            "Centre-weight or slightly offset the hero; distribute text and logo "
            "without crowding the focal subject. "
            "Extend background in all directions as needed — no mirrored duplicates."
        ),
        fill_direction="horizontally and vertically",
        fill_description=(
            "Pad with seamless background or scene continuation on all sides as needed; "
            "no duplicated foreground objects."
        ),
        layout_rules=[
            "CRITICAL: Preserve every supplied component; no redraws.",
            "CRITICAL: Humans unchanged from reference crops.",
            "CRITICAL: Single instance of each logo, person, and text block.",
            f"Respect the square bounds 0…{w} × 0…{h} px.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT letterbox with empty colour bars unless the source already had them.",
            "CRITICAL: DO NOT duplicate the subject left/right to fake symmetry.",
            f"Output must be exactly {w}×{h} px square.",
        ],
    )


def _std_portrait_3_4(w: int, h: int) -> DimProfile:
    return DimProfile(
        label=f"Standard 3:4 ({w}×{h})",
        canvas_description=(
            f"a 3:4 portrait canvas ({w}×{h} px). "
            "Classic vertical print and feed proportion."
        ),
        ratio_str="3:4",
        orientation="portrait_moderate",
        layout_direction="vertical_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.50,
        element_guidance=(
            f"Fill the {w}×{h} pixel canvas. "
            "Vertical hierarchy: headline zone → hero → supporting copy. "
            "⚠ RATIO TRAP: 3:4 can resemble a tall photo — still composite layers; "
            "do not rescale the entire source as a flat stretch. "
            "Person crops pasted as discrete assets."
        ),
        fill_direction="vertically",
        fill_description=(
            "Grow background vertically; keep a single hero instance."
        ),
        layout_rules=[
            "CRITICAL: No regeneration of faces or logos.",
            "CRITICAL: One copy of each detected element.",
            f"Content within x: 0–{w}, y: 0–{h}; maintain aspect ratios.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT treat this as a free-form regenerate — assemble components.",
            "DO NOT add invented furniture or scenery behind cut-out people.",
            f"Output must be exactly {w}×{h} px.",
        ],
    )


def _std_ultrawide_21_9(w: int, h: int) -> DimProfile:
    return DimProfile(
        label=f"Standard 21:9 ({w}×{h})",
        canvas_description=(
            f"a 21:9 ultrawide canvas ({w}×{h} px). "
            "Cinematic horizontal format — use full width with a single horizontal story."
        ),
        ratio_str="21:9",
        orientation="landscape_wide",
        layout_direction="horizontal_flow",
        arrangement_order=["background", "scene", "subject", "photo", "graphic", "text"],
        element_max_height=0.94,
        element_guidance=(
            f"Fill the {w}×{h} ultrawide frame edge-to-edge. "
            "Spread elements across the full width — avoid a tight cluster in the centre. "
            "Photo anchor left or right; headline and CTA occupy complementary horizontal zones. "
            "Extend panorama-style background only — no cloned subjects."
        ),
        fill_direction="horizontally",
        fill_description=(
            "Continue environment horizontally across empty zones; "
            "strictly no duplicate people or logos."
        ),
        layout_rules=[
            "CRITICAL: Use the full width — thin side margins only for breathing room.",
            "CRITICAL: Horizontal reading order; not a vertical stack.",
            "CRITICAL: Preserve all components from decomposition verbatim.",
            f"All pixels active within {w}×{h}; y-limits respected.",
        ],
        dimension_warnings=[
            "CRITICAL: DO NOT leave large empty gutters on both sides.",
            "CRITICAL: DO NOT vertically stack all text in the centre column.",
            "CRITICAL: DO NOT stretch faces to span width — extend background only.",
            f"Output must be exactly {w}×{h} px.",
        ],
    )


STANDARD_PROFILES: dict[tuple[int, int], DimProfile] = {
    # Direct Gemini ratio strings → GEMINI_NATIVE_RESOLUTIONS
    (1344, 768): _std_landscape_16_9(1344, 768),
    (768, 1344): _std_portrait_9_16(768, 1344),
    (1024, 1024): _std_square(1024, 1024),
    (896, 1152): _std_portrait_3_4(896, 1152),
    (1536, 640): _std_ultrawide_21_9(1536, 640),
    # Named presets from validate_aspect_ratio()
    (1920, 1080): _std_landscape_16_9(1920, 1080),
    (1080, 1920): _std_portrait_9_16(1080, 1920),
    (768, 1024): _std_portrait_3_4(768, 1024),
    (2560, 1080): _std_ultrawide_21_9(2560, 1080),
}

STANDARD_PIPELINE_TARGETS: FrozenSet[tuple[int, int]] = frozenset(STANDARD_PROFILES.keys())


def is_standard_pipeline_target(target_w: int, target_h: int) -> bool:
    """True when (target_w, target_h) should use ooh_pipeline + standard DimProfile."""
    return (target_w, target_h) in STANDARD_PIPELINE_TARGETS


def get_profile(target_w: int, target_h: int) -> Optional[DimProfile]:
    """Return the standard profile for exact dimensions, or None if not a standard target."""
    return STANDARD_PROFILES.get((target_w, target_h))
