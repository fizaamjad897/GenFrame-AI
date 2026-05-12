"""
ooh_pipeline.py — OOH banner resize via the full gemini_decomposition pipeline.

Architecture (mirrors gemini_decomposition reference implementation):
  1. analyze_components()      Gemini vision → JSON list of every visual layer
                                with bounding boxes and type metadata.
  2. isolate_component_png()   Per-component Gemini image edit → each element
                                returned as an isolated PNG on a plain background.
                                  • solid_color background → PIL fill (0 API calls)
                                  • text                  → bounding-box crop (0 API calls)
                                  • photo / image         → Gemini removes other elements
                                  • logo / icon / shape   → Gemini removes other elements
  3. recompose_with_gemini_vision()
                                Component sheet + high-res reference PNGs → Gemini
                                composes a single banner at (target_w × target_h).
                                Falls back to PIL manual compositor if Gemini fails.
  4. PIL resize                 Guarantee exact output dimensions.

All Gemini calls go through Google AI Studio REST (GOOGLE_AI_STUDIO_KEY).
The key is auto-injected from the backend's GLENN_GOOGLE_API_KEY* env vars so
no separate configuration is required.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
import os
import shutil
import sys
import hashlib
import time
from pathlib import Path
from typing import Optional

from PIL import Image

logger = logging.getLogger("ooh_pipeline")

# Per-hash decomposition locks.
# Ensures that if two requests arrive simultaneously for the same image,
# only the first runs the expensive Gemini decomposition while the second
# waits and then reads from the cache the first request populated.
_decomp_locks: dict[str, asyncio.Lock] = {}
_decomp_locks_meta: asyncio.Lock = asyncio.Lock()  # guards mutations of _decomp_locks


async def _get_decomp_lock(file_hash: str) -> asyncio.Lock:
    async with _decomp_locks_meta:
        if file_hash not in _decomp_locks:
            _decomp_locks[file_hash] = asyncio.Lock()
        return _decomp_locks[file_hash]

# ── 1. Locate gemini_decomposition folder ─────────────────────────────────────
# The decomposition package sits inside the backend folder.
_DECOMP_DIR = Path(__file__).resolve().parent / "gemini_decomposition"

if not _DECOMP_DIR.is_dir():
    raise ImportError(
        f"gemini_decomposition folder not found. Expected: {_DECOMP_DIR}"
    )

# Add to sys.path so the package's internal relative imports resolve correctly.
_DECOMP_STR = str(_DECOMP_DIR)
if _DECOMP_STR not in sys.path:
    sys.path.insert(0, _DECOMP_STR)

# ── 2. Inject GOOGLE_AI_STUDIO_KEY from backend env ───────────────────────────
# gemini_decomposition/api_client.py reads GOOGLE_AI_STUDIO_KEY from the
# environment.  The backend stores the same AI-Studio keys as
# GLENN_GOOGLE_API_KEY / _2 / _3.  Pick the first one available.
def _pick_ai_studio_key() -> str:
    for var in (
        "GOOGLE_AI_STUDIO_KEY",       # already set → use directly
        "GLENN_GOOGLE_API_KEY",
        "GLENN_GOOGLE_API_KEY_2",
        "GLENN_GOOGLE_API_KEY_3",
    ):
        key = os.getenv(var, "").strip().strip("'\"")
        if key:
            return key
    return ""

_injected_key = _pick_ai_studio_key()
if _injected_key:
    os.environ["GOOGLE_AI_STUDIO_KEY"] = _injected_key
    logger.debug("ooh_pipeline: GOOGLE_AI_STUDIO_KEY injected (...%s)", _injected_key[-8:])
else:
    logger.warning("ooh_pipeline: no Google AI Studio key found — isolation calls will fail")


# ── 3. Lazy imports from gemini_decomposition ─────────────────────────────────
# Deferred until first call so import-time errors don't break the whole server.
_DECOMP_IMPORTS: Optional[dict] = None

def _load_decomp_imports() -> dict:
    global _DECOMP_IMPORTS
    if _DECOMP_IMPORTS is not None:
        return _DECOMP_IMPORTS
    try:
        from gemini_isolate import analyze_components, isolate_component_png  # type: ignore
        from banner_recomposer import (                                          # type: ignore
            recompose_with_gemini_vision,
            recompose_banner,
        )
        _DECOMP_IMPORTS = {
            "analyze_components": analyze_components,
            "isolate_component_png": isolate_component_png,
            "recompose_with_gemini_vision": recompose_with_gemini_vision,
            "recompose_banner": recompose_banner,
        }
        logger.info("ooh_pipeline: gemini_decomposition imported successfully")
        return _DECOMP_IMPORTS
    except Exception as exc:
        raise ImportError(f"ooh_pipeline: cannot import gemini_decomposition — {exc}") from exc


# ── 4. Cache helpers ───────────────────────────────────────────────────────────

_SENTINEL = ".last_accessed"
# Delete cache folders older than this (by last-accessed sentinel mtime).
_CACHE_MAX_AGE_HOURS = 1


def _is_cache_valid(cache_dir: Path) -> bool:
    """
    A cache entry is valid only when decomposition is complete enough for
    faithful recomposition:
      1) components.json exists and parses,
      2) at least one layer PNG exists,
      3) all critical visual components (photo/image/logo) have corresponding layers.

    This avoids reusing partial caches where key reference layers are missing,
    which can cause face/logo drift during recomposition.
    """
    components_path = cache_dir / "components.json"
    if not components_path.exists():
        return False

    layer_pngs = list(cache_dir.glob("layer_*.png"))
    if len(layer_pngs) == 0:
        return False

    try:
        raw = json.loads(components_path.read_text())
        components = raw.get("components", []) if isinstance(raw, dict) else raw
        if not isinstance(components, list) or len(components) == 0:
            logger.warning("[OOH_PIPELINE] Cache invalid: malformed/empty components.json in %s", cache_dir)
            return False
    except Exception as exc:
        logger.warning("[OOH_PIPELINE] Cache invalid: cannot parse components.json in %s (%s)", cache_dir, exc)
        return False

    available_ids: set[int] = set()
    for layer in layer_pngs:
        # Expected filename pattern: layer_{idx:02d}_{type}_{desc}.png
        # Be defensive: ignore anything that does not match this prefix shape.
        name = layer.name
        if not name.startswith("layer_"):
            continue
        try:
            idx_part = name.split("_", 2)[1]
            available_ids.add(int(idx_part))
        except Exception:
            continue

    critical_types = {"photo", "image", "logo"}
    missing_critical: list[int] = []
    for idx, comp in enumerate(components):
        ctype = str(comp.get("type", "")).lower().strip()
        if ctype in critical_types and idx not in available_ids:
            missing_critical.append(idx)

    if missing_critical:
        missing_types = [str(components[i].get("type", "unknown")) for i in missing_critical]
        logger.warning(
            "[OOH_PIPELINE] Cache invalid: missing critical layers ids=%s types=%s in %s",
            missing_critical,
            missing_types,
            cache_dir,
        )
        return False

    return True


def _touch_sentinel(cache_dir: Path) -> None:
    """Update the last-accessed sentinel so TTL is based on last use, not creation."""
    try:
        sentinel = cache_dir / _SENTINEL
        sentinel.touch()
    except Exception:
        pass


def _cleanup_old_cache(
    cache_root: Path, max_age_hours: int = _CACHE_MAX_AGE_HOURS, exclude_hash: str = ""
) -> None:
    """
    Delete cached folders whose last-accessed sentinel is older than
    max_age_hours.  Falls back to directory mtime if the sentinel is absent.

    exclude_hash: skip the folder currently being processed so a concurrent
                  cleanup sweep cannot delete a folder mid-recompose.
    """
    if not cache_root.exists():
        return

    cutoff_time = time.time() - (max_age_hours * 3600)
    for item in cache_root.iterdir():
        if not item.is_dir():
            continue
        # Never evict the hash that is actively being used by this request.
        if item.name == exclude_hash:
            continue
        try:
            sentinel = item / _SENTINEL
            mtime = sentinel.stat().st_mtime if sentinel.exists() else item.stat().st_mtime
            if mtime < cutoff_time:
                logger.info("[OOH_PIPELINE] Cleaning up old cache: %s", item.name[:8])
                shutil.rmtree(item, ignore_errors=True)
        except Exception as e:
            logger.warning("[OOH_PIPELINE] Failed to clean up cache %s: %s", item.name[:8], e)


def sync_cache_from_s3(file_hash: str, cache_dir: Path) -> bool:
    # S3 cache sync disabled — local cache only.
    return False


def sync_cache_to_s3(file_hash: str, cache_dir: Path) -> None:
    # S3 cache sync disabled — local cache only.
    return


# ── 5. Public API ──────────────────────────────────────────────────────────────

async def ooh_resize(
    image_bytes: bytes,
    target_w: int,
    target_h: int,
) -> Optional[bytes]:
    """
    Resize/adapt an ad image to OOH billboard dimensions.

    Uses the full gemini_decomposition pipeline.
    Implements SHA256 caching strictly on the analysis/isolation phase so
    subsequent resizes of the exact same image run in seconds.
    """
    try:
        funcs = _load_decomp_imports()
    except ImportError as exc:
        logger.error("[OOH_PIPELINE] %s", exc)
        return None

    try:
        source = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        logger.error("[OOH_PIPELINE] Cannot open source image: %s", exc)
        return None

    # 2072×252 is handled exclusively by banner_2072x252.py via main.py routing.
    if target_w == 2072 and target_h == 252:
        logger.info("[OOH_PIPELINE] 2072×252 routed to banner_2072x252 — skipping ooh_resize.")
        return None

    # Ultra-wide QMS dimensions (AR ≥ 9:1) are routed to banner_2072x252 which has
    # purpose-built prompt engineering and post-processing for extreme aspect ratios.
    _ULTRA_WIDE_ROUTE = {(2640, 288)}
    _is_ultra_wide_route = (target_w, target_h) in _ULTRA_WIDE_ROUTE

    logger.info(
        "[OOH_PIPELINE] %d×%d → %d×%d",
        source.width, source.height, target_w, target_h,
    )

    # 1. Compute cache key and paths.
    file_hash = hashlib.sha256(image_bytes).hexdigest()
    cache_root = Path(__file__).resolve().parent / "ooh_decomposition_cache"
    cache_root.mkdir(exist_ok=True)
    cache_dir = cache_root / file_hash

    # 2. Cache lookup with per-hash lock.
    decomp_lock = await _get_decomp_lock(file_hash)

    if _is_cache_valid(cache_dir):
        logger.info("[OOH_PIPELINE] Cache hit (local) for %s.", file_hash[:8])
        _touch_sentinel(cache_dir)
    else:
        async with decomp_lock:
            # Re-check after lock: another request may have finished decomposition.
            if _is_cache_valid(cache_dir):
                logger.info(
                    "[OOH_PIPELINE] Cache hit (local, post-lock) for %s — "
                    "concurrent decomposition already completed.",
                    file_hash[:8],
                )
                _touch_sentinel(cache_dir)
            else:
                logger.info(
                    "[OOH_PIPELINE] Cache miss for %s. Running full decomposition.",
                    file_hash[:8],
                )
                cache_dir.mkdir(exist_ok=True, parents=True)
                success = await _decompose_and_save(
                    source,
                    cache_dir,
                    funcs["analyze_components"],
                    funcs["isolate_component_png"],
                )
                if not success:
                    shutil.rmtree(cache_dir, ignore_errors=True)
                    return None

                _touch_sentinel(cache_dir)

    # 3. Background cleanup after active cache selection.
    asyncio.get_event_loop().run_in_executor(
        None, _cleanup_old_cache, cache_root, _CACHE_MAX_AGE_HOURS, file_hash
    )

    # 3b. Patch photo/image layers with exact source crops.
    # Regardless of where the cache came from (local, S3, or fresh decomposition),
    # overwrite every non-full-canvas photo/image layer with a direct PIL crop so
    # faces are always pixel-perfect copies of the original — never AI-regenerated.
    _patch_photo_layers(source, cache_dir)

    # 4. Recompose for requested target dimensions.
    logger.info("[OOH_PIPELINE] Recomposing at %d×%d", target_w, target_h)
    orig_path = cache_dir / "00_original.png"

    # Ultra-wide QMS 2640×288 uses banner_2640x288.py — a dedicated recomposer with a
    # prompt engineered specifically for the 9.2:1 strip: forces horizontal output
    # orientation, distributes components across the full width, and prevents clustering.
    if _is_ultra_wide_route:
        try:
            from banner_2640x288 import recompose_with_gemini_vision as _uw_recompose  # type: ignore
            logger.info("[OOH_PIPELINE] Ultra-wide %d×%d → banner_2640x288", target_w, target_h)
            result_bytes = await _uw_recompose(
                output_dir=cache_dir,
                target_w=target_w,
                target_h=target_h,
                original_image_path=orig_path,
                temperature=0.10,
            )
            if result_bytes:
                logger.info("[OOH_PIPELINE] banner_2640x288 ultra-wide recompose succeeded")
                return result_bytes
            logger.warning("[OOH_PIPELINE] banner_2640x288 returned None for %d×%d — falling back to standard path", target_w, target_h)
        except Exception as exc:
            logger.warning("[OOH_PIPELINE] banner_2640x288 ultra-wide routing failed: %s — falling back", exc)

    try:
        result_bytes = await funcs["recompose_with_gemini_vision"](
            output_dir=cache_dir,
            target_w=target_w,
            target_h=target_h,
            original_image_path=orig_path,
            temperature=0.10,
        )
        if result_bytes:
            logger.info("[OOH_PIPELINE] Gemini recompose succeeded")
            return result_bytes
    except Exception as exc:
        logger.warning("[OOH_PIPELINE] Gemini recompose failed: %s", exc)

    # 5. Manual fallback compositor.
    logger.info("[OOH_PIPELINE] Falling back to manual PIL compositor")
    try:
        return await funcs["recompose_banner"](
            output_dir=cache_dir,
            target_w=target_w,
            target_h=target_h,
        )
    except Exception as exc:
        logger.error("[OOH_PIPELINE] Manual compositor failed: %s", exc)
        return None


# ── 6. Cache-only helper (used by external recomposers like banner_2072x252) ───

async def ensure_cache_decomposed(image_bytes: bytes) -> Optional[Path]:
    """
    Run the decomposition pipeline for image_bytes and return the cache dir path.
    Does NOT perform recomposition — callers supply their own recomposer.
    Returns None on failure.
    """
    try:
        funcs = _load_decomp_imports()
    except ImportError as exc:
        logger.error("[OOH_PIPELINE] %s", exc)
        return None

    try:
        source = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as exc:
        logger.error("[OOH_PIPELINE] Cannot open source image: %s", exc)
        return None

    file_hash = hashlib.sha256(image_bytes).hexdigest()
    cache_root = Path(__file__).resolve().parent / "ooh_decomposition_cache"
    cache_root.mkdir(exist_ok=True)
    cache_dir = cache_root / file_hash

    decomp_lock = await _get_decomp_lock(file_hash)

    if _is_cache_valid(cache_dir):
        logger.info("[OOH_PIPELINE] ensure_cache: hit (local) for %s.", file_hash[:8])
        _touch_sentinel(cache_dir)
    else:
        async with decomp_lock:
            if _is_cache_valid(cache_dir):
                logger.info("[OOH_PIPELINE] ensure_cache: hit (local, post-lock) for %s.", file_hash[:8])
                _touch_sentinel(cache_dir)
            else:
                logger.info("[OOH_PIPELINE] ensure_cache: miss for %s. Running decomposition.", file_hash[:8])
                cache_dir.mkdir(exist_ok=True, parents=True)
                success = await _decompose_and_save(
                    source,
                    cache_dir,
                    funcs["analyze_components"],
                    funcs["isolate_component_png"],
                )
                if not success:
                    shutil.rmtree(cache_dir, ignore_errors=True)
                    return None
                _touch_sentinel(cache_dir)

    asyncio.get_event_loop().run_in_executor(
        None, _cleanup_old_cache, cache_root, _CACHE_MAX_AGE_HOURS, file_hash
    )
    _patch_photo_layers(source, cache_dir)
    return cache_dir


# ── 7. Photo layer patch ──────────────────────────────────────────────────────

def _patch_photo_layers(source: Image.Image, cache_dir: Path) -> None:
    """
    Overwrite every photo/image layer PNG with a direct bounding-box crop from
    the source image — pixel-perfect, zero AI involvement.

    This runs after the cache is loaded from ANY source (local disk, S3, or a
    fresh decomposition).  The test pipeline never has face-change problems
    because it calls isolate_component_png with the live PIL source, and for
    non-full-canvas photos that now returns a plain crop.  This function brings
    the same guarantee to the cached path: even if S3 stored a Gemini-generated
    layer that changed a face, the layer on disk is replaced before recomposition.
    """
    components_path = cache_dir / "components.json"
    if not components_path.exists():
        return
    try:
        raw = json.loads(components_path.read_text())
        components = raw.get("components", []) if isinstance(raw, dict) else raw
    except Exception as exc:
        logger.warning("[OOH_PIPELINE] _patch_photo_layers: cannot read components.json: %s", exc)
        return

    for idx, comp in enumerate(components):
        ctype = comp.get("type", "").lower()
        if ctype not in ("photo", "image"):
            continue

        # Full-canvas photos are background scenes that need Gemini to strip overlaid
        # elements — leave those alone.
        b = comp.get("box_2d")
        is_full_canvas = (
            b and len(b) == 4 and
            b[1] <= 50 and b[0] <= 50 and
            b[3] >= 950 and b[2] >= 950
        )
        if is_full_canvas:
            continue

        # Find the layer file for this index.
        matches = sorted(cache_dir.glob(f"layer_{idx:02d}_*.png"))
        if not matches:
            continue
        layer_path = matches[0]

        # Bounding-box crop directly from source — same logic as test pipeline.
        if not b or len(b) != 4:
            continue
        ymin, xmin, ymax, xmax = b
        left   = int(max(0, xmin / 1000.0 * source.width))
        top    = int(max(0, ymin / 1000.0 * source.height))
        right  = int(min(source.width,  xmax / 1000.0 * source.width))
        bottom = int(min(source.height, ymax / 1000.0 * source.height))
        if right <= left or bottom <= top:
            continue

        try:
            cropped = source.crop((left, top, right, bottom))
            buf = io.BytesIO()
            cropped.convert("RGB").save(buf, format="PNG")
            layer_path.write_bytes(buf.getvalue())
            logger.info(
                "[OOH_PIPELINE] Patched layer %02d (%s) with exact crop %dx%d — face preserved",
                idx, ctype, cropped.width, cropped.height,
            )
        except Exception as exc:
            logger.warning("[OOH_PIPELINE] _patch_photo_layers: layer %02d failed: %s", idx, exc)


# ── 8. Internal decomposition helper ──────────────────────────────────────────

async def _decompose_and_save(
    source: Image.Image,
    out_dir: Path,
    analyze_components,
    isolate_component_png,
) -> bool:
    orig_path = out_dir / "00_original.png"
    source.save(str(orig_path))

    logger.info("[OOH_PIPELINE] Step 1/2 — analysing components")
    try:
        components = await analyze_components(source)
    except Exception as exc:
        logger.error("[OOH_PIPELINE] Analysis failed: %s", exc)
        return False

    if not components:
        logger.error("[OOH_PIPELINE] No components detected")
        return False

    logger.info("[OOH_PIPELINE] %d components detected", len(components))
    (out_dir / "components.json").write_text(
        json.dumps(
            {
                "metadata": {"original_width": source.width, "original_height": source.height},
                "components": components,
            },
            indent=2,
        )
    )

    logger.info("[OOH_PIPELINE] Step 2/2 — isolating %d components (parallel)", len(components))
    sem = asyncio.Semaphore(6)

    async def _isolate(comp: dict, idx: int):
        async with sem:
            try:
                png = await isolate_component_png(comp, components, source, idx)
                return idx, png
            except Exception as exc:
                logger.warning("[OOH_PIPELINE] Layer %02d isolation failed: %s", idx, exc)
                return idx, None

    raw_results = await asyncio.gather(*[_isolate(c, i) for i, c in enumerate(components)])

    ok_count = 0
    for idx, png_bytes in sorted(raw_results, key=lambda x: x[0]):
        if not png_bytes:
            continue
        ctype = components[idx].get("type", "unknown")
        safe = (
            "".join(ch if ch.isalnum() or ch in " _-" else "" for ch in components[idx].get("description", "")[:40])
            .strip()
            .replace(" ", "_")
        )
        (out_dir / f"layer_{idx:02d}_{ctype}_{safe}.png").write_bytes(png_bytes)
        ok_count += 1

    if ok_count == 0:
        logger.error("[OOH_PIPELINE] All isolation calls failed")
        return False

    return True
