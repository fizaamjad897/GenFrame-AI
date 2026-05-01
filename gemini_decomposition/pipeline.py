"""
pipeline.py — Unified image decomposition pipeline using Recreative AI APIs.

Chains: Image → Analyse → Isolate PNGs → Generate SVGs → Assemble Template4 JSON.

Uses Vertex AI wrapper for text/image analysis and FAL AI for image generation.

Usage:
    from gemini_decomposition.pipeline import decompose_image

    template = await decompose_image("https://example.com/flyer.png")
    # or
    template = await decompose_image("/path/to/image.png")
    # or
    template = await decompose_image(raw_png_bytes)
"""

import os
import io
import json
import time
import asyncio
import logging
from pathlib import Path
from datetime import datetime

from PIL import Image
from dotenv import load_dotenv

load_dotenv()
# Also try package-local .env (gemini_decomposition/.env)
load_dotenv(Path(__file__).parent / ".env")

logger = logging.getLogger("pipeline")

OUTPUT_BASE = Path(__file__).parent / "output"


def _safe_filename(desc: str) -> str:
    """Sanitise a component description for use in filenames."""
    safe = "".join(
        c if c.isalnum() or c in " _-" else ""
        for c in desc[:40]
    ).strip().replace(" ", "_")
    return safe


async def decompose_image(
    image_source: str | bytes,
    parallel: bool = True,
    output_dir: str | None = None,
) -> dict:
    """
    Full pipeline: image → isolate components → assemble Template4 JSON.

    Args:
        image_source: URL (http/https), local file path, or raw image bytes.
        parallel: Run PNG isolations concurrently (faster, may hit rate limits).
        output_dir: Directory for intermediate files. Auto-created if None.

    Returns:
        Template4 JSON dict ready for the canvas editor.
    """
    from gemini_isolate import (
        analyze_components,
        isolate_component_png,
        # generate_svg,   # SVG generation disabled
        # SVG_TYPES,      # SVG generation disabled
    )
    from gemini_assembler import assemble_template

    # ── 1. Load image ─────────────────────────────────────────────────────────
    if isinstance(image_source, bytes):
        image = Image.open(io.BytesIO(image_source)).convert("RGB")
        logger.info(f"Loaded image from bytes: {image.width}x{image.height}")
    elif isinstance(image_source, str) and image_source.startswith(("http://", "https://")):
        import httpx
        async with httpx.AsyncClient(timeout=60) as hc:
            r = await hc.get(image_source)
            r.raise_for_status()
            image = Image.open(io.BytesIO(r.content)).convert("RGB")
        logger.info(f"Downloaded image: {image.width}x{image.height}")
    else:
        path = Path(image_source)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")
        image = Image.open(path).convert("RGB")
        logger.info(f"Loaded image from file: {image.width}x{image.height}")

    # ── 2. Output directory ───────────────────────────────────────────────────
    if output_dir:
        out_dir = Path(output_dir)
    else:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = OUTPUT_BASE / f"pipeline_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    image.save(out_dir / "00_original.png")
    logger.info(f"Output dir: {out_dir}")

    # ── 3. Analyse components ─────────────────────────────────────────────────
    logger.info("Step 1/4: Analysing components...")
    components = await analyze_components(image)
    if not components:
        raise RuntimeError("API returned no components")
    logger.info(f"  Found {len(components)} components")

    # ── 4. Write components.json with metadata ────────────────────────────────
    components_data = {
        "metadata": {
            "original_width": image.width,
            "original_height": image.height,
        },
        "components": components,
    }
    (out_dir / "components.json").write_text(json.dumps(components_data, indent=2))

    # ── 5. PNG isolation (parallel per-component) ─────────────────────────────
    logger.info("Step 2/4: Isolating PNGs (parallel)...")

    MAX_CONCURRENT = 6
    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async def _process(comp, i):
        async with sem:
            png = await isolate_component_png(comp, components, image, i)
        # SVG generation disabled
        # svg = None
        # if comp.get("type", "") in SVG_TYPES:
        #     async with sem:
        #         svg = await generate_svg(comp, i, png)
        return i, png, None

    if parallel:
        raw_results = await asyncio.gather(*[_process(comp, i) for i, comp in enumerate(components)])
    else:
        raw_results = [await _process(comp, i) for i, comp in enumerate(components)]

    raw_results = sorted(raw_results, key=lambda x: x[0])
    png_bytes_list = [r[1] for r in raw_results]
    svg_results = {r[0]: r[2] for r in raw_results if r[2] is not None}

    # ── 7. Save PNG files to disk (assembler reads from disk) ────────────────
    for i, (comp, png_bytes) in enumerate(zip(components, png_bytes_list)):
        comp_type = comp.get("type", "unknown")
        comp_desc = comp.get("description", f"component_{i}")
        safe = _safe_filename(comp_desc)

        png_filename = f"layer_{i:02d}_{comp_type}_{safe}.png"
        # svg_filename = f"layer_{i:02d}_{comp_type}_{safe}.svg"  # SVG generation disabled

        if png_bytes:
            (out_dir / png_filename).write_bytes(png_bytes)

        # SVG saving disabled
        # svg_text = svg_results.get(i)
        # if svg_text:
        #     (out_dir / svg_filename).write_text(svg_text, encoding="utf-8")

    # ── 8. Removed Template4 JSON Assembly ────────────────────────────────────────────
    logger.info("Done extracting layers. Template JSON generation disabled by user.")
    return {}
