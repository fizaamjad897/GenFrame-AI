"""
Configuration for gemini_decomposition.
Supports Vertex AI (service-account auth) + Google AI Studio (API-key auth) + OpenRouter.
Image generation/editing routes to Google AI Studio by default when GOOGLE_AI_STUDIO_KEY is set.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# DigitalOcean Spaces Configuration (matches main.py env variable names)
DO_SPACES_KEY = (os.getenv("DO_ACCESS_KEY_ID") or os.getenv("ACCESS_KEY_ID", "")).strip("'\" ")
DO_SPACES_SECRET = (os.getenv("DO_SECRET_KEY") or os.getenv("SECRET_KEY", "")).strip("'\" ")
DO_SPACES_BUCKET = os.getenv("SPACENAME", "").strip("'\" ")
_endpoint_raw = os.getenv("ENDPOINT", "").strip("'\" ")
DO_SPACES_REGION = _endpoint_raw.replace("https://", "").replace("http://", "").split(".")[0] if _endpoint_raw else "nyc3"
DO_SPACES_ENDPOINT = _endpoint_raw if _endpoint_raw.startswith("http") else f"https://{_endpoint_raw}" if _endpoint_raw else ""
DO_SPACES_CDN = ""  # Will use bucket.endpoint format like main.py

# ── AI Provider Toggle ───────────────────────────────────────────────────────
# Set AI_PROVIDER=openrouter to route text/vision through OpenRouter instead of Vertex.
# Image editing always uses the direct Gemini image model (OpenRouter has no equivalent).
AI_PROVIDER = os.getenv("AI_PROVIDER", "vertex").strip("'\" ").lower()  # "vertex" | "openrouter"

# ── Google AI Studio (API-key auth — no service account needed) ───────────────
# Used for image generation and image editing throughout the project.
GOOGLE_AI_STUDIO_KEY = os.getenv("GOOGLE_AI_STUDIO_KEY", "").strip("'\" ")
AI_STUDIO_BASE_URL   = "https://generativelanguage.googleapis.com/v1beta/models"

# Primary image model — gemini-3-pro-image-preview via Google AI Studio
AI_STUDIO_IMAGE_MODEL = os.getenv("AI_STUDIO_IMAGE_MODEL", "gemini-3-pro-image-preview").strip("'\" ")

# ── Vertex AI / Generative Language API (text/vision only) ───────────────────
VERTEX_AI_BASE_URL = os.getenv("VERTEX_AI_BASE_URL", "").strip("'\" ")
VERTEX_AI_KEY = os.getenv("VERTEX_AI_KEY", "").strip("'\" ")
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "gemini-2.5-pro").strip("'\" ")

# ── OpenRouter ───────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip("'\" ")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_TEXT_MODEL = os.getenv("OPENROUTER_TEXT_MODEL", "google/gemini-2.5-pro").strip("'\" ")
OPENROUTER_VISION_MODEL = os.getenv("OPENROUTER_VISION_MODEL", "google/gemini-2.5-pro").strip("'\" ")

# Legacy Gemini image model name (kept for backward compat — AI_STUDIO_IMAGE_MODEL is preferred)
GEMINI_IMAGE_MODEL = os.getenv("GEMINI_IMAGE_MODEL", "gemini-3-pro-image-preview").strip("'\" ")

# FAL AI (legacy — no longer used)
FAL_AI_BASE_URL = os.getenv("FAL_AI_BASE_URL", "").strip("'\" ")
FAL_AI_KEY = os.getenv("FAL_AI_KEY", "").strip("'\" ")

# Optional: Image generation model for text-to-image (FAL AI Nano Banana Pro)
IMAGE_GENERATION_ENABLED = os.getenv("IMAGE_GENERATION_ENABLED", "true").lower() == "true"

# ── Google Service Account (Direct Vertex AI) ─────────────────────────────────
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    str(Path(__file__).parent / "gen-lang-client-0761213620-a395b0a53468 (1).json"),
)
VERTEX_AI_PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID", "gen-lang-client-0761213620")
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")