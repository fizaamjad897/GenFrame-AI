"""
Design Compliance Report service.

Post-generation audit of a resized/generated image: technical (dimensions,
file size), visual (safe zone, contrast, clutter, color), and content
(prompt adherence, readability, focal point via Gemini vision). Runs as a
FastAPI background task so it adds no latency to the /api/resize response.
"""
import os
import time
from datetime import datetime
from io import BytesIO
from typing import List, Optional, Tuple

from dotenv import load_dotenv
from PIL import Image, ImageFilter, ImageStat
from pydantic import BaseModel
from google import genai
from google.genai import types

from auth import db

load_dotenv()

compliance_collection = db["design_compliance_reports"] if db is not None else None

if compliance_collection is not None:
    compliance_collection.create_index("report_id", unique=True)
    compliance_collection.create_index("userId")
    compliance_collection.create_index("createdAt")

# Separate from the image-generation model (main.py) since this step needs
# text/JSON output rather than an image response.
COMPLIANCE_VISION_MODEL = os.getenv("COMPLIANCE_VISION_MODEL", "gemini-2.5-flash")
_GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
_vision_client = genai.Client(api_key=_GOOGLE_API_KEY) if _GOOGLE_API_KEY else None


class AIComplianceAnalysis(BaseModel):
    prompt_adherence_score: Optional[int] = None
    text_readable: bool
    text_readability_notes: str
    focal_point_centered: bool
    clutter_assessment: str
    analysis_summary: str


def _status_for_score(score: float) -> str:
    if score >= 85:
        return "PASS"
    if score >= 65:
        return "WARN"
    return "FAIL"


# ── Technical checks (Pillow, no API cost) ────────────────────────────────
def _run_technical_checks(image: Image.Image, image_bytes: bytes, target_dims: Tuple[int, int]) -> dict:
    actual_w, actual_h = image.size
    target_w, target_h = target_dims
    dims_match = (actual_w == target_w) and (actual_h == target_h)
    return {
        "status": "PASS" if dims_match else "WARN",
        "actual_dims": {"width": actual_w, "height": actual_h},
        "target_dims": {"width": target_w, "height": target_h},
        "dims_match": dims_match,
        "file_size_kb": round(len(image_bytes) / 1024, 1),
        "format": image.format or "PNG",
    }


# ── Visual checks (Pillow, no API cost) ───────────────────────────────────
def _edge_energy(region: Image.Image) -> float:
    gray = region.convert("L").filter(ImageFilter.FIND_EDGES)
    return ImageStat.Stat(gray).mean[0]


def _run_visual_checks(image: Image.Image) -> dict:
    rgb = image.convert("RGB")
    w, h = rgb.size

    # Safe zone heuristic: if the outer border carries meaningfully more edge
    # energy than the interior, key content likely sits too close to the crop edge.
    margin_w, margin_h = max(1, int(w * 0.08)), max(1, int(h * 0.08))
    inner = rgb.crop((margin_w, margin_h, max(margin_w + 1, w - margin_w), max(margin_h + 1, h - margin_h)))
    full_energy = _edge_energy(rgb)
    inner_energy = _edge_energy(inner)
    safe_zone_clear = full_energy <= inner_energy * 1.35

    # WCAG-style contrast approximation: split pixels by median luminance into
    # a "dark half" and "light half" and apply the standard contrast formula.
    gray_pixels = sorted(rgb.convert("L").getdata())
    mid = len(gray_pixels) // 2
    dark_avg = (sum(gray_pixels[:mid]) / max(1, mid)) / 255.0
    light_avg = (sum(gray_pixels[mid:]) / max(1, len(gray_pixels) - mid)) / 255.0
    contrast_ratio = round((light_avg + 0.05) / (dark_avg + 0.05), 2)
    contrast_status = "PASS" if contrast_ratio >= 4.5 else ("WARN" if contrast_ratio >= 3.0 else "FAIL")

    avg_saturation = round(ImageStat.Stat(rgb.convert("HSV")).mean[1] / 255.0 * 100, 1)

    # Clutter score: inverse of overall edge density, 0-100 (higher = cleaner).
    clutter_score = max(0, min(100, round(100 - (full_energy / 255.0 * 100))))

    small = rgb.resize((100, 100)).quantize(colors=5)
    palette = small.getpalette() or []
    dominant_colors = []
    for _, idx in sorted(small.getcolors() or [], reverse=True)[:5]:
        r, g, b = palette[idx * 3: idx * 3 + 3]
        dominant_colors.append(f"#{r:02x}{g:02x}{b:02x}")

    status = "PASS"
    if contrast_status == "FAIL" or not safe_zone_clear:
        status = "FAIL"
    elif contrast_status == "WARN" or clutter_score < 50:
        status = "WARN"

    return {
        "status": status,
        "safe_zone_clear": safe_zone_clear,
        "contrast_ratio": contrast_ratio,
        "contrast_status": contrast_status,
        "clutter_score": clutter_score,
        "avg_saturation": avg_saturation,
        "dominant_colors": dominant_colors,
    }


# ── AI analysis (Gemini vision) ───────────────────────────────────────────
def _run_ai_analysis(image: Image.Image, prompt: Optional[str], aspect_ratio: str, max_retries: int = 2) -> Optional[dict]:
    if not _vision_client:
        return None

    instruction = (
        "You are a digital signage design QA reviewer. Analyze this generated image and respond with the requested JSON fields. "
        f"Target display format: {aspect_ratio}. "
        "If the image contains no text at all, set text_readable to true (there is no legibility concern) and say so in text_readability_notes. "
        + (
            f'The image was generated/edited from this prompt: "{prompt}". Score how well the image matches the prompt\'s intent (0-100).'
            if prompt
            else "No custom prompt was used for this generation; leave prompt_adherence_score null."
        )
    )

    for attempt in range(max_retries):
        try:
            response = _vision_client.models.generate_content(
                model=COMPLIANCE_VISION_MODEL,
                contents=[instruction, image],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=AIComplianceAnalysis,
                ),
            )
            parsed = response.parsed
            return parsed.model_dump() if parsed else None
        except Exception as e:
            err = str(e)
            retriable = any(k in err for k in ["503", "429", "overload", "resource_exhausted", "deadline_exceeded"])
            print(f"[COMPLIANCE] AI analysis attempt {attempt + 1}/{max_retries} failed: {err[:160]}")
            if retriable and attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return None
    return None


def _content_from_ai(ai: Optional[dict]) -> dict:
    if not ai:
        return {
            "status": "WARN",
            "prompt_adherence_score": None,
            "text_readable": None,
            "text_readability_notes": "AI analysis unavailable.",
            "focal_point_centered": None,
            "clutter_assessment": "unavailable",
            "ai_analysis": "AI analysis was unavailable for this report.",
        }

    score = ai.get("prompt_adherence_score")
    status = "PASS"
    if score is not None and score < 60:
        status = "FAIL"
    elif (score is not None and score < 80) or ai.get("text_readable") is False:
        status = "WARN"

    return {
        "status": status,
        "prompt_adherence_score": score,
        "text_readable": ai.get("text_readable"),
        "text_readability_notes": ai.get("text_readability_notes"),
        "focal_point_centered": ai.get("focal_point_centered"),
        "clutter_assessment": ai.get("clutter_assessment"),
        "ai_analysis": ai.get("analysis_summary"),
    }


def _overall_score(technical: dict, visual: dict, content: dict) -> float:
    technical_score = 100.0 if technical["dims_match"] else 60.0

    contrast_component = min(100.0, (visual["contrast_ratio"] / 7.0) * 100)
    safe_zone_component = 100.0 if visual["safe_zone_clear"] else 40.0
    visual_score = (contrast_component + visual["clutter_score"] + safe_zone_component) / 3

    content_parts = []
    if content.get("prompt_adherence_score") is not None:
        content_parts.append(float(content["prompt_adherence_score"]))
    content_parts.append(100.0 if content.get("text_readable") else 50.0 if content.get("text_readable") is None else 40.0)
    content_parts.append(100.0 if content.get("focal_point_centered") else 50.0 if content.get("focal_point_centered") is None else 60.0)
    content_score = sum(content_parts) / len(content_parts)

    return round(technical_score * 0.2 + visual_score * 0.4 + content_score * 0.4, 1)


def _build_recommendations(technical: dict, visual: dict, content: dict) -> List[str]:
    recs = []
    if not technical["dims_match"]:
        recs.append(
            f"Output dimensions {technical['actual_dims']['width']}x{technical['actual_dims']['height']} do not "
            f"exactly match the target {technical['target_dims']['width']}x{technical['target_dims']['height']}."
        )
    if visual["contrast_status"] != "PASS":
        recs.append(
            f"Contrast ratio is {visual['contrast_ratio']}:1 (WCAG AA recommends 4.5:1+) — "
            "consider increasing foreground/background contrast."
        )
    if not visual["safe_zone_clear"]:
        recs.append("Key content may be too close to the edges — keep important elements within the inner safe zone.")
    if visual["clutter_score"] < 50:
        recs.append("Composition appears visually dense — consider simplifying or increasing negative space.")
    if content.get("prompt_adherence_score") is not None and content["prompt_adherence_score"] < 80:
        recs.append("The generated image may not fully match the prompt's intent — consider refining the prompt.")
    if content.get("text_readable") is False:
        recs.append("Text may not be legible at the target display size/distance.")
    return recs


def _serialize(doc: dict) -> dict:
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("createdAt"), datetime):
        doc["createdAt"] = doc["createdAt"].isoformat()
    if isinstance(doc.get("completedAt"), datetime):
        doc["completedAt"] = doc["completedAt"].isoformat()
    return doc


def create_pending_report(
    report_id: str,
    job_id: Optional[str],
    user_id: str,
    engine_type: str,
    image_url: str,
    prompt: Optional[str],
    aspect_ratio: str,
    target_dims: Tuple[int, int],
) -> None:
    if compliance_collection is None:
        return
    compliance_collection.insert_one({
        "report_id": report_id,
        "job_id": job_id,
        "userId": user_id,
        "engineType": engine_type,
        "imageUrl": image_url,
        "prompt": prompt,
        "aspectRatio": aspect_ratio,
        "targetDims": {"width": target_dims[0], "height": target_dims[1]},
        "status": "pending",
        "compliance": None,
        "recommendations": [],
        "createdAt": datetime.utcnow(),
        "completedAt": None,
        "error": None,
    })


def run_compliance_analysis(
    report_id: str,
    image_bytes: bytes,
    prompt: Optional[str],
    aspect_ratio: str,
    target_dims: Tuple[int, int],
) -> None:
    if compliance_collection is None:
        return
    try:
        image = Image.open(BytesIO(image_bytes))
        image.load()

        technical = _run_technical_checks(image, image_bytes, target_dims)
        visual = _run_visual_checks(image)
        ai = _run_ai_analysis(image, prompt, aspect_ratio)
        content = _content_from_ai(ai)

        overall_score = _overall_score(technical, visual, content)
        overall_status = _status_for_score(overall_score)
        recommendations = _build_recommendations(technical, visual, content)

        compliance_collection.update_one(
            {"report_id": report_id},
            {"$set": {
                "status": "complete",
                "compliance": {
                    "overall_score": overall_score,
                    "overall_status": overall_status,
                    "technical": technical,
                    "visual": visual,
                    "content": content,
                },
                "recommendations": recommendations,
                "completedAt": datetime.utcnow(),
            }},
        )
    except Exception as e:
        print(f"[COMPLIANCE] Analysis failed for {report_id}: {e}")
        compliance_collection.update_one(
            {"report_id": report_id},
            {"$set": {"status": "failed", "error": str(e), "completedAt": datetime.utcnow()}},
        )


def get_report(report_id: str, user_id: str) -> Optional[dict]:
    if compliance_collection is None:
        return None
    doc = compliance_collection.find_one({"report_id": report_id, "userId": user_id})
    return _serialize(doc) if doc else None


def get_report_history(
    user_id: str,
    engine_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    skip: int = 0,
) -> List[dict]:
    if compliance_collection is None:
        return []
    query = {"userId": user_id}
    if engine_type:
        query["engineType"] = engine_type
    if status:
        query["status"] = status
    cursor = compliance_collection.find(query, sort=[("createdAt", -1)], skip=skip, limit=limit)
    return [_serialize(doc) for doc in cursor]


def get_report_summary(user_id: str) -> dict:
    if compliance_collection is None:
        return {"total": 0, "avg_score": None, "pass_count": 0, "warn_count": 0, "fail_count": 0, "pending_count": 0}

    docs = list(compliance_collection.find({"userId": user_id}))
    scores = [d["compliance"]["overall_score"] for d in docs if d.get("compliance")]

    def _count(s: str) -> int:
        return sum(1 for d in docs if (d.get("compliance") or {}).get("overall_status") == s)

    return {
        "total": len(docs),
        "avg_score": round(sum(scores) / len(scores), 1) if scores else None,
        "pass_count": _count("PASS"),
        "warn_count": _count("WARN"),
        "fail_count": _count("FAIL"),
        "pending_count": sum(1 for d in docs if d.get("status") == "pending"),
    }
