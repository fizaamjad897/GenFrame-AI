"""
Visual Engine — OpenAI Image Edit Service

Approach: send the full source image content to gpt-image-2 with a prompt that
specifies exact target dimensions and asks for closest-possible composition.
No strip extraction, no center-crop tricks.

Post-processing: fit-then-AR-crop to reach exact target pixel dimensions.
"""
import asyncio
import base64
import io
import os

import httpx
from PIL import Image

from logger import generation_logger, error_logger

OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY", "")
OPENAI_EDIT_URL     = "https://api.openai.com/v1/images/edits"
OPENAI_MODEL        = "gpt-image-2"
OPENAI_DEFAULT_W    = 1536
OPENAI_DEFAULT_H    = 1024
OPENAI_SUPPORTED_SIZES = [
    (1792, 1024),
    (1536, 1024),
    (1024, 1024),
    (1024, 1536),
    (1024, 1792),
]

# Kept so existing imports in generation.py don't break
BANNER_AR_THRESHOLD = 3.5


def _closest_openai_size(target_width: int, target_height: int) -> tuple[int, int]:
    """
    Choose the closest supported OpenAI generation size to the target ratio.
    """
    target_ar = target_width / max(1, target_height)

    def _score(size: tuple[int, int]) -> tuple[float, float]:
        w, h = size
        ar_diff = abs((w / h) - target_ar)
        area_diff = abs((w * h) - (target_width * target_height))
        return (ar_diff, area_diff)

    return min(OPENAI_SUPPORTED_SIZES, key=_score)


def _normalize_source_image(source_bytes: bytes) -> bytes:
    """
    Normalize source into PNG while preserving full raw content and aspect ratio.
    No pre-scaling or centering before the OpenAI edit call.
    """
    src = Image.open(io.BytesIO(source_bytes)).convert("RGBA")
    buf = io.BytesIO()
    src.save(buf, format="PNG")
    return buf.getvalue()


async def call_openai_image_edit(
    source_bytes: bytes,
    prompt: str,
    target_width: int,
    target_height: int,
) -> bytes:
    """
    Send source image to gpt-image-2 with a prompt describing the target ratio.
    The model composes the output; we resize to exact target dimensions.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set in .env")

    prepared_source_bytes = await asyncio.get_event_loop().run_in_executor(
        None, _normalize_source_image, source_bytes
    )
    openai_w, openai_h = _closest_openai_size(target_width, target_height)

    generation_logger.info(
        f"[OPENAI] {OPENAI_MODEL} | target {target_width}×{target_height} "
        f"| closest model size {openai_w}×{openai_h}"
    )

    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(
            OPENAI_EDIT_URL,
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            files={"image": ("source.png", prepared_source_bytes, "image/png")},
            data={
                "model": OPENAI_MODEL,
                "prompt": prompt[:4000],
                "size": f"{openai_w}x{openai_h}",
                "n": "1",
            },
        )

        if resp.status_code != 200:
            error_logger.error(
                f"[OPENAI] API error {resp.status_code}: {resp.text[:300]}"
            )
            resp.raise_for_status()

        result = resp.json()

    b64_data = result["data"][0].get("b64_json")
    if not b64_data:
        raise RuntimeError("OpenAI returned no image data")

    raw_bytes = base64.b64decode(b64_data)

    raw_bytes = await asyncio.get_event_loop().run_in_executor(
        None, _resize_to_target, raw_bytes, target_width, target_height
    )

    generation_logger.info(f"[OPENAI] Done — {target_width}×{target_height}")
    return raw_bytes


def _resize_to_target(image_bytes: bytes, target_w: int, target_h: int) -> bytes:
    """
    Resize OpenAI output to exact target dimensions using direct stretch.
    This is intentional per current requirement: generate closest ratio first,
    then stretch to exact requested canvas.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
