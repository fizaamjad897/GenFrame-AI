"""
api_client.py — AI model client with automatic retry and generic error surfaces.

All vendor-specific details (model names, URLs, provider names) are kept internal.
Callers receive clean exceptions without any provider references.
"""

import asyncio
import base64
import logging
import httpx

logger = logging.getLogger("api_client")

try:
    from gemini_decomposition.config import (
        GOOGLE_SERVICE_ACCOUNT_PATH,
        VERTEX_AI_MODEL,
        AI_PROVIDER,
        OPENROUTER_API_KEY,
        OPENROUTER_BASE_URL,
        OPENROUTER_TEXT_MODEL,
        OPENROUTER_VISION_MODEL,
        GOOGLE_AI_STUDIO_KEY,
        AI_STUDIO_BASE_URL,
        AI_STUDIO_IMAGE_MODEL,
    )
except ImportError:
    from config import (
        GOOGLE_SERVICE_ACCOUNT_PATH,
        VERTEX_AI_MODEL,
        AI_PROVIDER,
        OPENROUTER_API_KEY,
        OPENROUTER_BASE_URL,
        OPENROUTER_TEXT_MODEL,
        OPENROUTER_VISION_MODEL,
        GOOGLE_AI_STUDIO_KEY,
        AI_STUDIO_BASE_URL,
        AI_STUDIO_IMAGE_MODEL,
    )


# ── Shared HTTP client ────────────────────────────────────────────────────────
# One client for the process lifetime — reuses TCP + TLS connections across all
# API calls instead of opening a new socket per request.
# Per-request timeouts are passed directly to each .post() call.
_shared_client = httpx.AsyncClient(
    limits=httpx.Limits(
        max_keepalive_connections=20,
        max_connections=50,
        keepalive_expiry=30.0,
    ),
)


# ── Auth ──────────────────────────────────────────────────────────────────────

def _get_access_token() -> str:
    from google.oauth2 import service_account
    import google.auth.transport.requests
    creds = service_account.Credentials.from_service_account_file(
        GOOGLE_SERVICE_ACCOUNT_PATH,
        scopes=["https://www.googleapis.com/auth/generative-language"],
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def _model_url(model: str) -> str:
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _parse_response(data: dict) -> str:
    candidates = data.get("candidates", [])
    if not candidates:
        finish = data.get("promptFeedback", {}).get("blockReason", "unknown")
        raise ValueError(f"No candidates in response (blockReason={finish})")
    candidate = candidates[0]
    finish_reason = candidate.get("finishReason", "")
    if finish_reason in ("SAFETY", "RECITATION", "BLOCKED"):
        raise ValueError(f"Response blocked: finishReason={finish_reason}")
    parts = candidate.get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts)
    if not text:
        logger.warning("_parse_response: empty text — finishReason=%s", finish_reason)
    return text


def _is_retryable(status_code: int) -> bool:
    """Retry on server errors and rate limits; not on client errors (4xx)."""
    return status_code in (429, 500, 502, 503, 504)


async def _post_with_retry(
    url: str,
    payload: dict,
    token: str,
    timeout: int,
    max_retries: int = 3,
    label: str = "AI request",
) -> dict:
    """POST to AI endpoint with retry on transient errors. Returns parsed JSON."""
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(max_retries):
        try:
            r = await _shared_client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=timeout,
            )
            if not r.is_success:
                logger.error("%s error %s (attempt %d): %s", label, r.status_code, attempt + 1, r.text[:300])
                if _is_retryable(r.status_code) and attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                r.raise_for_status()
            return r.json()
        except httpx.TimeoutException as e:
            last_exc = e
            logger.warning("%s timeout (attempt %d/%d)", label, attempt + 1, max_retries)
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        except httpx.HTTPStatusError:
            raise
        except Exception as e:
            last_exc = e
            logger.warning("%s failed (attempt %d/%d): %s", label, attempt + 1, max_retries, type(e).__name__)
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
    raise RuntimeError("AI service unavailable. Please try again.") from last_exc


# ══════════════════════════════════════════════════════════════════════════════
# OpenRouter — OpenAI-compatible text + vision
# ══════════════════════════════════════════════════════════════════════════════

def _openrouter_headers() -> dict:
    return {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://recreative.ai",
        "X-Title": "Recreative AI",
        "Content-Type": "application/json",
    }


async def _openrouter_chat(
    messages: list[dict],
    model: str,
    timeout: int,
    label: str = "openrouter",
) -> str:
    """Send messages to OpenRouter (OpenAI-compatible /chat/completions). Returns text."""
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 32768,
    }
    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(3):
        try:
            r = await _shared_client.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                headers=_openrouter_headers(),
                timeout=timeout,
            )
            if not r.is_success:
                logger.error("%s error %s (attempt %d): %s", label, r.status_code, attempt + 1, r.text[:300])
                if _is_retryable(r.status_code) and attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.TimeoutException, KeyError, IndexError) as e:
            last_exc = e
            logger.warning("%s failed (attempt %d/3): %s", label, attempt + 1, type(e).__name__)
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
        except httpx.HTTPStatusError:
            raise
    raise RuntimeError("AI service unavailable. Please try again.") from last_exc


# ══════════════════════════════════════════════════════════════════════════════
# Text Generation  (routes to Vertex or OpenRouter based on AI_PROVIDER)
# ══════════════════════════════════════════════════════════════════════════════

async def vertex_ai_generate(
    prompt: str,
    model: str = None,
    timeout: int = 60,
) -> str:
    if AI_PROVIDER == "openrouter":
        m = OPENROUTER_TEXT_MODEL
        logger.info("text-gen via OpenRouter model=%s", m)
        return await _openrouter_chat(
            [{"role": "system", "content": "Do not overthink. Respond directly and concisely."},
             {"role": "user", "content": prompt}],
            model=m, timeout=timeout, label="text-gen",
        )
    if model is None:
        model = VERTEX_AI_MODEL
    token = _get_access_token()
    payload = {
        "system_instruction": {"parts": [{"text": "Do not overthink. Respond directly and concisely without extended reasoning."}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 32768},
    }
    data = await _post_with_retry(_model_url(model), payload, token, timeout, label="text-gen")
    return _parse_response(data)


# ══════════════════════════════════════════════════════════════════════════════
# Chat (Multi-turn)  (routes to Vertex or OpenRouter based on AI_PROVIDER)
# ══════════════════════════════════════════════════════════════════════════════

async def vertex_ai_chat(
    messages: list[dict],
    model: str = None,
    timeout: int = 60,
) -> str:
    if AI_PROVIDER == "openrouter":
        m = OPENROUTER_TEXT_MODEL
        logger.info("chat via OpenRouter model=%s", m)
        or_messages = [{"role": ("assistant" if msg["role"] == "model" else msg["role"]),
                        "content": msg["content"]} for msg in messages]
        return await _openrouter_chat(or_messages, model=m, timeout=timeout, label="chat")
    if model is None:
        model = VERTEX_AI_MODEL
    token = _get_access_token()
    contents = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})
    payload = {
        "system_instruction": {"parts": [{"text": "Do not overthink. Respond directly and concisely without extended reasoning."}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 32768},
    }
    data = await _post_with_retry(_model_url(model), payload, token, timeout, label="chat")
    return _parse_response(data)


# ══════════════════════════════════════════════════════════════════════════════
# Vision (Image + Text)  (routes to Vertex or OpenRouter based on AI_PROVIDER)
# ══════════════════════════════════════════════════════════════════════════════

async def gemini_generate_with_image(
    image_bytes: bytes,
    prompt: str,
    model: str = "gemini-2.5-pro",
    timeout: int = 120,
) -> str:
    if not GOOGLE_AI_STUDIO_KEY:
        raise ValueError("GOOGLE_AI_STUDIO_KEY is required.")

    logger.info(f"vision via Google AI Studio model={model}")
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GOOGLE_AI_STUDIO_KEY}"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [
                {"inlineData": {"mimeType": "image/png", "data": img_b64}},
                {"text": prompt},
            ],
        }],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.2
        }
    }

    last_exc: Exception = RuntimeError("No attempts made")
    for attempt in range(3):
        try:
            r = await _shared_client.post(url, json=payload, timeout=timeout)
            if not r.is_success:
                logger.error("vision error %s (attempt %d): %s", r.status_code, attempt + 1, r.text[:300])
                if _is_retryable(r.status_code) and attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (httpx.TimeoutException, KeyError, IndexError) as e:
            last_exc = e
            logger.warning("vision failed (attempt %d/3): %s", attempt + 1, type(e).__name__)
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)

    raise last_exc


# ══════════════════════════════════════════════════════════════════════════════
# Google AI Studio — Image Generation & Editing  (API-key auth, no service account)
# Model: gemini-3-pro-image-preview  (or whatever AI_STUDIO_IMAGE_MODEL is set to)
# ══════════════════════════════════════════════════════════════════════════════

async def _ai_studio_image_request(
    payload: dict,
    model: str,
    timeout: int,
    label: str,
) -> bytes | None:
    """
    POST to Google AI Studio image API using GOOGLE_AI_STUDIO_KEY.
    Returns raw image bytes from the first inlineData image part, or None.

    Retry policy (single responsibility):
      - 429 rate-limit → retried here (up to 2×) with server-side backoff,
        because the caller cannot usefully handle rate-limit timing.
      - Everything else (timeout, server error, empty response) → returns None
        immediately so the CALLER'S retry loop (isolate_component_png /
        recompose_with_gemini_vision) fires with its own backoff.
        This keeps total attempts at 3 (2 outer retries × 1 inner attempt)
        rather than 9 (3 × 3).
    """
    key = GOOGLE_AI_STUDIO_KEY
    if not key:
        logger.warning("%s: GOOGLE_AI_STUDIO_KEY not set", label)
        return None

    url = f"{AI_STUDIO_BASE_URL}/{model}:generateContent?key={key}"

    for attempt in range(3):  # loop only to absorb 429s — exits immediately on any other result
        try:
            r = await _shared_client.post(url, json=payload, timeout=timeout)

            if r.status_code == 429:
                if attempt < 2:
                    wait = 10 * (attempt + 1)
                    logger.warning("%s rate-limited — retrying in %ds", label, wait)
                    await asyncio.sleep(wait)
                    continue
                logger.error("%s rate-limited — all 429 retries exhausted", label)
                return None

            if not r.is_success:
                logger.error("%s error %s: %s", label, r.status_code, r.text[:300])
                return None

            data = r.json()
            candidates = data.get("candidates", [])
            if not candidates:
                logger.warning("%s: no candidates in response", label)
                return None

            for part in candidates[0].get("content", {}).get("parts", []):
                inline = part.get("inlineData", {})
                if inline.get("data"):
                    img_bytes = base64.b64decode(inline["data"])
                    logger.info("%s: received %d bytes", label, len(img_bytes))
                    return img_bytes

            logger.warning("%s: response had no image part", label)
            return None

        except httpx.TimeoutException:
            logger.warning("%s timeout", label)
            return None
        except Exception as e:
            logger.warning("%s failed: %s", label, type(e).__name__)
            return None

    return None


async def ai_studio_generate_image(
    prompt: str,
    model: str = None,
    timeout: int = 180,
) -> bytes | None:
    """
    Text-to-image generation via Google AI Studio.
    Uses gemini-3-pro-image-preview (or AI_STUDIO_IMAGE_MODEL env override).
    Returns PNG bytes or None on failure.
    """
    model = model or AI_STUDIO_IMAGE_MODEL
    logger.info("ai_studio_generate_image: model=%s", model)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["image", "text"]},
    }
    return await _ai_studio_image_request(payload, model, timeout, "image-gen")


async def gemini_edit_image(
    image_bytes: bytes,
    prompt: str,
    model: str = None,
    timeout: int = 120,
    original_image_bytes: bytes | None = None,
    temperature: float = 0.05,
    extra_image_parts: list[bytes] | None = None,
) -> bytes | None:
    """
    Edit an image using Google AI Studio image model.
    Uses GOOGLE_AI_STUDIO_KEY (API-key auth — no service account required).
    Model: gemini-3-pro-image-preview (or AI_STUDIO_IMAGE_MODEL env override).
    Returns edited PNG bytes or None on failure.

    temperature: controls how much Gemini deviates from the reference.
                 0.1-0.2 = faithful copy-paste; 1.0 = maximum creative freedom.
    extra_image_parts: additional full-resolution PNG bytes to include as
                       separate image parts (e.g. key photo/logo components so
                       Gemini sees them at full quality, not as tiny thumbnails).
    """
    model = model or AI_STUDIO_IMAGE_MODEL
    logger.info("gemini_edit_image: model=%s temperature=%.2f", model, temperature)
    img_b64 = base64.b64encode(image_bytes).decode("utf-8")

    parts = [{"inlineData": {"mimeType": "image/png", "data": img_b64}}]

    if original_image_bytes:
        orig_b64 = base64.b64encode(original_image_bytes).decode("utf-8")
        parts.append({"inlineData": {"mimeType": "image/jpeg", "data": orig_b64}})

    if extra_image_parts:
        for extra_bytes in extra_image_parts:
            extra_b64 = base64.b64encode(extra_bytes).decode("utf-8")
            parts.append({"inlineData": {"mimeType": "image/png", "data": extra_b64}})

    parts.append({"text": prompt})

    payload = {
        "contents": [{
            "role": "user",
            "parts": parts,
        }],
        "generationConfig": {
            "responseModalities": ["image", "text"],
            "temperature": temperature,
            "topP": 0.95,
        },
    }
    return await _ai_studio_image_request(payload, model, timeout, "image-edit")


# ══════════════════════════════════════════════════════════════════════════════
# Health / Utility
# ══════════════════════════════════════════════════════════════════════════════

async def vertex_ai_health_check(timeout: int = 5) -> bool:
    try:
        token = _get_access_token()
        return bool(token)
    except Exception:
        return False


async def vertex_ai_list_models(timeout: int = 10) -> list[str]:
    return [VERTEX_AI_MODEL]


# Legacy stub
async def fal_ai_generate_image(*args, **kwargs) -> list[bytes]:
    raise NotImplementedError("Use image generation directly via server.py")
