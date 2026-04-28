from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header, Request, Body
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Tuple, Any, Dict
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io
import base64
import httpx
from datetime import datetime, timedelta
import uuid
import boto3
import stripe
import google.auth
import vertexai
from bson import ObjectId
from botocore.config import Config
from models import UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest, TokenResponse, UserResponse, PlanUpgradeRequest, CheckoutRequest
from auth import (
    create_user, verify_user_credentials, create_access_token, 
    verify_token, get_user_by_id, increment_user_units, 
    create_password_reset_token, reset_password_by_token, 
    send_password_reset_email, user_doc_to_response,
    get_all_plans, get_user_usage_stats, get_billing_history,
    generate_monthly_bill, log_usage,
    consume_units, cancel_user_plan, update_user_plan,
    simulate_month_end_rollover, perform_all_postpaid_rollovers
)
import auth as auth_module
import org_auth  # Organisation Module JWT validation
from stripe_manager import create_checkout_session, create_portal_session, handle_webhook_event, cancel_subscription
import asyncio
from functools import partial


async def run_blocking(fn, *args, **kwargs):
    """
    Run blocking function in executor to avoid blocking event loop.
    Critical for Gemini API calls which can take 30-120 seconds.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        partial(fn, *args, **kwargs)
    )


# --- Wrapper classes (from reference project) ---
class _InlineDataWrapper:
    def __init__(self, data: bytes, mime_type: str = "image/png"):
        self.data = data
        self.mime_type = mime_type

class _PartWrapper:
    def __init__(self, data: bytes, mime_type: str = "image/png"):
        self.inline_data = _InlineDataWrapper(data, mime_type)

class _GeminiLikeImageResponse:
    """Minimal wrapper so Vertex/SeedDream image responses look like google-genai responses."""
    def __init__(self, data: bytes, mime_type: str = "image/png"):
        self.parts = [_PartWrapper(data, mime_type)]


async def call_openrouter_image(contents: list) -> _GeminiLikeImageResponse:
    """
    Fallback: Call OpenRouter API with gemini-3-pro-image-preview.
    OpenRouter routes through multiple providers, so it may work when direct Gemini is down.
    """
    openrouter_key = os.getenv("OPENROUTER_KEY")
    if not openrouter_key:
        raise RuntimeError("OPENROUTER_KEY not configured in .env")

    # Extract user_context and image dimensions
    user_context = ""
    src_w = None
    src_h = None
    
    for item in contents:
        if isinstance(item, str):
            user_context += item + " "
        elif isinstance(item, Image.Image):
            src_w, src_h = item.size
        elif isinstance(item, (bytes, bytearray)):
            # Try to get dimensions from bytes
            try:
                img = Image.open(io.BytesIO(item))
                src_w, src_h = img.size
            except:
                pass
    
    user_context = user_context.strip()
    
    # Only use detailed prompt if we have dimensions, otherwise fall back to original behavior
    if src_w and src_h:
        # Use source dimensions as target for fallback behavior
        tw = src_w
        th = src_h

        # Construct the detailed resize prompt
        detailed_prompt = build_openrouter_resize_prompt(source_dims=(src_w, src_h), target_dims=(tw, th), user_context=user_context)

        message_parts = []
        # Add the detailed prompt as text
        message_parts.append({"type": "text", "text": detailed_prompt})
        
        # Add images
        for item in contents:
            if isinstance(item, Image.Image):
                buf = io.BytesIO()
                item.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                message_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })
            elif isinstance(item, types.Part):
                inline = getattr(item, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    b64 = base64.b64encode(inline.data).decode("utf-8")
                    mime = getattr(inline, "mime_type", "image/png")
                    message_parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"}
                    })
            elif isinstance(item, (bytes, bytearray)):
                b64 = base64.b64encode(bytes(item)).decode("utf-8")
                message_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })

        content = message_parts
    else:
        # Fall back to original behavior if we can't get dimensions
        message_parts = []
        for item in contents:
            if isinstance(item, str):
                message_parts.append({"type": "text", "text": item})
            elif isinstance(item, Image.Image):
                buf = io.BytesIO()
                item.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                message_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })
            elif isinstance(item, types.Part):
                inline = getattr(item, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    b64 = base64.b64encode(inline.data).decode("utf-8")
                    mime = getattr(inline, "mime_type", "image/png")
                    message_parts.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"}
                    })
                else:
                    message_parts.append({"type": "text", "text": str(item)})
            elif isinstance(item, (bytes, bytearray)):
                b64 = base64.b64encode(bytes(item)).decode("utf-8")
                message_parts.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"}
                })
            else:
                message_parts.append({"type": "text", "text": str(item)})

        if all(p["type"] == "text" for p in message_parts):
            content = " ".join(p["text"] for p in message_parts)
        else:
            content = message_parts

    payload = {
        "model": "google/gemini-3-pro-image-preview",
        "messages": [{"role": "user", "content": content}],
        "modalities": ["image", "text"],
    }

    print(f"[OpenRouter] Calling OpenRouter with gemini-3-pro-image-preview...")

    async with httpx.AsyncClient(timeout=120.0) as hc:
        resp = await hc.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openrouter_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    if resp.status_code != 200:
        raise RuntimeError(f"OpenRouter API failed ({resp.status_code}): {resp.text}")

    result = resp.json()
    choices = result.get("choices", [])
    if not choices:
        raise RuntimeError(f"OpenRouter returned no choices: {result}")

    message = choices[0].get("message", {})
    images = message.get("images", [])

    if not images:
        raise RuntimeError(f"OpenRouter returned no images. Response: {message.get('content', 'No content')}")

    data_url = images[0]["image_url"]["url"]
    header, encoded = data_url.split(",", 1)
    image_bytes = base64.b64decode(encoded)

    print(f"[OpenRouter] Successfully generated image ({len(image_bytes)} bytes)")
    return _GeminiLikeImageResponse(image_bytes)


async def call_gemini_with_retry(model_name, contents, config=None, max_retries=3, api_client=None):
    """
    Call Gemini API with exponential backoff retry logic.
    Ported from reference project.
    """
    def _resolve_client():
        return api_client if api_client is not None else client

    for attempt in range(max_retries):
        try:
            _client = _resolve_client()
            if config:
                response = await run_blocking(
                    _client.models.generate_content,
                    model=model_name,
                    contents=contents,
                    config=config
                )
            else:
                response = await run_blocking(
                    _client.models.generate_content,
                    model=model_name,
                    contents=contents
                )
            return response
        except Exception as e:
            error_str = str(e).lower()
            full_error = str(e)
            print(f"[Attempt {attempt + 1}/{max_retries}] Gemini API Error: {full_error}")
            
            is_retriable = any([
                "503" in full_error,
                "429" in full_error,
                "overload" in error_str,
                "resource_exhausted" in error_str,
                "too_many_requests" in error_str,
                "deadline_exceeded" in error_str
            ])
            
            if is_retriable and attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"⚠️  Retriable error. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            else:
                if attempt == max_retries - 1:
                    print(f"❌ Max retries ({max_retries}) exhausted")
                raise


def _init_vertex_if_configured() -> bool:
    """
    Initialize Vertex AI using native SDK, preferring explicit env vars
    but falling back to the project embedded in application default credentials.
    Ported from reference project.
    """
    project_id = os.getenv("VERTEX_PROJECT_ID")

    if not project_id:
        try:
            credentials, detected_project = google.auth.default()
            if detected_project:
                project_id = detected_project
                print(f"Vertex fallback: using detected project '{project_id}' from ADC")
        except Exception as e:
            print(f"Vertex fallback: failed to detect project from ADC: {e}")

    if not project_id:
        # Try from vertex.json
        try:
            import json as _json
            _possible_paths = [
                os.getenv("VERTEX_SA_PATH"),
                os.path.join(os.path.dirname(__file__), "vertex.json"),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), "vertex.json"),
            ]
            _vertex_sa_path = next((p for p in _possible_paths if p and os.path.exists(p)), None)
            if _vertex_sa_path:
                with open(_vertex_sa_path, "r") as _vf:
                    _vertex_data = _json.load(_vf)
                    project_id = _vertex_data.get("project_id")
        except Exception:
            pass

    if not project_id:
        print("Vertex fallback disabled: no project id available")
        return False

    try:
        vertex_location = os.getenv("VERTEX_LOCATION", "us-central1")
        vertexai.init(project=project_id, location=vertex_location)
        return True
    except Exception as e:
        print(f"Error initializing Vertex AI: {e}")
        return False


async def call_gemini_with_retry_and_vertex_fallback(
    model_name,
    contents,
    config=None,
    max_retries=3,
    prefer_vertex: bool = False,
    vertex_contents=None,
):
    """
    Master function ported from reference project.
    Tries: Gemini SDK → native Vertex AI → SeedDream → Flux
    """
    # For non-image models, just use the primary path
    if model_name != "gemini-3-pro-image-preview":
        return await call_gemini_with_retry(
            model_name=model_name,
            contents=contents,
            config=config,
            max_retries=max_retries,
        )

    async def _try_vertex() -> "_GeminiLikeImageResponse":
        if not _init_vertex_if_configured():
            raise RuntimeError("Vertex not configured")

        vertex_model_name = os.getenv("VERTEX_IMAGE_MODEL") or model_name
        project_id = os.getenv("VERTEX_PROJECT_ID")
        if not project_id:
            try:
                _, project_id = google.auth.default()
            except Exception:
                pass
        if not project_id:
            raise RuntimeError("No Vertex project ID available")

        # gemini-3-pro-image-preview requires the GLOBAL endpoint
        location = "global"

        def _vertex_genai_call(use_model_name: str):
            vertex_client = genai.Client(
                vertexai=True,
                project=project_id,
                location=location,
            )
            effective_contents = vertex_contents if vertex_contents is not None else contents
            genai_contents = []
            for item in effective_contents:
                if isinstance(item, str):
                    genai_contents.append(item)
                elif isinstance(item, types.Part):
                    genai_contents.append(item)
                elif isinstance(item, Image.Image):
                    buf = io.BytesIO()
                    item.save(buf, format="PNG")
                    genai_contents.append(types.Part.from_bytes(
                        data=buf.getvalue(),
                        mime_type="image/png"
                    ))
                elif isinstance(item, (bytes, bytearray)):
                    genai_contents.append(types.Part.from_bytes(
                        data=bytes(item),
                        mime_type="image/png"
                    ))
                else:
                    genai_contents.append(str(item))

            v_response = vertex_client.models.generate_content(
                model=use_model_name,
                contents=genai_contents,
                config=config,
            )

            image_bytes = None
            for part in getattr(v_response, "candidates", [{}])[0].content.parts if hasattr(v_response, "candidates") and v_response.candidates else []:
                inline = getattr(part, "inline_data", None)
                if inline and getattr(inline, "data", None):
                    image_bytes = inline.data
                    break

            if image_bytes is None:
                for part in getattr(v_response, "parts", []):
                    inline = getattr(part, "inline_data", None)
                    if inline and getattr(inline, "data", None):
                        image_bytes = inline.data
                        break

            if not image_bytes:
                raise RuntimeError(f"Vertex AI ({use_model_name}) returned no image payload")

            return image_bytes

        # Cascade: try primary model, then flash fallbacks on 429/quota errors
        vertex_models = [
            vertex_model_name,
            "gemini-3.1-flash-image-preview",
            "gemini-2.5-flash-image",
        ]

        for i, try_model in enumerate(vertex_models):
            try:
                image_bytes = await run_blocking(_vertex_genai_call, try_model)
                print(f"[Vertex] Successfully generated image via Vertex AI Gen AI SDK ({try_model})")
                return _GeminiLikeImageResponse(image_bytes)
            except Exception as e:
                err_str = str(e).lower()
                is_quota_error = any(k in err_str for k in ["429", "resource_exhausted", "quota", "rate limit"])
                print(f"[Vertex] Model {try_model} failed: {e}")
                if is_quota_error and i < len(vertex_models) - 1:
                    print(f"[Vertex] Quota exhausted for {try_model}, trying next model...")
                    continue
                else:
                    raise

    async def _try_seedream(sd_contents):
        """SeedDream 4.5 fallback via fal.ai"""
        seedream_key = os.getenv("SEEDREAM_KEY")
        if not seedream_key:
            raise RuntimeError("SEEDREAM_KEY not configured")
        prompt = ""
        image_data_uris = []
        for item in sd_contents:
            if isinstance(item, str):
                prompt += item + " "
            elif isinstance(item, Image.Image):
                buf = io.BytesIO()
                item.save(buf, format="PNG")
                b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
                image_data_uris.append(f"data:image/png;base64,{b64}")
            elif isinstance(item, (bytes, bytearray)):
                b64 = base64.b64encode(item).decode("utf-8")
                image_data_uris.append(f"data:image/png;base64,{b64}")

        url = "https://fal.run/fal-ai/bytedance/seedream/v4.5/edit"
        headers = {"Authorization": f"Key {seedream_key}", "Content-Type": "application/json"}
        payload = {
            "prompt": f"IMAGE ONLY. FULL FRAME DIGITAL CONTENT. NO physical mockups. {prompt.strip()}",
            "image_urls": image_data_uris,
            "sync_mode": True
        }
        async with httpx.AsyncClient(timeout=120.0) as hc:
            resp = await hc.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            result = resp.json()
            images = result.get("images", [])
            if not images:
                raise RuntimeError("SeedDream returned no images")
            image_url = images[0].get("url")
            if image_url.startswith("data:"):
                header, encoded = image_url.split(",", 1)
                return _GeminiLikeImageResponse(base64.b64decode(encoded))
            else:
                img_resp = await hc.get(image_url)
                return _GeminiLikeImageResponse(img_resp.content)

    async def _try_flux(fx_contents):
        """Flux Schnell fallback via fal.ai"""
        flux_key = os.getenv("FLUX_KEY")
        if not flux_key:
            raise RuntimeError("FLUX_KEY not configured")
        prompt = ""
        for item in fx_contents:
            if isinstance(item, str):
                prompt += item + " "
        url = "https://fal.run/fal-ai/flux-1/schnell"
        headers = {"Authorization": f"Key {flux_key}", "Content-Type": "application/json"}
        payload = {"prompt": prompt.strip(), "sync_mode": True}
        async with httpx.AsyncClient(timeout=120.0) as hc:
            resp = await hc.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            result = resp.json()
            images = result.get("images", [])
            if not images:
                raise RuntimeError("Flux returned no images")
            image_url = images[0].get("url")
            if image_url.startswith("data:"):
                header, encoded = image_url.split(",", 1)
                return _GeminiLikeImageResponse(base64.b64decode(encoded))
            else:
                img_resp = await hc.get(image_url)
                return _GeminiLikeImageResponse(img_resp.content)

    # --- Execution order ---
    if prefer_vertex:
        try:
            return await _try_vertex()
        except Exception as e:
            print(f"[Vertex Primary] Vertex-first attempt failed: {e}")

    # --- TIER 0 (FIRST PRIORITY): OPENROUTER ---
    try:
        print("[OpenRouter] Attempting OpenRouter as primary fallback...")
        return await call_openrouter_image(contents)
    except Exception as or_error:
        print(f"[OpenRouter] OpenRouter failed: {or_error}")

    try:
        return await call_gemini_with_retry(
            model_name=model_name,
            contents=contents,
            config=config,
            max_retries=max_retries,
        )
    except Exception as primary_error:
        print(f"[Gemini Fallback] Primary Gemini call failed: {primary_error}")

        try:
            return await _try_vertex()
        except Exception as vertex_error:
            print(f"[Vertex Fallback] Vertex AI call also failed: {vertex_error}")

            try:
                print("[SeedDream Fallback] Attempting SeedDream 4.5...")
                return await _try_seedream(contents)
            except Exception as sd_error:
                print(f"[SeedDream Fallback] SeedDream failed: {sd_error}")

                try:
                    print("[Flux Fallback] Attempting Flux Schnell...")
                    return await _try_flux(contents)
                except Exception as flux_error:
                    print(f"[Flux Fallback] Flux also failed: {flux_error}")
                    raise vertex_error

import warnings
# Suppress the Google Cloud Python 3.10 deprecation warnings for cleaner logs
warnings.filterwarnings("ignore", category=FutureWarning, module=r"google.api_core")

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Import and validate Stripe configuration
from stripe_manager import validate_stripe_configuration, is_production_mode
if not validate_stripe_configuration():
    print("⚠️  WARNING: Stripe configuration validation failed. Server will start but payments may fail.")

app = FastAPI(
    title="Visual Engine API",
    root_path="/secure"
)

# Add CORS middleware
# CORS: allow explicit origins (Starlette blocks "*" when allow_credentials=True)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in (os.getenv("CORS_ORIGINS") or "http://localhost:3000,http://127.0.0.1:3000,https://transformation.slidexy.ai,https://recreative.slidexy.ai,https://transformation.signagexai.com").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def billing_rollover_task():
    """
    Background loop to check if it's the 1st of the month and run rollovers.
    """
    print("🕒 [SYSTEM] Billing rollover background task started")
    while True:
        try:
            now = datetime.utcnow()
            # If it's the 1st day of the month
            if now.day == 1:
                # IMPORTANT: perform_all_postpaid_rollovers is synchronous (blocking).
                # We use asyncio.to_thread to run it in a separate side-thread so it doesn't 
                # freeze the main server event loop for other users.
                success = await asyncio.to_thread(perform_all_postpaid_rollovers)
                if success:
                    print(f"✅ [SYSTEM] Automated rollover for {now.strftime('%Y-%m')} completed successfully")
            
            # Wait 1 hour before checking again
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"❌ [SYSTEM] Error in billing rollover task: {e}")
            await asyncio.sleep(600)  # Wait 10 mins before retry on error

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(billing_rollover_task())

from fastapi.exceptions import RequestValidationError
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    import json
    body = await request.body()
    print(f"[VALIDATION ERROR] Path: {request.url.path}")
    print(f"Details: {exc.errors()}")
    print(f"Body received: {body.decode('utf-8', errors='ignore')}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body_preview": body.decode('utf-8', errors='ignore')[:100]}
    )

# Digital Ocean Spaces Configuration (matching NestJS env variable names)
# We use specific DO_ prefixes to avoid shadowing conflicts in .env
DO_SPACES_ACCESS_KEY = (os.getenv("DO_ACCESS_KEY_ID") or os.getenv("ACCESS_KEY_ID", "")).strip("'\" ")
DO_SPACES_SECRET_KEY = (os.getenv("DO_SECRET_KEY") or os.getenv("SECRET_KEY", "")).strip("'\" ")
DO_SPACES_ENDPOINT = os.getenv("ENDPOINT", "").strip("'\" ")
DO_SPACES_BUCKET_NAME = os.getenv("SPACENAME", "").strip("'\" ")

# Dependency for authentication
def get_current_user(request: Request, authorization: str = Header(None), x_api_key: str = Header(None, alias="X-API-KEY")):
    """
    Enhanced authentication handler that supports:
    1. API Key auth (server-to-server) - highest priority
    2. Organisation Module JWT (from microservice) - preferred for new users
    3. Legacy Visual Engine JWT (for backward compatibility during migration)
    """
    
    # Priority 1: API Key auth (server-to-server, always works)
    if x_api_key:
        user = auth_module.verify_api_key(x_api_key)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        request.state.api_key_type = auth_module.get_api_key_type(user, x_api_key)
        request.state.auth_mode = "api_key"
        return user

    # Validate Bearer token exists
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    
    # Priority 2: Try Organisation Module JWT (new microservice)
    # This JWT contains userId, orgId, userRole, etc.
    try:
        user = org_auth.validate_org_module_jwt(token)
        request.state.auth_mode = "org_jwt"
        request.state.org_id = org_auth.get_org_context_from_user(user).get("org_id")
        request.state.org_role = org_auth.get_org_context_from_user(user).get("role")
        print(f"[AUTH] Org Module JWT authenticated user: {user.get('email')}")
        return user
    except HTTPException as org_jwt_error:
        # If not a valid org JWT, try legacy
        if org_jwt_error.status_code == 401:
            # Likely not an org JWT, try legacy
            print(f"[AUTH] Status 401, will try legacy JWT")
            pass
        else:
            # Server error, don't try legacy
            raise
    except Exception as e:
        print(f"[AUTH]Org JWT validation failed, trying legacy: {e}")
    
    # Priority 3: Fallback to legacy Visual Engine JWT (during migration)
    # This JWT only contains {"sub": user_id}
    user_id = verify_token(token)
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            request.state.auth_mode = "legacy_jwt"
            print(f"[AUTH] Legacy Visual Engine JWT authenticated user: {user.get('email')}")
            return user
    
    # No auth method succeeded
    raise HTTPException(status_code=401, detail="Invalid or expired credentials")

def get_admin_user(current_user = Depends(get_current_user)):
    """
    Dependency to ensure the current user has administrative privileges.
    """
    # 1. Check for 'admin' role in Organization Context (preferred for new users)
    org_context = current_user.get("_org_context", {})
    org_role = org_context.get("role", "").lower()
    
    # 2. Check for 'admin' role in local user record (fallback for legacy/local users)
    local_role = str(current_user.get("role") or "").lower()
    
    # 3. Specific owner/tester fallback
    is_owner = current_user.get("email") == "muhammadhamzafaisal146@gmail.com"
    
    if org_role == "admin" or local_role == "admin" or is_owner:
        return current_user
        
    raise HTTPException(status_code=403, detail="Administrative privileges required")


def _can_use_custom_resize(current_user: dict) -> bool:
    """Allow custom-resize for Glen/HamzaFaisal orgs and their sub-orgs using org-id-based checks."""
    # Allowed org UUIDs
    ALLOWED_ORG_IDS = {
        "d9f031dc-ba8f-4397-9534-81612cc8a686",  # Glen's org ID
        "35cd976c-d4ac-4e76-8dde-d8065334fa42",  # HamzaFaisal's org ID
    }
    
    # Org-id-based check (primary)
    org_context = (current_user.get("_org_context") or {}) if isinstance(current_user, dict) else {}
    org_id = str(org_context.get("org_id") or "").strip()
    parent_org_id = str(org_context.get("parent_org_id") or "").strip()
    
    if org_id in ALLOWED_ORG_IDS or parent_org_id in ALLOWED_ORG_IDS:
        return True
    
    # Email/domain fallback for testing
    email = str(current_user.get("email") or "").strip().lower()
    domain = email.split("@")[-1] if "@" in email else ""
    if email == "muhammadhamzafaisal146@gmail.com" or domain == "fmctv.co.nz":
        return True
    
    return False

# Initialize Gemini Client (lazy init or global if key is present)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Vertex AI (second fallback for Gemini)
# 1) Prefer explicit env overrides
# 2) Fallback to project_id from local vertex.json service account if present
_vertex_project_id_env = os.getenv("VERTEX_PROJECT_ID")
_vertex_project_id_file = None
try:
    import json as _json
    _possible_paths = [
        os.getenv("VERTEX_SA_PATH"),
        os.path.join(os.path.dirname(__file__), "vertex.json"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "vertex.json"),
        "/home/lahore/visual-engine-be/vertex.json" # Fallback for known server path
    ]
    _vertex_sa_path = next((p for p in _possible_paths if p and os.path.exists(p)), None)
    if _vertex_sa_path:
        with open(_vertex_sa_path, "r") as _vf:
            _vertex_data = _json.load(_vf)
            _vertex_project_id_file = _vertex_data.get("project_id")
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _vertex_sa_path
                print(f"🔑 [VERTEX] Set GOOGLE_APPLICATION_CREDENTIALS to {_vertex_sa_path}")
    else:
        print("⚠️  [VERTEX] vertex.json not found in any expected location.")
except Exception as _vertex_load_err:
    print(f"⚠️  [VERTEX] Failed to initialize Vertex credentials: {_vertex_load_err}")

VERTEX_PROJECT_ID = _vertex_project_id_env or _vertex_project_id_file
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")

if VERTEX_PROJECT_ID:
    print(f"✅ [VERTEX] Project identified: {VERTEX_PROJECT_ID}")
else:
    print("⚠️  [VERTEX] No Project ID found. Vertex AI will be skipped.")

# Create Vertex AI client using google-genai SDK (same approach as vertex-gemini-api)
vertex_client = None
if VERTEX_PROJECT_ID:
    try:
        vertex_client = genai.Client(
            vertexai=True,
            project=VERTEX_PROJECT_ID,
            location=VERTEX_LOCATION,
        )
        print(f"✅ [VERTEX] Client initialized (project={VERTEX_PROJECT_ID}, location={VERTEX_LOCATION})")
    except Exception as vc_err:
        print(f"⚠️  [VERTEX] Failed to create Vertex client: {vc_err}")

# Fallback image generation service (Fal.ai Nano Banana Pro wrapper)
FAL_FALLBACK_URL = os.getenv(
    "FAL_FALLBACK_URL",
    "https://recreative.signagexai.com/fal-ai-fallback/generate",
)

# We will init inside the function or global if key exists.
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    print("Warning: GOOGLE_API_KEY not set in .env")

# Glenn's own Gemini clients (multi-key rotation with 250/24h limit per key)
GLENN_API_KEY = os.getenv("GLENN_VERTEX_API_KEY")
GLENN_GOOGLE_KEY_1 = os.getenv("GLENN_GOOGLE_API_KEY")
GLENN_GOOGLE_KEY_2 = os.getenv("GLENN_GOOGLE_API_KEY_2")
GLENN_GOOGLE_KEY_3 = os.getenv("GLENN_GOOGLE_API_KEY_3")
glenn_client = None
glenn_google_client_1 = None
glenn_google_client_2 = None
glenn_google_client_3 = None

if GLENN_GOOGLE_KEY_1:
    glenn_google_client_1 = genai.Client(api_key=GLENN_GOOGLE_KEY_1)
    print(f"Glenn Google client #1 initialised (key: ...{GLENN_GOOGLE_KEY_1[-8:]})")
if GLENN_GOOGLE_KEY_2:
    glenn_google_client_2 = genai.Client(api_key=GLENN_GOOGLE_KEY_2)
    print(f"Glenn Google client #2 initialised (key: ...{GLENN_GOOGLE_KEY_2[-8:]})")
if GLENN_GOOGLE_KEY_3:
    glenn_google_client_3 = genai.Client(api_key=GLENN_GOOGLE_KEY_3)
    print(f"Glenn Google client #3 initialised (key: ...{GLENN_GOOGLE_KEY_3[-8:]})")
if GLENN_API_KEY:
    glenn_client = genai.Client(api_key=GLENN_API_KEY)
    print(f"Glenn Vertex client initialised  (key: ...{GLENN_API_KEY[-8:]})")
if not GLENN_GOOGLE_KEY_1 and not GLENN_GOOGLE_KEY_2 and not GLENN_GOOGLE_KEY_3 and not GLENN_API_KEY:
    print("Warning: No Glenn API keys set in .env")

# ── Glenn key request counters (250 requests / 24h per key) ──────────────
GLENN_KEY_LIMIT = 250

# Map key labels → (client object, api_key string)
_glenn_keys_map = {
    "key_1":  {"client": glenn_google_client_1, "api_key": GLENN_GOOGLE_KEY_1 or "not-set"},
    "key_2":  {"client": glenn_google_client_2, "api_key": GLENN_GOOGLE_KEY_2 or "not-set"},
    "key_3":  {"client": glenn_google_client_3, "api_key": GLENN_GOOGLE_KEY_3 or "not-set"},
    "vertex": {"client": glenn_client,          "api_key": GLENN_API_KEY      or "not-set"},
}

# Map key labels → client objects (kept for interception fallback loop)
_glenn_clients = {k: v["client"] for k, v in _glenn_keys_map.items()}

# In-memory fallback cache (only used if MongoDB is unreachable)
_glenn_counters = {
    "key_1":  {"count": 0, "reset_at": datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)},
    "key_2":  {"count": 0, "reset_at": datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)},
    "key_3":  {"count": 0, "reset_at": datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)},
    "vertex": {"count": 0, "reset_at": datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)},
}

def _get_glenn_col():
    """Safely get the MongoDB collection, returns None if unavailable."""
    try:
        col = auth_module.glenn_key_usage_collection
        return col if col is not None else None
    except Exception:
        return None

print("[GLENN] ✅ Counter system initialised")

def _glenn_get_counter(key_label: str) -> dict:
    """Read counter from MongoDB (shared). Falls back to in-memory if DB is down."""
    now = datetime.utcnow()
    next_reset = now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
    try:
        col = _get_glenn_col()
        if col is not None:
            doc = col.find_one({"_id": key_label})
            if doc:
                # Auto-reset if 24h window passed
                if now >= doc.get("reset_at", now):
                    col.update_one({"_id": key_label}, {"$set": {"count": 0, "reset_at": next_reset}})
                    print(f"[GLENN] 🔄 Counter reset for {key_label} (24h window passed)")
                    _glenn_counters[key_label] = {"count": 0, "reset_at": next_reset}
                    return {"count": 0, "reset_at": next_reset}
                # Sync in-memory cache from DB
                _glenn_counters[key_label] = {"count": doc.get("count", 0), "reset_at": doc.get("reset_at", next_reset)}
                return _glenn_counters[key_label]
            else:
                # No doc yet — seed it
                col.insert_one({"_id": key_label, "count": 0, "reset_at": next_reset})
                _glenn_counters[key_label] = {"count": 0, "reset_at": next_reset}
                return _glenn_counters[key_label]
    except Exception as e:
        print(f"[GLENN] ⚠️  MongoDB read failed, using in-memory fallback: {e}")
    # Fallback to in-memory
    c = _glenn_counters.get(key_label, {"count": 0, "reset_at": next_reset})
    if now >= c.get("reset_at", now):
        c["count"] = 0
        c["reset_at"] = next_reset
    return c

def glenn_log_all_counters():
    """Print a dashboard of all Glenn key counters."""
    lines = ["[GLENN] 📊 Key counters (shared):"]
    for kid in ["key_1", "key_2", "key_3", "vertex"]:
        c = _glenn_get_counter(kid)
        suffix = _glenn_keys_map.get(kid, {}).get("api_key", "?")
        suffix = f"...{suffix[-8:]}" if suffix != "not-set" and suffix != "?" else "NOT SET"
        lines.append(f"  {kid} ({suffix}): {c['count']}/{GLENN_KEY_LIMIT}")
    print("\n".join(lines))

def glenn_get_google_client():
    """Return the active Google client + key label based on shared counters."""
    for kid in ["key_1", "key_2", "key_3"]:
        if _glenn_clients.get(kid):
            c = _glenn_get_counter(kid)
            if c["count"] < GLENN_KEY_LIMIT:
                return _glenn_clients[kid], kid
    return glenn_google_client_1 or glenn_google_client_2 or glenn_google_client_3, "all_google_exhausted"

def glenn_increment_counter(key_label: str):
    """Atomically increment counter in MongoDB (shared) + sync in-memory cache."""
    count = "?"
    try:
        col = _get_glenn_col()
        if col is not None:
            next_reset = datetime.utcnow().replace(hour=0, minute=0, second=0) + timedelta(days=1)
            result = col.find_one_and_update(
                {"_id": key_label},
                {"$inc": {"count": 1}, "$setOnInsert": {"reset_at": next_reset}},
                upsert=True,
                return_document=True,
            )
            if result:
                count = result.get("count", 0)
                _glenn_counters[key_label] = {"count": count, "reset_at": result.get("reset_at", next_reset)}
    except Exception as e:
        print(f"[GLENN] ⚠️  MongoDB increment failed, using in-memory: {e}")
        c = _glenn_counters.get(key_label)
        if c:
            c["count"] = c.get("count", 0) + 1
            count = c["count"]
    suffix = _glenn_keys_map.get(key_label, {}).get("api_key", "?")
    suffix = f"...{suffix[-8:]}" if suffix != "not-set" and suffix != "?" else "?"
    print(f"[GLENN] 📊 {key_label} ({suffix}): {count}/{GLENN_KEY_LIMIT} requests used")
    glenn_log_all_counters()

def glenn_mark_key_exhausted(key_label: str):
    """Mark a key as exhausted in shared MongoDB + in-memory cache."""
    try:
        col = _get_glenn_col()
        if col is not None:
            col.update_one(
                {"_id": key_label},
                {"$set": {"count": GLENN_KEY_LIMIT}},
                upsert=True,
            )
    except Exception as e:
        print(f"[GLENN] ⚠️  MongoDB exhausted-mark failed: {e}")
    c = _glenn_counters.get(key_label)
    if c:
        c["count"] = GLENN_KEY_LIMIT
    suffix = _glenn_keys_map.get(key_label, {}).get("api_key", "?")
    suffix = f"...{suffix[-8:]}" if suffix != "not-set" and suffix != "?" else "?"
    print(f"[GLENN] 🚫 {key_label} ({suffix}) marked EXHAUSTED — won't be used until reset")
    glenn_log_all_counters()

# Legacy alias for backward compat
glenn_google_client = glenn_google_client_1

# Initialize Digital Ocean Spaces client (matching NestJS implementation exactly)
if not DO_SPACES_ENDPOINT or not DO_SPACES_BUCKET_NAME:
    raise ValueError("ENDPOINT and SPACENAME must be set in environment variables")

if not DO_SPACES_ACCESS_KEY or not DO_SPACES_SECRET_KEY:
    raise ValueError("ACCESS_KEY_ID and SECRET_KEY must be set in environment variables")

try:
    # Clean endpoint - remove protocol if present
    endpoint_clean = DO_SPACES_ENDPOINT.replace('https://', '').replace('http://', '').strip()
    
    # Extract region from endpoint (e.g., sfo3.digitaloceanspaces.com -> sfo3)
    region = endpoint_clean.split('.')[0] if '.' in endpoint_clean else 'nyc3'
    
    # Ensure endpoint has protocol for boto3
    endpoint_url = endpoint_clean if endpoint_clean.startswith('http') else f'https://{endpoint_clean}'
    
    s3_client = boto3.client(
        's3',
        endpoint_url=endpoint_url,
        aws_access_key_id=DO_SPACES_ACCESS_KEY,
        aws_secret_access_key=DO_SPACES_SECRET_KEY,
        region_name=region,
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'virtual'} # Recommended for Digital Ocean
        )
    )
    print("Digital Ocean Spaces client initialized")
except Exception as e:
    print(f"Error: Failed to initialize Digital Ocean Spaces client: {e}")
    raise

@app.post("/api/users/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    new_user = create_user(user_data)
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    access_token = create_access_token(str(new_user["_id"]))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": auth_module.user_doc_to_response(new_user)
    }

@app.get("/api/status")
async def get_status():
    """Health check and version verification"""
    return {
        "status": "online",
        "version": "1.1.2",
        "timestamp": datetime.utcnow().isoformat(),
        "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
        "db_connected": auth_module.client is not None
    }

@app.post("/api/users/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Login user"""
    user = verify_user_credentials(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(str(user["_id"]))
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_doc_to_response(user)
    }

@app.post("/api/users/request-password-reset")
async def request_password_reset(request: ForgotPasswordRequest):
    """Request password reset"""
    from auth import get_user_by_email
    user = get_user_by_email(request.email)
    if not user:
        # For security, don't reveal if email exists
        return {"message": "If email exists, reset link has been sent"}
    
    reset_token = create_password_reset_token(request.email)
    email_sent, token = send_password_reset_email(request.email, reset_token)
    
    # For development mode, return the token so user can test without email
    response = {"message": "Password reset token created"}
    if token:  # Token returned means dev mode or email failed
        response["dev_token"] = token
        response["message"] += " (Dev Mode - use token below)"
    
    return response

@app.post("/api/users/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset password using token"""
    success = reset_password_by_token(request.token, request.newPassword)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    return {"message": "Password reset successfully"}

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user info"""
    return user_doc_to_response(current_user)


@app.post("/api/users/api-key")
async def create_api_key(type: str | None = None, current_user = Depends(get_current_user)):
    """
    Create an API key for a specific engine type.
    Query param (optional): type=resize|create
    Returns raw key once; only hash is stored.
    """
    try:
        # Backward-compatible behavior: if no type param, manage legacy single key via `apiKeyHash`.
        if type is None:
            if current_user.get("apiKeyHash"):
                raise ValueError("API key already exists")
            raw = auth_module.generate_api_key_for_user(str(current_user["_id"]))
            return {"message": "API key created", "api_key": raw}

        # New behavior: scoped keys stored under `api_keys`
        api_keys = current_user.get("api_keys", {}) or {}
        if api_keys.get(f"{type}_hash"):
            raise ValueError("API key already exists for this type")
        raw = auth_module.generate_api_key_for_user(str(current_user["_id"]), type)
        return {"message": "API key created", "api_key": raw, "type": type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/users/api-key")
async def remove_api_key(type: str | None = None, current_user = Depends(get_current_user)):
    if type is None:
        ok = auth_module.delete_api_key(str(current_user["_id"]))
    else:
        ok = auth_module.delete_api_key(str(current_user["_id"]), type)
    if not ok:
        raise HTTPException(status_code=400, detail="No API key to delete")
    return {"message": "API key deleted", "type": type}


@app.post("/api/stripe/create-checkout")
@app.post("/stripe/create-checkout")
@app.post("/create-checkout")  # Highly robust alias
async def stripe_create_checkout(
    request: Request,
    body: dict = Body(...), 
    current_user = Depends(get_current_user)
):
    """
    Create a Stripe checkout session.
    """
    user_email = current_user.get("email")
    print(f"💳 [STRIPE] Checkout Attempt: User={user_email}, Path={request.url.path}")
    
    plan_code = body.get("plan_code") or body.get("planCode")
    engine_type = body.get("engine_type") or body.get("engineType") or "transformation"
    order_type = body.get("order_type") or body.get("orderType") or "subscription"
    
    if not plan_code:
        print(f"❌ [STRIPE] Missing plan_code in body: {body}")
        raise HTTPException(status_code=400, detail="plan_code is required")

    try:
        url = create_checkout_session(str(current_user["_id"]), plan_code=plan_code, engine_type=engine_type, order_type=order_type)
        if not url:
            print(f"❌ [STRIPE] create_checkout_session returned None for {user_email}")
            raise HTTPException(status_code=500, detail="Failed to create Stripe checkout session.")
            
        print(f"✅ [STRIPE] Success: {url}")
        return {"url": url}
    except Exception as e:
        print(f"❌ [STRIPE] Unexpected Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stripe/create-portal")
@app.post("/stripe/create-portal")
@app.post("/create-portal")
async def stripe_create_portal(current_user = Depends(get_current_user)):
    customer_id = current_user.get("stripeCustomerId")
    if not customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer on file for user")
    url = create_portal_session(customer_id)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to create Stripe portal session")
    return {"url": url}


@app.post("/api/stripe/create-test-checkout")
async def stripe_create_test_checkout(current_user = Depends(get_current_user)):
    """
    Create a simple $1 test checkout session for the current user.
    Intended for manual verification that Stripe is wired correctly.
    """
    price_id = os.getenv("STRIPE_PRICE_TEST_DAILY")
    if not price_id:
        raise HTTPException(status_code=500, detail="Test price ID is not configured")

    user_id = str(current_user["_id"])
    user_email = current_user.get("email")

    # Ensure Stripe customer exists
    customer_id = current_user.get("stripeCustomerId")
    if not customer_id:
        customer = stripe.Customer.create(
            email=user_email,
            metadata={"user_id": user_id}
        )
        customer_id = customer.id
        auth_module.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"stripeCustomerId": customer_id}}
        )

    try:
        # Detect if the price is recurring or one-time so we use the correct mode
        try:
            price_obj = stripe.Price.retrieve(price_id)
            is_recurring = price_obj.type == "recurring"
            print(f"[TEST CHECKOUT] Price {price_id} is {'RECURRING' if is_recurring else 'ONE-TIME'}")
        except Exception as e:
            print(f"[TEST CHECKOUT] Failed to retrieve price {price_id}: {e}")
            # Fallback: assume recurring since your tester product is per-day
            is_recurring = True

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription" if is_recurring else "payment",
            success_url=os.getenv("FRONTEND_URL") + "/billing/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("FRONTEND_URL") + "/billing/cancel",
            metadata={
                "user_id": user_id,
                "engine_type": "transformation",
                "order_type": "test",
                "plan_code": "daily_tester",
            }
        )
        return {"url": session.url}
    except Exception as e:
        print(f"Stripe Test Checkout Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create test checkout session")


@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    payload = await request.body()
    ok = handle_webhook_event(payload, stripe_signature)
    if not ok:
        raise HTTPException(status_code=400, detail="Webhook error")
    return {"received": True}

# Alternative webhook route without /api prefix for deployment flexibility
@app.post("/stripe/webhook")
@app.post("/secure/api/stripe/webhook")
async def stripe_webhook_alt(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    """Alternative webhook endpoint for deployments where /api prefix is handled by reverse proxy or deep paths"""
    payload = await request.body()
    ok = handle_webhook_event(payload, stripe_signature)
    if not ok:
        raise HTTPException(status_code=400, detail="Webhook error")
    return {"received": True}


@app.post("/api/stripe/cancel-subscription")
async def stripe_cancel_subscription(body: dict | None = None, current_user = Depends(get_current_user)):
    """
    Cancel the user's active Stripe subscription.
    Body (optional):
      - at_period_end: bool (default False) — if True, cancel at period end instead of immediately.
      - engine_type: str (optional) — if specified, only cancels that engine's subscription
    """
    from bson import ObjectId
    
    # Determine which engine to cancel
    engine_type = None
    at_period_end = False
    if isinstance(body, dict):
        at_period_end = bool(body.get("at_period_end", False))
        engine_type = body.get("engine_type")
    
    # Prioritize subscription ID from engine_data if engine_type is specified
    # This prevents using the wrong sub ID in a multi-engine environment
    subscription_id = None
    if engine_type:
        engine_data = current_user.get("engine_data", {})
        engine_info = engine_data.get(engine_type, {})
        subscription_id = engine_info.get("stripeSubscriptionId")
        if subscription_id:
            print(f"🔍 Prioritizing engine-specific subscription ID for {engine_type}: {subscription_id}")

    # Fallback to top-level if no engine-specific ID or no engine_type provided
    if not subscription_id:
        subscription_id = current_user.get("stripeSubscriptionId")
        if subscription_id:
            print(f"ℹ️ Using top-level subscription ID: {subscription_id}")

    user_id = str(current_user["_id"])
    
    # Normalize subscription_id (remove empty strings, trim whitespace)
    subscription_id = (subscription_id or "").strip() if subscription_id else None
    
    if not subscription_id:
        print(f"❌ Cancel attempt failed: No subscription ID found for user {user_id} (Engine: {engine_type or 'any'})")
        raise HTTPException(
            status_code=400, 
            detail="No active subscription found for this engine. You may not have an active subscription, or it may have already been cancelled."
        )

    try:
        # Validate subscription exists in Stripe before attempting cancellation
        print(f"🔍 Validating subscription {subscription_id} for user {user_id}")
        
        try:
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            print(f"✅ Subscription found in Stripe: {subscription_id}, status: {stripe_sub.status}")
        except stripe.error.InvalidRequestError as e:
            # Subscription doesn't exist in Stripe
            error_msg = str(e)
            print(f"❌ Subscription not found in Stripe: {error_msg}")
            
            # Clean up invalid subscription ID from database
            users_collection = auth_module.users_collection
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {"stripeSubscriptionId": ""}}
            )
            print(f"🧹 Cleaned up invalid subscription ID from user {user_id}")
            
            raise HTTPException(
                status_code=400, 
                detail="Subscription not found in Stripe. It may have already been cancelled. Your account has been updated."
            )
        
        # Check if subscription is already cancelled
        if stripe_sub.status == 'canceled':
            print(f"ℹ️  Subscription {subscription_id} is already cancelled")
            # Clean up from database
            users_collection = auth_module.users_collection
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {"stripeSubscriptionId": ""}}
            )
            cancel_user_plan(user_id, engine_type=engine_type)
            
            raise HTTPException(
                status_code=400,
                detail="This subscription has already been cancelled. Your account has been updated."
            )
        
        # Proceed with cancellation
        print(f"🔄 Cancelling subscription {subscription_id} (at_period_end={at_period_end})")
        cancelled_sub = cancel_subscription(subscription_id, at_period_end=at_period_end)
        print(f"✅ Subscription cancelled successfully: {subscription_id}")
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        error_msg = str(e)
        print(f"❌ Stripe cancel error: {error_msg}")
        
        # Provide better error message
        if "No such subscription" in error_msg or "does_not_exist" in error_msg:
            # Subscription doesn't exist in Stripe, update local database
            users_collection = auth_module.users_collection
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$unset": {"stripeSubscriptionId": ""}}
            )
            print(f"🧹 Cleaned up invalid subscription ID from user {user_id}")
            
            raise HTTPException(
                status_code=400, 
                detail="Subscription not found in Stripe. It may have already been cancelled. Your account has been updated."
            )
        raise HTTPException(status_code=400, detail=f"Failed to cancel subscription: {error_msg}")
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error during cancellation: {error_msg}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {error_msg}")

    # Update local user state immediately to provide instant feedback
    if not at_period_end:
        print(f"📝 Updating user plan after immediate cancellation")
        cancel_user_plan(user_id, engine_type=engine_type)
    else:
        # For resumable cancellation, mark as pending immediately so UI shows "Resume Subscription"
        print(f"📝 Marking user plan as pending cancellation locally (resumable)")
        cancel_user_plan(user_id, engine_type=engine_type, is_pending=True)

    return {"cancelled": True, "at_period_end": at_period_end, "engine_type": engine_type}

async def _perform_stripe_sync(user_id: str, email: str, stripe_customer_id: str = None, session_id: str = None):
    """Internal helper to sync user from Stripe with extreme robustness"""
    users_collection = auth_module.users_collection
    print(f"\n--- 🔄 STRIPE SYNC START ({email}) ---")
    
    # Skip Stripe sync for postpaid users - they don't use Stripe subscriptions
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user and user.get("is_postpaid", False):
        print(f"[SYNC] Skipping Stripe sync for postpaid user: {email}")
        return {"success": True, "detail": "Postpaid user - Stripe sync not applicable.", "plan": None}
    
    if session_id:
        print(f"🔍 [SYNC] Called with session_id: {session_id}")
    
    try:
        # 1. Resolve Customer ID and Handle Add-ons
        # If session_id is provided, check if it was an add-on purchase
        if session_id:
            try:
                s = stripe.checkout.Session.retrieve(session_id)
                stripe_customer_id = getattr(s, 'customer', None)
                
                # CHECK FOR ADD-ON SESSION
                meta = getattr(s, 'metadata', {})
                print(f"📦 [SYNC] Session {session_id} Metadata: {meta}")
                
                if meta.get("order_type") == "addon":
                    plan_code = meta.get("plan_code")
                    engine_type = meta.get("engine_type", "transformation")
                    
                    amount = 100.0
                    if plan_code:
                        if "50" in plan_code: amount = 50.0
                        elif "200" in plan_code: amount = 200.0
                    
                    print(f"💰 [SYNC] Processing ADDON credits: {amount} for {email}")
                    from auth import add_addon_credits
                    add_addon_credits(user_id, amount, engine_type=engine_type)
                    
                    # Return success for add-on since it doesn't affect subscriptions
                    return {"success": True, "detail": "Add-on credits applied successfully.", "plan": "Add-on", "credits": amount}
                else:
                    print(f"ℹ️  [SYNC] Session found but not an add-on (order_type={meta.get('order_type')})")
            except Exception as e:
                print(f"⚠️  [SYNC] Error retrieving/processing session {session_id}: {e}")
        
        if not stripe_customer_id:
            print(f"ℹ️  [SYNC] No Stripe customer record found for {email}. Assuming no active sub.")
            # Ensure local state is also clear if no Stripe record exists
            users_collection.update_one({"_id": ObjectId(user_id)}, {"$unset": {"stripeSubscriptionId": ""}})
            cancel_user_plan(user_id, engine_type=None)
            return {"success": True, "detail": "Account synced: No Stripe customer record found.", "plan": None}

        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"stripeCustomerId": stripe_customer_id}})

        # 2. Get Subscriptions
        print(f"🔍 Fetching active subs for {stripe_customer_id}...")
        try:
            subs = stripe.Subscription.list(customer=stripe_customer_id, status='all', limit=20).data
        except Exception as e:
            print(f"❌ Stripe API Error listing subs: {e}")
            return {"success": False, "detail": f"Stripe List Error: {str(e)}"}
            
        print(f"📊 Found {len(subs)} total subscriptions in Stripe records.")
        
        # Robustness: Filter out subscriptions that are set to cancel
        # We treat those as cancelled for the local application state to provide immediate feedback
        active_subs = []
        active_engines_in_stripe = []
        for s in subs:
            # Use dot access and .get() to be ultra-safe
            is_cancelling_bool = getattr(s, 'cancel_at_period_end', False)
            cancel_at_timestamp = getattr(s, 'cancel_at', None)
            status = getattr(s, 'status', 'inactive')
            
            # BROAD DETECTION: If either period-end cancellation is set, or a cancel_at timestamp exists, it's cancelling
            is_cancelling = is_cancelling_bool or (cancel_at_timestamp is not None)
            
            # 🚨 CRITICAL: Skip any subscription that is actually an ADDON
            # We use multiple checks to be ultra-safe
            meta = getattr(s, 'metadata', {}) or {}
            if not meta and hasattr(s, 'get'):
                meta = s.get('metadata', {}) or {}
                
            order_type = meta.get('order_type')
            if order_type == 'addon':
                print(f"⏭️  [STRIPE SYNC] Skipping sub {s.id} - Explicitly marked as ADDON in metadata.")
                continue

            # Also check plan_code if order_type is missing
            plan_code_meta = meta.get('plan_code', '')
            if isinstance(plan_code_meta, str) and plan_code_meta.startswith('ADDON'):
                print(f"⏭️  [STRIPE SYNC] Skipping sub {s.id} - plan_code '{plan_code_meta}' suggests it is an ADDON.")
                continue

            print(f"   - Sub {s.id}: status={status}, cancelling={is_cancelling}, plan_meta={plan_code_meta}")
            
            # Log the full object in case of discrepancy
            if status in ['active', 'trialing', 'past_due']:
                try:
                    # Strip long fields for readable logs but keep important ones
                    debug_info = {
                        "id": s.id,
                        "status": status,
                        "cancel_at_period_end": is_cancelling_bool,
                        "cancel_at": cancel_at_timestamp,
                        "canceled_at": getattr(s, 'canceled_at', None),
                        "current_period_end": getattr(s, 'current_period_end', None),
                        "items_count": len(s.get('items', {}).get('data', []))
                    }
                    print(f"🔍 DEBUG SUB OBJECT: {debug_info}")
                except Exception as log_err:
                    print(f"⚠️  Could not log debug info: {log_err}")

            if status in ['active', 'trialing', 'past_due'] and not is_cancelling:
                active_subs.append(s)
            else:
                if is_cancelling:
                    print(f"🚫 Skipping sub {s.id} because it is marked as CANCELLING. Triggering local pending state...")
                    # Determine engine_type and plan_code for this cancelling sub to keep it in sync
                    meta = s.get('metadata', {})
                    cancelling_engine_type = meta.get('engine_type')
                    if not cancelling_engine_type:
                        # Fallback mapping check
                        items_data = s.get('items', {}).get('data', [])
                        if items_data:
                            price_id = items_data[0].get('price', {}).get('id')
                            # Minimal mapping
                            mapping = {
                                os.getenv("STRIPE_PRICE_T_STARTER"): "transformation",
                                os.getenv("STRIPE_PRICE_T_GROWTH"): "transformation",
                                os.getenv("STRIPE_PRICE_T_SCALE"): "transformation",
                                os.getenv("STRIPE_PRICE_M_STARTER"): "creation",
                                os.getenv("STRIPE_PRICE_M_GROWTH"): "creation",
                                os.getenv("STRIPE_PRICE_M_SCALE"): "creation",
                            }
                            cancelling_engine_type = mapping.get(price_id)
                    
                    # Mark as pending LOCAL cancellation in DB
                    cancel_user_plan(user_id, engine_type=cancelling_engine_type, is_pending=True)
                    
                    # Add to trackers so we don't fully nuke the plan/sub_id
                    if cancelling_engine_type:
                        active_engines_in_stripe.append(cancelling_engine_type)
        
        if not active_subs:
            print(f"ℹ️  [SYNC] No FULLY ACTIVE subscriptions found for customer {stripe_customer_id}.")
            if not active_engines_in_stripe:
                print(f"🧹 [SYNC] No cancelling subscriptions either. Performing global cleanup...")
                users_collection.update_one({"_id": ObjectId(user_id)}, {"$unset": {"stripeSubscriptionId": "", "is_pending_cancellation": ""}})
                cancel_user_plan(user_id, engine_type=None)
                return {"success": True, "detail": "Account synced: No active subscriptions found.", "plan": None}
            else:
                print(f"⏳ [SYNC] Found pending cancellations. Preserving stripeSubscriptionId for Portal access.")
                # Ensure top-level is_pending_cancellation is set if applicable
                users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"is_pending_cancellation": True}})
                pass
        
        print(f"✅ Found {len(active_subs)} Active Sub(s)")
        
        # Sync each active subscription
        latest_plan = None
        latest_credits = None
        
        for sub in active_subs:
            sub_id = sub.id

            # 3. Determine Plan (Extreme robustness)
            plan_code = None
            engine_type = None
            
            # Try metadata first
            meta = sub.get('metadata', {})
            plan_code = meta.get('plan_code')
            engine_type = meta.get('engine_type')
            
            # Try item mapping
            items_data = sub.get('items', {}).get('data', [])
            price_id = None
            amount = 0
            if items_data:
                price_obj = items_data[0].get('price')
                if price_obj:
                    price_id = price_obj.get('id')
                    amount = (price_obj.get('unit_amount') or 0) / 100

            print(f"📦 Data: price={price_id}, meta={plan_code}, amt={amount}")

            # Explicit Mapping (User suggestion: use env IDs)
            mapping = {
                os.getenv("STRIPE_PRICE_T_STARTER"): ("Starter", "transformation"),
                os.getenv("STRIPE_PRICE_T_GROWTH"): ("Growth", "transformation"),
                os.getenv("STRIPE_PRICE_T_SCALE"): ("Scale", "transformation"),
                os.getenv("STRIPE_PRICE_M_STARTER"): ("Starter", "creation"),
                os.getenv("STRIPE_PRICE_M_GROWTH"): ("Growth", "creation"),
                os.getenv("STRIPE_PRICE_M_SCALE"): ("Scale", "creation"),
            }
            
            # Remove None keys from mapping if env vars are missing
            mapping = {k: v for k, v in mapping.items() if k}
            
            res = mapping.get(price_id)
            if res:
                plan_code, engine_type = res
                print(f"✅ Matched Price ID {price_id} to {plan_code} ({engine_type})")
            else:
                print(f"⚠️  No direct mapping found for Price ID {price_id}. Checking fallback mapping...")
                res = mapping.get(price_id) # Should be the same, but for logging
            
            # Fallback if mapping failed but we have metadata
            if not plan_code and meta.get('plan_code'):
                plan_code = meta.get('plan_code')
                engine_type = meta.get('engine_type', 'transformation')

            if not plan_code:
                # Last resort fallback based on amount
                if amount < 200: plan_code = "Starter"
                elif amount < 500: plan_code = "Growth"
                else: plan_code = "Scale"
                if not engine_type: engine_type = "transformation"

            # 4. Finalize updates for this engine
            print(f"📝 Syncing Sub {sub_id}: {plan_code}, {engine_type}")
            update_user_plan(user_id, plan_code, engine_type, subscription_id=sub_id)
            active_engines_in_stripe.append(engine_type)
            
            latest_plan = plan_code
            stats = get_user_usage_stats(user_id, engine_type)
            latest_credits = stats.get('remaining_units')

        # 5. Engine Cleanup: Clear any engine LOCAL that is NOT in Stripe anymore
        current_user = get_user_by_id(user_id)
        if current_user:
            engine_data = current_user.get("engine_data", {})
            print(f"🧹 Sweeping engine data for cleanup. Active in Stripe: {active_engines_in_stripe}")
            for eng_type in list(engine_data.keys()):
                eng_info = engine_data.get(eng_type)
                if not eng_info: continue
                
                # If engine has a plan locally but wasn't found in Stripe's active list
                local_plan = eng_info.get("plan")
                if eng_type not in active_engines_in_stripe and local_plan:
                    print(f"🧹 CLEANUP: Engine '{eng_type}' has local plan '{local_plan}' but NO active sub in Stripe. Cancelling locally...")
                    cancel_user_plan(user_id, engine_type=eng_type)
                else:
                    if local_plan:
                        print(f"✅ Engine '{eng_type}' matches an active sub in Stripe.")

        print("✅ COMPLETED SYNC")
        return {"success": True, "plan": latest_plan, "credits": latest_credits}

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return {"success": False, "detail": str(e)}



@app.post("/api/stripe/manual-sync")
async def manual_sync_subscription(request: dict):
    """Manually sync a user's Stripe subscription robustly."""
    email = request.get("email")
    session_id = request.get("session_id")
    
    if not email and not session_id:
        raise HTTPException(status_code=400, detail="Email or session_id is required")
    
    print(f"🔄 Manual Sync Triggered - Email: {email}, Session: {session_id}")
    
    users_collection = auth_module.users_collection
    user = None
    if email:
        user = users_collection.find_one({"email": email})
    
    if not user and session_id:
        # Resolve user via session as fallback
        try:
            print(f"🔍 [MANUAL-SYNC] Resolving user via session {session_id}")
            session = stripe.checkout.Session.retrieve(session_id)
            customer_id = session.get("customer")
            if customer_id:
                user = users_collection.find_one({"stripeCustomerId": customer_id})
                if user:
                    print(f"✅ [MANUAL-SYNC] Found user {user.get('email')} via customer ID {customer_id}")
        except Exception as e:
            print(f"⚠️ [MANUAL-SYNC] Error resolving user via session: {e}")

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    # Skip for postpaid users - they don't use Stripe subscriptions
    if user.get("is_postpaid", False):
        return {"success": True, "detail": "Postpaid user - Stripe sync not applicable.", "plan": None}

    res = await _perform_stripe_sync(str(user["_id"]), user.get("email"), user.get("stripeCustomerId"), session_id)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["detail"])
    return res


@app.post("/api/stripe/refresh-subscription")
async def refresh_subscription(current_user = Depends(get_current_user)):
    """Authenticated endpoint to refresh subscription status."""
    # Skip for postpaid users - they don't use Stripe subscriptions
    if current_user.get("is_postpaid", False):
        return {"success": True, "detail": "Postpaid user - Stripe subscription not applicable.", "plan": None}
    
    res = await _perform_stripe_sync(str(current_user["_id"]), current_user.get("email"), current_user.get("stripeCustomerId"))
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["detail"])
    return res

@app.get("/api/plans")
async def get_plans():
    """Get all available pricing plans"""
    plans = get_all_plans()
    # Convert ObjectId to string for JSON serialization
    for plan in plans:
        plan["_id"] = str(plan["_id"])
    return plans

@app.get("/api/users/usage")
async def get_usage(engine_type: str = None, current_user = Depends(get_current_user)):
    """Get usage stats for current user, optionally for a specific engine"""
    stats = get_user_usage_stats(str(current_user["_id"]), engine_type=engine_type)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats

@app.get("/api/users/billing-history")
async def get_billing(current_user = Depends(get_current_user)):
    """Get billing history for current user"""
    history = get_billing_history(str(current_user["_id"]))
    for bill in history:
        bill["_id"] = str(bill["_id"])
    return history

@app.post("/api/billing/generate")
async def generate_bill(current_user = Depends(get_current_user)):
    """Manually generate a bill for the current period (for demo)"""
    bill = generate_monthly_bill(str(current_user["_id"]))
    if not bill:
        raise HTTPException(status_code=400, detail="Failed to generate bill")
    bill["_id"] = str(bill["_id"])
    return bill



# ─── AI Content-Aware Resize Utilities ───────────────────────────────────────

from PIL import ImageEnhance, ImageFilter

# Gemini only supports a fixed set of aspect ratios.  Any custom dimension
# must be mapped to the closest supported ratio before calling the API.
GEMINI_RATIOS = {
    "1:1":  1.0,
    "16:9": 16/9,    # 1.7778
    "9:16": 9/16,    # 0.5625
    "4:3":  4/3,     # 1.3333
    "3:4":  3/4,     # 0.75
    "3:2":  3/2,     # 1.5
    "2:3":  2/3,     # 0.6667
    "21:9": 21/9,    # 2.3333
}

GEMINI_NATIVE_RESOLUTIONS = {
    "1:1":   (1024, 1024),
    "16:9":  (1344, 768),
    "9:16":  (768, 1344),
    "4:3":   (1152, 896),
    "3:4":   (896, 1152),
    "3:2":   (1216, 832),
    "2:3":   (832, 1216),
    "21:9":  (1536, 640),
}


def _find_closest_gemini_ratio(target_ratio: float) -> tuple:
    """Map an arbitrary aspect ratio value to the nearest Gemini-supported ratio."""
    if target_ratio < 0.5:
        return "9:16", 9/16
    if target_ratio > 2.5:
        return "21:9", 21/9

    closest_ratio = "1:1"
    closest_val = 1.0
    min_diff = float('inf')
    for ratio_str, ratio_val in GEMINI_RATIOS.items():
        diff = abs(target_ratio - ratio_val)
        if diff < min_diff:
            min_diff = diff
            closest_ratio = ratio_str
            closest_val = ratio_val
    return closest_ratio, closest_val


def get_native_resolution(ratio_str: str) -> tuple:
    """Return the native Gemini resolution for a given ratio string."""
    return GEMINI_NATIVE_RESOLUTIONS.get(ratio_str, (1024, 1024))


def validate_aspect_ratio_smart(aspect_ratio: str) -> tuple:
    """
    Validate and map custom aspect ratios / dimensions to Gemini-supported
    formats.  Accepts multiple input formats:
      - Direct Gemini ratio:  "16:9", "1:1"
      - Named preset:        "landscape", "story", "square" …
      - pWxH format:         "p288x608"
      - WxH format:          "1920x1080"
      - W:H arbitrary:       "288:608"

    Returns (gemini_ratio_str, target_dims | None, gemini_ratio_val)
    """
    # 1. Direct Gemini ratio pass-through
    if aspect_ratio in GEMINI_RATIOS:
        return aspect_ratio, None, GEMINI_RATIOS[aspect_ratio]

    # 2. Named semantic presets
    named_presets = {
        "landscape":   ("16:9", (1920, 1080), 16/9),
        "story":       ("9:16", (1080, 1920), 9/16),
        "square":      ("1:1",  (1024, 1024), 1.0),
        "portrait":    ("3:4",  (768,  1024), 3/4),
        "ultrawide":   ("21:9", (2560, 1080), 21/9),
        "billboard":   ("16:9", (1920, 1080), 16/9),
        "poster":      ("2:3",  (800,  1200), 2/3),
        "banner":      ("21:9", (2100, 900),  21/9),
        "kiosk":       ("9:16", (1080, 1920), 9/16),
        "menu_board":  ("16:9", (1920, 1080), 16/9),
    }
    if aspect_ratio.lower() in named_presets:
        return named_presets[aspect_ratio.lower()]

    # 3. pWxH format (e.g. "p288x608") — used by pixel-specific presets
    if aspect_ratio.lower().startswith("p") and "x" in aspect_ratio.lower():
        try:
            dims_part = aspect_ratio[1:]
            w_str, h_str = dims_part.lower().split("x")
            width, height = int(w_str), int(h_str)
            actual_ratio = width / height
            closest_ratio, closest_val = _find_closest_gemini_ratio(actual_ratio)
            return closest_ratio, (width, height), closest_val
        except (ValueError, ZeroDivisionError):
            pass

    # 4. WxH format (e.g. "800x600") — from custom dimension inputs
    if "x" in aspect_ratio.lower() and not aspect_ratio.lower().startswith("p"):
        try:
            w_str, h_str = aspect_ratio.lower().split("x")
            width, height = int(w_str), int(h_str)
            actual_ratio = width / height
            closest_ratio, closest_val = _find_closest_gemini_ratio(actual_ratio)
            return closest_ratio, (width, height), closest_val
        except (ValueError, ZeroDivisionError):
            pass

    # 5. Fallback: W:H colon format (e.g. "288:608")
    try:
        width, height = map(int, aspect_ratio.split(':'))
        target_ratio = width / height
        closest_ratio, closest_val = _find_closest_gemini_ratio(target_ratio)
        # If both values are >= 100 treat them as pixel dimensions
        if width >= 100 and height >= 100:
            return closest_ratio, (width, height), closest_val
        return closest_ratio, None, closest_val
    except (ValueError, ZeroDivisionError):
        return "1:1", None, 1.0


# --- Gemini Helper Constants & Functions ---
GEMINI_RATIOS: Dict[str, float] = {
    "1:1": 1.0,   "16:9": 16/9, "9:16": 9/16, "4:3": 4/3,
    "3:4": 3/4,   "3:2": 3/2,   "2:3": 2/3,   "21:9": 21/9,
    "4:5": 0.8,   "5:4": 1.25
}

GEMINI_NATIVE_RESOLUTIONS: Dict[str, Tuple[int, int]] = {
    "1:1":   (1024, 1024),
    "16:9":  (1344, 768),
    "9:16":  (768, 1344),
    "4:3":   (1152, 896),
    "3:4":   (896, 1152),
    "3:2":   (1216, 832),
    "2:3":   (832, 1216),
    "21:9":  (1536, 640),
}

def get_native_resolution(gemini_ratio: str) -> Tuple[int, int]:
    """Return optimized native resolution for a Gemini ratio string."""
    return GEMINI_NATIVE_RESOLUTIONS.get(gemini_ratio, (1024, 1024))

def get_aspect_ratio_data(ratio_str: str) -> Tuple[str, Optional[Tuple[int, int]], float]:
    """
    Parse a ratio string (e.g., '16:9' or '864:288') into 
    (gemini_ratio, target_dims, float_ratio).
    """
    try:
        if ":" in ratio_str:
            parts = ratio_str.split(":")
            w, h = int(parts[0]), int(parts[1])
            val = w / h
            # Find closest Gemini ratio
            closest_ratio = "1:1"
            min_diff = float("inf")
            for r, v in GEMINI_RATIOS.items():
                diff = abs(v - val)
                if diff < min_diff:
                    min_diff = diff
                    closest_ratio = r
            
            # If it's a standard Gemini ratio (within 5%), use its name
            if min_diff < 0.05:
                return closest_ratio, (w, h), val
            return closest_ratio, (w, h), val
        return "1:1", None, 1.0
    except (ValueError, ZeroDivisionError):
        return "1:1", None, 1.0


def build_openai_outpaint_prompt(
    user_prompt: str,
    target_width: int,
    target_height: int,
    source_dims: Optional[Tuple[int, int]] = None,
) -> str:
    """
    Prompt for OpenAI gpt-image-2 outpainting.
    Core principle: CONTINUE the existing edge pixels — never invent new content.
    The model must sample the left/right edges of the visible image and extend them
    outward seamlessly. Kept entirely separate from all Gemini prompts.
    """
    ar = target_width / target_height
    if ar >= 3.0:
        fill_desc = "large transparent areas on both the left and right (the target is very wide)"
    elif ar >= 1.5:
        fill_desc = "transparent areas on the left and right"
    elif ar <= 0.67:
        fill_desc = "transparent areas on the top and bottom"
    else:
        fill_desc = "transparent areas on the sides"

    src_note = ""
    if source_dims:
        sw, sh = source_dims
        src_note = (
            f"The source image ({sw}×{sh}px) has been scaled and centred on this canvas. "
        )

    brand_line = f"\n\nBRAND / STYLE CONTEXT (use only to inform tone — do NOT add new content): {user_prompt}" if user_prompt and user_prompt.strip() else ""

    return f"""TASK: Intelligent layout adaptation and seamless outpainting.
PRIMARY TARGET: {target_width}×{target_height}px.
RATIO TARGET: {target_width/target_height:.4f}:1 (must be matched as closely as possible in composition).
IMPORTANT: Preserve ALL source content with zero loss. No cropping of meaningful content.

Your job is not simple side padding. You must intelligently re-balance layout so text, logos, CTA and hero elements read clearly in the final wide canvas.
Extend this image to fill {target_width}×{target_height}px by filling the {fill_desc}.

{src_note}

HOW TO FILL THE TRANSPARENT AREAS:
1. Look at the leftmost visible column of pixels in the existing image. Note the exact colour, texture, gradient, brightness, and any partial shapes or patterns present there. Extend that content leftward, following the same visual logic.
2. Look at the rightmost visible column of pixels. Do the same extending rightward.
3. Preserve every perspective line, horizon line, gradient direction, and lighting angle from the original through into the extended area.
4. The join between the original image and the extension must be completely invisible — no colour shift, no brightness jump, no edge artefact.

THE MOST IMPORTANT RULE:
Only continue what is already visually present at the image edges. If the edge is a plain colour gradient, extend that gradient. If it is a studio backdrop, continue the backdrop. If it is a product on white, extend the white. Never introduce a scene, environment, landscape, sky, building, or background element that is not already visible at that edge.

INTELLIGENT CONTENT PLACEMENT RULES:
1) Keep every original text block, logo and brand mark present exactly once.
2) Reposition spacing and margins so text remains readable at billboard distance.
3) Keep the primary message and hero element dominant, not tiny and not centered as a narrow strip.
4) Use the full canvas width intentionally; avoid empty dead zones.
5) Maintain original brand colors, style and typography hierarchy.
6) VERTICAL SAFETY ZONE: You must keep ALL text, faces, logos, and critical product elements within the vertical middle 50% of the canvas. Do NOT place text near the very top or very bottom edge, as it may be cropped.

STRICT PROHIBITIONS:
✗ Do NOT invent new background content (sky, clouds, buildings, landscapes, abstract textures) unless that exact content is visible at the image edge
✗ Do NOT move, resize, crop, or alter the central subject in any way
✗ Do NOT duplicate, mirror, or tile any element from the original image
✗ Do NOT add solid colour bars, vignettes, borders, or decorative frames
✗ Do NOT add new objects, people, logos, or text not already in the image
✗ Do NOT change the colour temperature, saturation, or exposure of the original content{brand_line}

OUTPUT: One seamless flat digital graphic at exactly {target_width}×{target_height}px. The result must look like a single image that was always this size."""


def build_openai_banner_prompt(
    user_prompt: str,
    target_width: int,
    target_height: int,
    source_dims: Optional[Tuple[int, int]] = None,
) -> str:
    """
    Prompt for OpenAI banner-generation mode (AR > 3.5).

    The source image is sent as a REFERENCE via the all-white mask technique —
    OpenAI regenerates the full canvas while treating the attached image as the
    complete design brief. The AI must extract elements and re-compose them as a
    proper ultra-wide signage banner, NOT just centre the source image.
    """
    src_note = ""
    if source_dims:
        sw, sh = source_dims
        src_note = f"The reference image attached is {sw}×{sh}px. "

    ar = target_width / target_height
    if ar >= 6:
        width_desc = "extremely ultra-wide"
        layout_hint = (
            "LEFT zone: main visual / product (full height, ~25 % of width). "
            "CENTRE-LEFT zone: headline text, large and bold (~30 % of width). "
            "CENTRE-RIGHT zone: supporting copy or sub-headline (~25 % of width). "
            "RIGHT zone: logo + brand name (~20 % of width). "
            "Background: brand colour / gradient from the reference, spanning the entire width seamlessly."
        )
    elif ar >= 4:
        width_desc = "ultra-wide"
        layout_hint = (
            "LEFT zone: main visual / product (~35 % of width). "
            "CENTRE zone: headline text, large and clearly legible (~35 % of width). "
            "RIGHT zone: logo + call-to-action or tagline (~30 % of width). "
            "Background: brand colour / gradient from the reference, spanning full width."
        )
    else:
        width_desc = "wide"
        layout_hint = (
            "LEFT zone: main visual or product (~40 % of width). "
            "RIGHT zone: headline text + logo (~60 % of width). "
            "Background: brand colour / gradient from reference."
        )

    brand_line = (
        f"\n\nBRAND / CAMPAIGN CONTEXT: {user_prompt}"
        if user_prompt and user_prompt.strip()
        else ""
    )

    return f"""Create a professional {width_desc} digital signage banner.
PRIMARY TARGET: {target_width}×{target_height}px.
RATIO TARGET: {target_width/target_height:.4f}:1 (compose as close as possible to this ratio).
MANDATORY: keep all important source content; no content loss.

{src_note}The attached image is the COMPLETE DESIGN REFERENCE — it contains all brand elements: product visuals, headline text, logo, tagline, colour palette, and visual style. Do not invent anything new; extract everything from the reference.

LAYOUT — divide the {target_width}px width into zones:
{layout_hint}

COMPOSITION RULES (INTELLIGENT PLACEMENT):
• Every text element from the reference must appear in the banner at a size readable on a large digital display — never shrunken or cropped
• The main subject (product, person, key visual) must be fully visible at a dominant size, not a thumbnail
• Text must be razor-sharp and legible — same wording, same brand fonts and colours as the reference
• The background must feel intentional: extend the brand gradient or colour field across the full width with no seam or empty area
• The banner must look like a professionally art-directed piece, not a cropped or tiled photo
• Distribute elements across zones with clear visual hierarchy; avoid placing all source content as one centered block
• VERTICAL SAFETY ZONE: You must keep ALL text, faces, logos, and critical product elements within the vertical middle 50% of the canvas. Do NOT place text near the very top or very bottom edge, as it may be cropped.

STRICT PROHIBITIONS:
✗ Do NOT centre the source image and fill sides with generated scenery
✗ Do NOT stretch, tile, mirror, or repeat any element
✗ Do NOT add people, objects, text, or logos not present in the reference
✗ Do NOT leave large empty or featureless areas — every zone must contribute
✗ Do NOT add borders, vignettes, or watermarks{brand_line}

OUTPUT: One flat, ready-to-display {target_width}×{target_height}px digital signage banner with all elements from the reference intelligently composed across the full width."""



def build_layout_prompt(prompt: str, target_dims: Optional[Tuple[int, int]], validated_ratio: str) -> str:
    """
    PixExact v8: Ultra-Smart Intelligent Content Placement Engine.
    If no custom dims, returns the raw prompt (standard ratios handled by GemImg).
    """
    if not target_dims:
        return prompt

    tw, th = target_dims
    actual_ratio = tw / th

    if actual_ratio < 0.4 or actual_ratio > 2.5:
        safe_pct = 40
    elif actual_ratio < 0.6 or actual_ratio > 1.8:
        safe_pct = 50
    else:
        safe_pct = 60

    orientation = "TALL PORTRAIT" if th > tw else "WIDE LANDSCAPE" if tw > th else "SQUARE"
    safe_width = int(tw * (safe_pct / 100))
    safe_height = int(th * (safe_pct / 100))
    edge_width_px = (tw - safe_width) // 2
    edge_height_px = (th - safe_height) // 2

    layout_prefix = f"""[PIXEXACT v8 | {tw}x{th}px | {orientation}]
STRICT RULE: PLACE CONTENT ONCE ONLY. NO DUPLICATION.

1. SOURCE ISLAND: Place all logos, text, and main subjects in the CENTER safe zone.
2. NEGATIVE SPACE: Extend the background to the edges. Do NOT put any branding in extensions.
3. NO STACKING: The design must be a single coherent block, not a split-screen or multi-tier layout.

NEGATIVE CONSTRAINTS: NO duplicated logos, NO stacked text, NO mirrored subjects, NO footer branding.

USER REQUEST:
{prompt}

DELIVERY: Pixel-perfect {tw}×{th} output."""

    return layout_prefix



def build_image_adaptation_prompt(
    prompt: Optional[str],
    target_dims: Optional[Tuple[int, int]],
    validated_ratio: str,
) -> str:
    """
    PixExact v10 — IMAGE ADAPTATION mode.
    Concise, front-loaded prompt: most critical rule first.
    Prevents content duplication on tall portrait and wide landscape outputs.
    """
    tw, th = target_dims or get_native_resolution(validated_ratio)
    actual_ratio = tw / th

    is_tall         = th > tw * 1.2
    is_extreme_tall = th > tw * 1.5  # Lowered from 1.8 to capture 9:16 and 1:2
    is_wide         = tw > th * 1.2
    is_extreme_wide = tw > th * 2.0  # Lowered from 2.5 to capture 1472x480 (3.07) and 2640x288 (9.17)
    orientation     = "TALL PORTRAIT" if is_tall else "WIDE LANDSCAPE" if is_wide else "SQUARE"

    user_note = f" Additional instruction: {prompt}." if prompt else ""

    # How much extra space needs filling
    extra_h = max(0, th - tw)
    extra_w = max(0, tw - th)

    if is_extreme_tall:
        # Ultra-surgical Zonal Prompting for 1:2+ ratios
        fill_note = (
            f"SURGICAL TASK: The 1:2+ ratio canvas is {tw}x{th}px. "
            "You MUST divide the layout into 3 VERTICAL ZONES:\n"
            f"1. TOP ZONE (rows 0 to {extra_h // 2}): BACKGROUND EXTENSION. Fill this area by natively extending the background colors, gradients, and textures from the source image. DO NOT leave it black. NO NEW OBJECTS. NO LOGOS.\n"
            f"2. MIDDLE ZONE (rows {extra_h // 2} to {th - (extra_h // 2)}): SOURCE CONTENT. Place the ENTIRE design here as a SINGLE LOCKED RECTANGLE. Do NOT break apart logos or text.\n"
            f"3. BOTTOM ZONE (rows {th - (extra_h // 2)} to {th}): BACKGROUND EXTENSION. Fill this area by natively extending the background colors, gradients, and textures from the source image. DO NOT leave it black. NO NEW OBJECTS. NO LOGOS.\n"
            "PROHIBITION: Zero content duplication. Branding, logos, and subject matter MUST stay together in the MIDDLE ZONE."
        )
    elif is_extreme_wide:
        # Ultra-surgical Horizontal Zonal Prompting for ultra-wide signs (ratio > 2.0)
        # More explicit pixel math to prevent Gemini from ignoring the instructions
        fill_note = (
            f"ULTRA-WIDE SIGNAGE TASK: Canvas is {tw}x{th}px (ratio {tw/th:.2f}:1).\n"
            f"This is an extreme wide-format digital sign.\n"
            f"The source image content occupies the CENTER {th}px-high zone.\n"
            f"LEFT EXTENSION: {extra_w // 2}px — fill by continuing the background color/gradient from the left edge of the source. NO logos, NO text, NO subjects.\n"
            f"RIGHT EXTENSION: {extra_w - extra_w // 2}px — fill by continuing the background color/gradient from the right edge of the source. NO logos, NO text, NO subjects.\n"
            f"RESULT: A single wide graphic where the original content sits centered, flanked by clean background extensions.\n"
            f"PROHIBITION: Do NOT mirror or tile the source image. Do NOT repeat any element."
        )
    elif is_wide:
        # Wide landscape (ratio 1.2-2.0)
        fill_note = (
            f"WIDE SIGNAGE TASK: Canvas is {tw}x{th}px (ratio {tw/th:.2f}:1).\n"
            f"Scale the source to exactly {th}px height. Centre it horizontally.\n"
            f"Fill the {extra_w}px of empty space (split left/right) by extending the background ONLY — use the edge colors/gradients from the source image.\n"
            f"Do NOT use edge mirroring. Do NOT repeat any content. Blend naturally."
        )
    elif is_tall:
        fill_note = (
            f"The canvas is {tw}x{th}px ({orientation}). "
            f"Place the source image as a single composition, centred vertically. "
            f"The ~{extra_h}px gap above and below must be NATIVELY FILLED by extending the "
            "background textures, colors, and gradients from the source image. Ensure a seamless blend."
        )
    else:
        fill_note = (
            f"The canvas is {tw}x{th}px. "
            "Scale and recompose the source image to fill it exactly while maintaining all text and logos."
        )

    return (
        f"TASK: ADAPT IMAGE TO {tw}x{th}px ({orientation})\n"
        "ABSORUTE CONSTRAINT: LOGOS AND TEXT MUST APPEAR EXACTLY ONCE.\n"
        "\n"
        "COLOR FIDELITY LOCK (MANDATORY):\n"
        "- Use the EXACT color palette from the source image.\n"
        "- Do NOT shift the hue, saturation, or white balance.\n"
        "- The background extension MUST be a pixel-perfect color match to the source edges.\n"
        "\n"
        "ARRANGEMENT LOCK (LAYOUT FIDELITY):\n"
        "- Keep the original spacing and alignment between the person, the text, and the logos.\n"
        "- Do NOT move elements relative to each other within the source block.\n"
        "\n"
        "WHAT YOU MUST PRESERVE (SEMANTIC LOCK - ZERO LOSS):\n"
        "- The SAME subject matter, logos, icons, and scenery—NOTHING removed or swapped.\n"
        "- The SAME people and faces—100% identical to the source.\n"
        "- EVERY SINGLE word of text (same font, same placement).\n"
        "- EVERY logo and icon (do NOT omit the Mastercard logo, the QR code, or any brand marks).\n"
        "- The SAME color palette and overall graphic style.\n"
        "\n"
        "1. CENTER THE DESIGN: Place the entire source image content as a single locked block in the center of the canvas.\n"
        "2. NATIVE BACKGROUND FILL: Outpaint and extend the background ONLY. Use the existing colors and patterns to fill the gaps. NO BLACK BARS.\n"
        "3. NO CONTENT CLONES: Avoid repeating the subject, logo, or text in the extension zones.\n"
        "\n"
        f"FILL NOTE: {fill_note}\n"
        "\n"
        "HARD PROHIBITIONS:\n"
        "❌ Do NOT redraw, redesign, or artistically reinterpret the content.\n"
        "❌ Do NOT change the person's face or clothing.\n"
        "❌ Do NOT remove any text, logos, people, or products from the original design.\n"
        "❌ Do NOT shift the background colors or apply a different theme.\n"
        "❌ Do NOT break the design into separate stacked pieces.\n"
        "\n"
        "PROVISION: Output must be a single, non-mirrored, non-stacked digital graphic.\n"
        f"Source additional task: {user_note}"
    )




# ═══════════════════════════════════════════════════════════════════════════
# IMAGE EXTENSION HELPERS
# ═══════════════════════════════════════════════════════════════════════════


def build_outpaint_prompt(user_prompt: str, target_dims: tuple, source_dims: tuple = None) -> str:
    """
    Prompt for Gemini outpainting on a pre-composited canvas.
    The source content is centred and sharp; surrounding areas are blurred placeholders.
    """
    tw, th = target_dims
    is_wide = tw > th * 1.3
    is_tall = th > tw * 1.3
    if is_wide:
        extend_dir = "left and right sides"
    elif is_tall:
        extend_dir = "top and bottom"
    else:
        extend_dir = "all sides"

    ratio_context = ""
    if source_dims:
        sw, sh = source_dims
        ratio_context = (
            f"\nINPUT: source image {sw}x{sh}px ({sw/sh:.2f}:1 ratio) → "
            f"target canvas {tw}x{th}px ({tw/th:.2f}:1 ratio). "
            f"You must extend content to fill the additional {abs(tw-sw)}x{abs(th-sh)}px of space."
        )

    extra = f"\nAdditional instruction: {user_prompt}" if user_prompt and user_prompt.strip() else ""
    return f"""[OUTPAINT | {tw}x{th}px]{ratio_context}
The attached image is a pre-composited {tw}x{th}px canvas. The original content is centred and sharp. The {extend_dir} contain a blurred colour approximation showing the background to extend.

YOUR TASK — replace the blurred {extend_dir} with seamless, intelligent content:
• Architecture / buildings → extend walls, facades, windows with correct vanishing-point perspective. Do NOT tile or repeat building sections.
• Sky / outdoor / atmosphere → continue clouds, gradients, ambient light naturally.
• Ground / road / floor → follow the horizon line and surface texture to the edges.
• Solid or gradient studio background → blend the colour smoothly, no seam, no tone jump.
• The full result must read as ONE seamless wide-format digital sign — no visible join anywhere.

PRESERVE the centred content (logos, text, products, subjects) exactly as placed. Do not move, scale, or repeat any element.

PROHIBITIONS:
✗ No mirroring or flipping of any element
✗ No tiling or copy-pasting of content blocks
✗ No black bars, white bars, or solid-colour padding
✗ No hard colour jump at the seam between original and extension{extra}

OUTPUT: One seamless flat digital graphic at exactly {tw}x{th}px."""



def build_openrouter_resize_prompt(
    source_dims: Tuple[int, int],
    target_dims: Optional[Tuple[int, int]],
    user_context: Optional[str] = None,
    validated_ratio: str = "1:1"
) -> str:
    """
    Build OpenRouter resize prompt using the robust template style requested
    by the user (from the provided FastAPI reference implementation).
    """
    src_w, src_h = source_dims
    tw, th = target_dims or get_native_resolution(validated_ratio)
    context = (user_context or "").strip()

    prompt = f"""TASK (read carefully):
Redraw the input image as a NEW composition at exactly
{tw} x {th} pixels. 

CORE INSTRUCTIONS:
Preserve the input image exactly as the visual source. Keep all logos, text, branding, objects, colors, and composition unchanged. Only adapt layout to fit the target resolution with native edge extension and zero distortion.

WHAT YOU MUST PRESERVE (semantic lock):
- The same subject matter, logos, icons, diagrams, products, people, and
  scenery—nothing important removed or swapped out.
- The same readable text (same words; same language). Do not change copy,
  spelling, or branding.
- The same color palette, contrast level, and overall graphic style (flat vs
  photo, illustration style, etc.).
- The same meaning: it should read as the same ad, slide, banner, or asset.

WHAT YOU SHOULD DO (layout + redraw):
- Output must look **freshly rendered** for this canvas size: clean edges,
  appropriate typography scale for {tw}x{th}, balanced
  margins—not a smeared upscale/downscale artifact.
- **Preserve the main focal point** (hero, headline, primary logo, key
  product): keep it dominant and in roughly the same visual priority as in
  the source unless the new aspect ratio forces minor shifts.
- If source aspect ratio ({src_w}:{src_h}) differs from target
  ({tw}:{th}), use **intelligent rearrangement**: reflow
  blocks, adjust spacing, stack or align elements, redistribute background—so
  the full message still fits without cropping important content.
- If aspect ratios are close, prefer **minimal change**: proportional scaling
  and gentle spacing tweaks; keep composition and focus aligned with original.
- Background may extend or simplify to fill the frame if it stays consistent
  with the original style (no unrelated new scenes).

INTELLIGENT CANVAS MAPPING RULES (MANDATORY):
- Intelligently place existing elements so the final design covers the FULL {tw}x{th} canvas with no dead zones.
- Do NOT stretch or squeeze logos, people, products, or text. Keep original proportions.
- Do NOT add new elements, and do NOT remove required elements.
- Do NOT duplicate semantic elements (no repeated logos, CTA, subject, or text blocks).
- Avoid obvious leftover empty side/top/bottom spaces; fill naturally with source-consistent continuation only.
- Keep all element relationships coherent so the result feels intentionally laid out for this canvas.

HARD DON'TS:
- Do not crop out logos, faces, legal text, or key product areas.
- Do not replace elements with different objects or invent new messaging.
- Do not apply a different art direction (e.g. photorealistic if source is flat
  graphic), heavy filters, or "make it prettier" redesigns.
- Do not leave unused blank regions or artificial padding bands.

OUTPUT:
- Exactly {tw} x {th} pixels.
- One coherent image; no collage seams or watermarks unless in source.

USER CONTEXT (optional; must not contradict rules above):
{context}
""".strip()

    return prompt



def build_ai_recompose_prompt(user_prompt: str, target_dims: tuple, validated_ratio: str) -> str:
    """
    Build a highly-detailed AI prompt that instructs Gemini to ADAPT the
    source image into a new aspect ratio while preserving ALL content.
    """
    tw, th = target_dims
    orientation = "TALL VERTICAL" if th > tw else "WIDE HORIZONTAL" if tw > th else "SQUARE"

    recompose_prompt = f"""TASK: Resize the attached image to {tw}x{th} pixels ({validated_ratio}, {orientation}).

You are performing a SIMPLE RESIZE/CANVAS EXTENSION operation. This is NOT a creative task.

WHAT TO DO:
- Take the source image and fit it into a {tw}x{th} canvas
- If the aspect ratio changes, extend the background edges to fill the new space
- Keep the image FLAT, STRAIGHT, and FRONT-FACING — exactly as the original
- Maintain every pixel of the original content

ABSOLUTE PROHIBITIONS (DO NOT DO ANY OF THESE):
❌ Do NOT rotate, tilt, skew, or apply ANY perspective transform
❌ Do NOT place the image at an angle
❌ Do NOT add ANY background pattern, texture, or decoration
❌ Do NOT create a "photo on a surface" or "card on a table" effect
❌ Do NOT add frames, borders, shadows, or 3D effects
❌ Do NOT regenerate, redraw, or artistically reinterpret the content
❌ Do NOT change ANY text — keep exact same words, spelling, font, size, color
❌ Do NOT duplicate, mirror, or repeat any foreground subject, logo, or text. Each element must appear exactly once.
❌ Do NOT add black bars, white bars, or colored padding
❌ Do NOT crop or remove any part of the image
❌ Do NOT add physical mockups, screens, monitors, kiosks
❌ Do NOT add watermarks or signatures

WHAT YOU ARE ALLOWED TO DO:
✅ Extend the existing background color/gradient/pattern to fill new space
✅ Adjust spacing and margins around existing content
✅ Scale the composition proportionally if needed
✅ VERTICAL SAFETY ZONE: You must keep ALL text, faces, logos, and critical product elements within the vertical middle 50% of the canvas. Do NOT place text near the very top or very bottom edge, as it may be cropped.

OUTPUT REQUIREMENTS:
- Resolution: exactly {tw}x{th} pixels
- The image must be FLAT and RECTANGULAR — no 3D, no angles, no perspective
- Content must fill the entire canvas edge-to-edge
- Crystal clear, sharp output — no blur, no pixelation, no artifacts
- All text must be razor-sharp and fully legible"""

    if user_prompt and user_prompt.strip():
        recompose_prompt += f"\n\nADDITIONAL INSTRUCTIONS: {user_prompt}"

    return recompose_prompt

def build_vertex_resize_prompt(validated_ratio: str) -> str:
    """
    Vertex AI-specific prompt for the resize/transformation use case.
    Used when the Vertex AI fallback is activated during resize operations.
    """
    return (
        f"Recreate the provided image in the target aspect ratio: {validated_ratio}.\n\n"
        "Preserve all original visual elements exactly as they are, including shapes, objects, "
        "text, logos, QR codes, and design components. Do not alter, redesign, or restyle any element.\n\n"
        "Maintain the original color scheme, typography, proportions of elements, and visual identity.\n\n"
        "You may intelligently reposition, scale, or adjust spacing between elements only as needed "
        "to fit the new aspect ratio, ensuring a clean and balanced composition.\n\n"
        "Do not crop out or remove any existing content. Do not introduce any new elements.\n\n"
        "Logos, QR codes, and critical brand elements must remain pixel-accurate and unmodified.\n\n"
        "VERTICAL SAFETY ZONE: You must keep ALL text, faces, logos, and critical product elements within the vertical middle 50% of the canvas. Do NOT place text near the very top or very bottom edge, as it may be cropped.\n\n"
        "The final output should look like a natural, professionally adapted version of the original "
        "image for the new aspect ratio, not a distorted or stretched transformation."
    )
def safe_scale_to_exact(image_bytes: bytes, target_width: int, target_height: int) -> bytes:
    """
    Scale AI output to exact target dimensions using LANCZOS.
    No cropping, no padding — progressive upscaling for quality.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    src_w, src_h = img.size
    if src_w <= 0 or src_h <= 0:
        raise ValueError("Invalid source image dimensions")

    # Skip if already exact
    if src_w == target_width and src_h == target_height:
        return image_bytes

    scale_factor = max(target_width / src_w, target_height / src_h)
    print(f"📏 [SCALE] Source: {src_w}x{src_h} → Target: {target_width}x{target_height} (scale: {scale_factor:.2f}x)")

    # Progressive upscaling: scale in 1.5x steps for better quality
    # This preserves detail much better than one giant jump
    if scale_factor > 1.6:
        current_w, current_h = src_w, src_h
        step = 1.5
        while True:
            next_w = int(current_w * step)
            next_h = int(current_h * step)
            # If the next step would overshoot, just go to final target
            if next_w >= target_width or next_h >= target_height:
                break
            img = img.resize((next_w, next_h), Image.Resampling.LANCZOS)
            current_w, current_h = next_w, next_h
            print(f"  📐 [SCALE] Progressive step: {current_w}x{current_h}")

    # Final resize to exact target
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Adaptive sharpening: stronger for larger upscales
    if scale_factor > 2.0:
        sharpness_amount = 1.4
    elif scale_factor > 1.5:
        sharpness_amount = 1.3
    elif scale_factor > 1.0:
        sharpness_amount = 1.2
    else:
        sharpness_amount = 1.1  # Downscale: very gentle

    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness_amount)

    # Subtle detail enhancement for upscaled images
    if scale_factor > 1.3:
        detail_filter = ImageFilter.DETAIL
        img = img.filter(detail_filter)

    # Preserve contrast (scaling can wash out colors)
    if scale_factor > 1.5:
        contrast_enhancer = ImageEnhance.Contrast(img)
        img = contrast_enhancer.enhance(1.05)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG", optimize=True)
    print(f"  ✅ [SCALE] Final output: {target_width}x{target_height}, sharpness={sharpness_amount}")
    return buffer.getvalue()


@app.post("/api/resize", response_class=JSONResponse)
async def resize_image(
    aspect_ratio: str = Form("1:1", description="Target aspect ratio, e.g., '16:9', '1:1', '4:3'"),
    engine_type: str = Form("transformation", description="Engine type: 'transformation' or 'creation'"),
    file: UploadFile = File(None),  # Optional for creation engine
    prompt: str = Form(None, description="Custom prompt for image editing/generation. Required for creation engine."),
    current_user = Depends(get_current_user)
):
    """
    Endpoint to resize or edit an image intelligently using Gemini 3 Pro (Nano Banana Pro).
    
    Transformation Engine:
    - Requires image upload
    - No custom prompt (uses default aspect ratio transformation)
    - Purpose: Pure image resizing/transformation
    
    Creation Engine:
    - Requires custom prompt
    - Image upload is optional
    - Can generate from prompt alone OR transform image with custom prompt
    """
    global client

    # Enforce engine allocation at API level so direct callers cannot bypass UI route guards.
    allocated_engines = (
        (current_user.get("_org_context", {}) or {}).get("selected_engines")
        or current_user.get("available_engines")
        or current_user.get("engine_access")
        or ["transformation", "creation"]
    )
    if isinstance(allocated_engines, list) and allocated_engines:
        if engine_type not in allocated_engines:
            raise HTTPException(
                status_code=403,
                detail=f"Engine '{engine_type}' is not allocated for this user",
            )

    # Legacy Glenn interception (kept as commented reference; do not remove):
    # user_email = str(current_user.get("email", "")).lower()
    # user_domain = user_email.split("@")[-1] if "@" in user_email else ""
    #
    # # ── Glenn Pipeline Interception ──────────────────────────────────────
    # GLENN_DOMAINS = ["fmctv.co.nz"]
    # GLENN_EMAILS = ["muhammadhamzafaisal146@gmail.com", "richard.moore@oohmedia.com.au"]
    # is_glenn = user_domain in GLENN_DOMAINS or user_email in GLENN_EMAILS
    # if is_glenn and file:
    #     print(f"[GLENN INTERCEPT] Detected Glenn user ({user_email}) — routing to Glenn pipeline")
    
    # ── Glenn Pipeline (now available to all users) ──────────────────────
    
    if file:
        print(f"[GLENN PIPELINE] Using advanced Glenn image processing")
        
        GLENN_PROVIDER = os.getenv("GLENN_PROVIDER", "google").lower().strip()
        GLENN_MODELS = [
            "gemini-3-pro-image-preview",
            "gemini-3.1-flash-image-preview",
        ]
        
        gemini_aspect_ratio, target_dims, gemini_ratio_val = validate_aspect_ratio_smart(aspect_ratio)
        
        user_id = str(current_user["_id"])
        is_postpaid = current_user.get("is_postpaid", False)
        image_bytes = await file.read()
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Max 10MB.")

        pil_image = await run_blocking(Image.open, io.BytesIO(image_bytes))
        src_w, src_h = pil_image.size
        max_dim = max(src_w, src_h)

        has_custom_prompt = bool(prompt and prompt.strip()) and engine_type == "creation"

        # Match Visual-Engine pricing logic:
        # - 4 credits: plain transformation (image-only) or prompt-only generation
        # - 6 credits: image + prompt edit (creation engine with a custom prompt)
        if is_postpaid:
            cost = 1.0
        elif engine_type == "creation":
            cost = 6.0 if has_custom_prompt else 4.0
        else:
            cost = 4.0
        
        # Credit check — only for prepaid users (postpaid users have unlimited usage)
        if not is_postpaid:
            # Prepaid user: check credits
            engine_data = current_user.get("engine_data", {})
            target_engine_info = engine_data.get(engine_type, {})
            engine_credits = target_engine_info.get("credits", {}) if target_engine_info else {}
            if not engine_credits and current_user.get("engineType") == engine_type:
                engine_credits = current_user.get("credits", {})
            remaining = float(engine_credits.get("remaining_units", 0.0))
            if remaining < cost:
                raise HTTPException(status_code=429, detail=f"Insufficient credits. Need {cost}, have {remaining}")
        
        try:
            if target_dims:
                tw, th = target_dims
            else:
                tw, th = get_native_resolution(gemini_aspect_ratio)
            

            # ── Glenn-specific resize prompt (Smart Routing) ────────────────
            is_wide_landscape = tw > th * 1.5
            is_extreme_portrait = th > tw * 1.5
            
            if is_wide_landscape:
                # Use OpenRouter resize prompt for wide landscapes (best for reflow)
                resize_prompt = build_openrouter_resize_prompt(
                    source_dims=(src_w, src_h),
                    target_dims=(tw, th),
                    user_context=prompt if has_custom_prompt else "",
                    validated_ratio=gemini_aspect_ratio
                )
                print(f"[GLENN] Wide landscape: using build_openrouter_resize_prompt")
            elif is_extreme_portrait:
                resize_prompt = build_image_adaptation_prompt(
                    prompt=prompt if has_custom_prompt else "",
                    target_dims=(tw, th),
                    validated_ratio=gemini_aspect_ratio
                )
                print(f"[GLENN] Portrait: using build_image_adaptation_prompt")
            else:
                resize_prompt = build_ai_recompose_prompt(
                    user_prompt=prompt if has_custom_prompt else "",
                    target_dims=(tw, th),
                    validated_ratio=gemini_aspect_ratio
                )
                print(f"[GLENN] Moderate ratio: using build_ai_recompose_prompt")

            
            # Log all key counters at start of each request
            glenn_log_all_counters()
            
            image_data = None
            provider_used = "none"
            
            # ── PROVIDER: GOOGLE (multi-key rotation) ────────────────────
            if GLENN_PROVIDER == "google":
                active_client, key_label = glenn_get_google_client()
                actual_key = _glenn_keys_map.get(key_label, {}).get("api_key", "?")
                key_suffix = f"...{actual_key[-8:]}" if actual_key and actual_key != "?" and actual_key != "not-set" else "exhausted"
                db_counter = _glenn_get_counter(key_label)
                print(f"[GLENN] Provider: GOOGLE ({key_label} | {key_suffix}) | Target: {tw}x{th} | Counter: {db_counter.get('count', '?')}/{GLENN_KEY_LIMIT}")
                contents = [resize_prompt, pil_image]
                config = types.GenerateContentConfig(
                    response_modalities=["Image"],
                    image_config=types.ImageConfig(aspect_ratio=gemini_aspect_ratio),
                )
                try:
                    print(f"[GLENN] Trying gemini-3-pro-image-preview with {key_label}...")
                    response = await call_gemini_with_retry(
                        model_name="gemini-3-pro-image-preview",
                        contents=contents,
                        config=config,
                        max_retries=3,
                        api_client=active_client,
                    )
                    if response.parts:
                        for part in response.parts:
                            if part.inline_data:
                                image_data = part.inline_data.data
                                break
                    if image_data:
                        glenn_increment_counter(key_label)
                        provider_used = f"google/{key_label}/gemini-3-pro-image-preview"
                        print(f"[GLENN] ✅ Success with {key_label}")
                except Exception as e:
                    print(f"[GLENN] ❌ {key_label} failed: {e}")
                    glenn_mark_key_exhausted(key_label)
                    # Try remaining Google keys
                    remaining_keys = [k for k in ["key_1", "key_2", "key_3"] if k != key_label and _glenn_clients.get(k) and _glenn_get_counter(k).get("count", 0) < GLENN_KEY_LIMIT]
                    for fallback_kid in remaining_keys:
                        try:
                            fb_key = _glenn_keys_map.get(fallback_kid, {}).get("api_key", "?")
                            fb_suffix = f"...{fb_key[-8:]}" if fb_key != "not-set" and fb_key != "?" else "?"
                            print(f"[GLENN] 🔄 Trying fallback {fallback_kid} ({fb_suffix})...")
                            response = await call_gemini_with_retry(
                                model_name="gemini-3-pro-image-preview",
                                contents=contents,
                                config=config,
                                max_retries=2,
                                api_client=_glenn_clients[fallback_kid],
                            )
                            if response.parts:
                                for part in response.parts:
                                    if part.inline_data:
                                        image_data = part.inline_data.data
                                        break
                            if image_data:
                                glenn_increment_counter(fallback_kid)
                                provider_used = f"google/{fallback_kid}/gemini-3-pro-image-preview"
                                print(f"[GLENN] ✅ Success with fallback {fallback_kid}")
                                break
                        except Exception as fb_err:
                            print(f"[GLENN] ❌ {fallback_kid} also failed: {fb_err}")
                            glenn_mark_key_exhausted(fallback_kid)
            
            # ── PROVIDER: VERTEX (fallback from Google or primary) ───────
            if GLENN_PROVIDER == "vertex" or (GLENN_PROVIDER == "google" and not image_data):
                if not image_data:
                    print(f"[GLENN] Provider: VERTEX | Target: {tw}x{th}")
                    contents = [resize_prompt, pil_image]
                    config = types.GenerateContentConfig(response_modalities=["Image"])
                    for model_name in GLENN_MODELS:
                        try:
                            response = await call_gemini_with_retry(
                                model_name=model_name, contents=contents, config=config,
                                max_retries=2, api_client=glenn_client,
                            )
                            if response.parts:
                                for part in response.parts:
                                    if part.inline_data:
                                        image_data = part.inline_data.data
                                        break
                            if image_data:
                                glenn_increment_counter("vertex")
                                provider_used = f"vertex/{model_name}"
                                print(f"[GLENN] ✅ Success with {model_name}")
                                break
                        except Exception as e:
                            print(f"[GLENN] ❌ {model_name} failed: {e}")
                            continue
            
            # ── PROVIDER: OPENROUTER (final fallback) ────────────────────
            if not image_data:
                print(f"[GLENN] Provider: OPENROUTER | Target: {tw}x{th}")
                try:
                    or_response = await call_openrouter_image([pil_image, resize_prompt])
                    if or_response.parts:
                        for part in or_response.parts:
                            if part.inline_data:
                                image_data = part.inline_data.data
                                break
                    if image_data:
                        provider_used = "openrouter"
                        print(f"[GLENN] ✅ Success with OpenRouter")
                except Exception as e:
                    print(f"[GLENN] ❌ OpenRouter failed: {e}")
            
            if not image_data:
                raise RuntimeError("All Glenn resize providers failed")
            
            image_data = await run_blocking(safe_scale_to_exact, image_data, tw, th)
            print(f"[GLENN] Resize complete via {provider_used}: {tw}x{th}")
            
            # Upload to DO Spaces
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"glenn_resized/{timestamp}_{unique_id}.png"
            await run_blocking(
                s3_client.put_object,
                Bucket=DO_SPACES_BUCKET_NAME,
                Key=filename,
                Body=image_data,
                ContentType='image/png',
                ACL='public-read'
            )
            endpoint_for_url = DO_SPACES_ENDPOINT.replace('https://', '').replace('http://', '').strip()
            uploaded_url = f"https://{DO_SPACES_BUCKET_NAME}.{endpoint_for_url}/{filename}"
            
            # Consume units (handles both prepaid credit deduction and postpaid usage tracking)
            consume_units(user_id, cost, engine_type=engine_type)
            
            # Increment legacy counter
            increment_user_units(user_id)
            
            # Log to archive for history page
            log_usage(
                user_id=user_id,
                operation="resize",
                aspect_ratio=gemini_aspect_ratio,
                success=True,
                image_url=uploaded_url,
                prompt=prompt,
                target_dims=[tw, th]
            )
            
            print(f"[GLENN] Done: {uploaded_url}")
            return JSONResponse(content={
                "url": uploaded_url,
                "width": tw,
                "height": th,
                "ratio": gemini_aspect_ratio,
                "provider": provider_used,
            })
        except HTTPException:
            raise
        except Exception as e:
            print(f"[GLENN] Pipeline error: {e}")
            raise HTTPException(status_code=500, detail=f"Glenn resize failed: {str(e)}")
    
    # ── End Glenn Pipeline ────────────────────────────────────────────────
    
    try:
        # Engine-specific validation
        if engine_type == "transformation":
            # Transformation requires image, no custom prompt
            if not file:
                raise HTTPException(
                    status_code=400, 
                    detail="Transformation engine requires an image upload. Please upload an image to transform."
                )
            # Force default prompt for transformation (ignore any user-provided prompt)
            prompt = None
            print(f"🔄 [TRANSFORMATION] Image-only transformation mode")
            
        elif engine_type == "creation":
            # Creation requires prompt, image is optional
            if not prompt or not prompt.strip():
                raise HTTPException(
                    status_code=400,
                    detail="Creation engine requires a prompt. Please provide a description of what you want to create."
                )
            print(f"🎨 [CREATION] Prompt-based {'generation' if not file else 'transformation'} mode")
        
        # 1. Read the image and get dimensions for credit calculation (if image provided)
        pil_image = None
        max_dim = 1024  # Default for prompt-only generation
        
        if file:
            image_bytes = await file.read()
            print(f"📥 [DEBUG] Received file: {file.filename}, length: {len(image_bytes)} bytes")
            
            if len(image_bytes) == 0:
                raise HTTPException(status_code=400, detail="Uploaded file is empty")

            try:
                pil_image = Image.open(io.BytesIO(image_bytes))
                width, height = pil_image.size
                max_dim = max(width, height)
            except Exception as e:
                print(f"❌ [DEBUG] PIL Error: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid image format: {str(e)}")
        else:
            # Creation engine with prompt only - no image
            print(f"🎨 [CREATION] Generating image from prompt only (no input image)")
        
        is_postpaid = bool(current_user.get("is_postpaid", False))

        has_custom_prompt = bool(prompt and prompt.strip()) and engine_type == "creation"
        has_image = pil_image is not None

        # Credit cost logic:
        # POSTPAID: Always 1 credit per operation (dollar cost is dynamic via per-credit rate)
        # PREPAID:  4 credits base, 6 credits for creation engine with image + custom prompt
        if is_postpaid:
            tokens_to_deduct = 1.0
        else:
            tokens_to_deduct = 6.0 if (engine_type == "creation" and has_image and has_custom_prompt) else 4.0

        if pil_image:
            width, height = pil_image.size
            print(f"🖼️ [RESIZE] Image: {width}x{height} ({max_dim}px). Engine: {engine_type}. Postpaid: {is_postpaid}. Cost: {tokens_to_deduct} credits.")
        else:
            print(f"🎨 [GENERATE] Prompt-only generation ({max_dim}px default). Engine: {engine_type}. Postpaid: {is_postpaid}. Cost: {tokens_to_deduct} credits.")

        # Check user's credits
        user_id = str(current_user["_id"])
        
        # Get backend session/user data refresh to ensure we have latest credits
        # Priority: engine_data[engine_type] -> credits
        engine_data = current_user.get("engine_data", {})
        target_engine_info = engine_data.get(engine_type, {})
        engine_credits = target_engine_info.get("credits", {}) if target_engine_info else {}
        
        # Fallback to top-level if engine matches current user's active engine
        if not engine_credits and current_user.get("engineType") == engine_type:
            engine_credits = current_user.get("credits", {})

        remaining = float(engine_credits.get("remaining_units", 0.0))

        if (not is_postpaid) and remaining < tokens_to_deduct:
            raise HTTPException(
                status_code=429, 
                detail=f"Insufficient credits for {engine_type}. Required: {tokens_to_deduct}, Available: {remaining}. Please upgrade your {engine_type} plan."
            )
        
        # 2. Aspect Ratio Sanitization
        SUPPORTED_RATIOS = ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9']
        
        # Save the original requested ratio for post-processing
        original_aspect_ratio = aspect_ratio
        
        # Normalize input aspect_ratio (handle both '16:9' and '16x9' or '1120:360')
        input_ratio = aspect_ratio.replace('x', ':')
        
        # If not directly supported, find the closest one to prevent API crash
        gemini_aspect_ratio = input_ratio  # This will be sent to Gemini
        if input_ratio not in SUPPORTED_RATIOS:
            try:
                w_in, h_in = map(int, input_ratio.split(':'))
                ratio_val = w_in / h_in
                
                # Find closest supported ratio based on decimal value
                ratio_map = {
                    '1:1': 1.0,
                    '2:3': 0.66,
                    '3:2': 1.5,
                    '3:4': 0.75,
                    '4:3': 1.33,
                    '4:5': 0.8,
                    '5:4': 1.25,
                    '9:16': 0.56,
                    '16:9': 1.77,
                    '21:9': 2.33
                }
                
                closest_ratio = min(ratio_map.keys(), key=lambda k: abs(ratio_map[k] - ratio_val))
                print(f"⚠️ [RESIZE] Unsupported ratio {input_ratio} ({ratio_val:.2f}). Mapping to closest supported: {closest_ratio}")
                gemini_aspect_ratio = closest_ratio
            except Exception as e:
                print(f"❌ [RESIZE] Aspect ratio parsing error: {e}. Defaulting to 1:1")
                gemini_aspect_ratio = '1:1'
        
        if not client:
            # Try reloading env if key was added later
            load_dotenv()
            GOOGLE_API_KEY_LATEST = os.getenv("GOOGLE_API_KEY")
            if GOOGLE_API_KEY_LATEST:
                client = genai.Client(api_key=GOOGLE_API_KEY_LATEST)
            else:
                client = None
        
        # 3. Call the primary AI service (Gemini) with Vertex + Fal.ai fallbacks
        image_data = None
        gemini_error: Exception | None = None
        vertex_error: Exception | None = None

        # Helper for safer extraction
        def extract_img_bytes(obj):
            if not obj: return None
            # If it's already bytes, return it
            if isinstance(obj, bytes): return obj
            # If it's a part/blob with a 'data' attribute
            data_attr = getattr(obj, "data", None)
            if isinstance(data_attr, bytes): return data_attr
            # If it has 'inline_data'
            inline = getattr(obj, "inline_data", None)
            if inline:
                if isinstance(inline, bytes): return inline
                return getattr(inline, "data", None)
            return None


        # Construct the structured prompt (Smart Routing)
        is_wide_landscape = (target_dims[0] > target_dims[1] * 1.5) if target_dims else False
        is_extreme_portrait = (target_dims[1] > target_dims[0] * 1.5) if target_dims else False

        if has_image:
            if is_wide_landscape:
                use_prompt = build_openrouter_resize_prompt(
                    source_dims=pil_image.size,
                    target_dims=target_dims,
                    user_context=prompt or "",
                    validated_ratio=gemini_aspect_ratio
                )
            elif is_extreme_portrait:
                use_prompt = build_image_adaptation_prompt(
                    prompt=prompt or "",
                    target_dims=target_dims,
                    validated_ratio=gemini_aspect_ratio
                )
            else:
                use_prompt = build_ai_recompose_prompt(
                    user_prompt=prompt or "",
                    target_dims=target_dims,
                    validated_ratio=gemini_aspect_ratio
                )
        else:
            use_prompt = build_layout_prompt(
                prompt=prompt or "Generate a professional digital graphic.",
                target_dims=target_dims,
                validated_ratio=gemini_aspect_ratio
            )


        # --- Primary: Vertex AI via google-genai SDK (High Priority) ---
        # Uses genai.Client(vertexai=True) with service account credentials
        # This has its own separate quota from the Gemini API key
        if not image_data and vertex_client:
            # Try multiple image-capable models in order of preference
            VERTEX_IMAGE_MODELS = [
                "gemini-2.0-flash-001",
                "gemini-2.0-flash-preview-image-generation",
                "gemini-2.5-flash-preview-image-generation",
            ]
            for v_model_name in VERTEX_IMAGE_MODELS:
                try:
                    print(f"🧭 [PRIMARY] Trying Vertex AI model: {v_model_name}")

                    # Build contents just like Gemini SDK
                    if pil_image:
                        v_contents = [use_prompt, pil_image]
                    else:
                        v_contents = [use_prompt]

                    v_response = vertex_client.models.generate_content(
                        model=v_model_name,
                        contents=v_contents,
                        config=types.GenerateContentConfig(
                            response_modalities=["IMAGE"],
                        )
                    )
                    print(f"📡 [PRIMARY] Vertex AI response received (model={v_model_name}). Parts: {len(v_response.parts) if v_response.parts else 0}")

                    if v_response.parts:
                        for part in v_response.parts:
                            extracted = extract_img_bytes(part)
                            if extracted:
                                image_data = extracted
                                print(f"🖼️ [PRIMARY] Extracted Vertex image: {len(image_data)} bytes (model={v_model_name})")
                                break

                    if image_data:
                        break  # Success! Stop trying models
                    else:
                        print(f"❌ [PRIMARY] {v_model_name} returned no image bytes, trying next model...")

                except Exception as ve:
                    vertex_error = ve
                    print(f"❌ [PRIMARY] {v_model_name} failed: {ve}")
                    continue  # Try next model

            if not image_data and vertex_error:
                print(f"❌ [PRIMARY] All Vertex AI models failed. Last error: {vertex_error}")

        # --- Second: Gemini (google-genai SDK - Fallback 1) ---
        # For prompt-only creation, prefer Glenn rotated Google keys first.
        gemini_client_for_request = client
        gemini_client_label = "default"
        if engine_type == "creation" and not pil_image:
            try:
                glenn_candidate_client, glenn_key_label = glenn_get_google_client()
                if glenn_candidate_client:
                    gemini_client_for_request = glenn_candidate_client
                    gemini_client_label = f"glenn/{glenn_key_label}"
                    print(f"🤖 [CREATION] Using rotated Glenn client: {gemini_client_label}")
                else:
                    print("🤖 [CREATION] No Glenn Google key available, using default Gemini client")
            except Exception as glenn_client_err:
                print(f"⚠️ [CREATION] Failed to pick Glenn client, using default: {glenn_client_err}")

        if not image_data and gemini_client_for_request:
            try:
                model_name = "gemini-3-pro-image-preview"
                print(f"🤖 [FALLBACK] Calling {model_name} (Gemini SDK, client={gemini_client_label}) with prompt: '{use_prompt[:50]}...'")

                # Build contents based on whether we have an image
                if pil_image:
                    contents = [use_prompt, pil_image]
                else:
                    contents = [use_prompt]

                response = gemini_client_for_request.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                        image_config=types.ImageConfig(
                            aspect_ratio=gemini_aspect_ratio
                        )
                    )
                )
                print(f"📡 [FALLBACK] Gemini SDK response received. Parts: {len(response.parts) if response.parts else 0}")
                
                if response.parts:
                    for part in response.parts:
                        extracted = extract_img_bytes(part)
                        if extracted:
                            image_data = extracted
                            print(f"🖼️ [FALLBACK] Extracted Gemini SDK image: {len(image_data)} bytes")
                            break

                # Track Glenn key usage only when it was actually used successfully.
                if image_data and gemini_client_label.startswith("glenn/"):
                    try:
                        key_label = gemini_client_label.split("/", 1)[1]
                        if key_label in ("key_1", "key_2", "key_3"):
                            glenn_increment_counter(key_label)
                    except Exception as glenn_counter_err:
                        print(f"⚠️ [CREATION] Could not increment Glenn counter: {glenn_counter_err}")

                if not image_data:
                    print(f"❌ [FALLBACK] No image data in Gemini SDK response.")
            except Exception as ge:
                gemini_error = ge
                print(f"❌ [FALLBACK] Gemini SDK failed: {ge}")

        # --- Third: Fal.ai wrapper (Fallback 2) ---
        if not image_data:
            try:
                print(f"🛟 [FALLBACK] Invoking Fal.ai wrapper at {FAL_FALLBACK_URL}")
                payload = {
                    "prompt": use_prompt,
                    "aspect_ratio": gemini_aspect_ratio,
                    "sync_mode": True,
                }

                async with httpx.AsyncClient(timeout=60.0) as http_client:
                    fal_response = await http_client.post(FAL_FALLBACK_URL, json=payload)
                fal_response.raise_for_status()

                fal_json = fal_response.json()
                print(f"🛟 [FALLBACK] Fal.ai response received")

                image_url = None
                if isinstance(fal_json, dict):
                    if fal_json.get("image_urls"):
                        image_url = fal_json["image_urls"][0]
                    elif fal_json.get("images"):
                        first = fal_json["images"][0]
                        if isinstance(first, dict):
                            image_url = first.get("url") or first.get("image_url")
                        else:
                            image_url = first
                    elif fal_json.get("url"):
                        image_url = fal_json["url"]

                if not image_url:
                    raise RuntimeError("Fal.ai fallback did not return an image URL")

                print(f"🛟 [FALLBACK] Downloading image from {image_url}")
                async with httpx.AsyncClient(timeout=60.0) as http_client:
                    img_resp = await http_client.get(image_url)
                img_resp.raise_for_status()
                image_data = img_resp.content
                print(f"✅ [FALLBACK] Retrieved fallback image: {len(image_data)} bytes")

            except Exception as fallback_err:
                print(f"❌ [FALLBACK] Fal.ai wrapper failed: {fallback_err}")

                # Try direct SeedDream fallback if we have an input image and a SeedDream key
                if pil_image:
                    seedream_key = os.getenv("SEEDREAM_KEY")
                    if seedream_key:
                        try:
                            print("🛟 [FALLBACK] Invoking SeedDream via fal.ai direct endpoint")
                            b64 = base64.b64encode(image_bytes).decode("utf-8")
                            image_data_uris = [f"data:image/png;base64,{b64}"]
                            sd_payload = {
                                "prompt": f"IMAGE ONLY. FULL FRAME DIGITAL CONTENT. NO physical mockups. {use_prompt}",
                                "image_urls": image_data_uris,
                                "sync_mode": True,
                            }
                            async with httpx.AsyncClient(timeout=120.0) as sd_client:
                                sd_resp = await sd_client.post(
                                    "https://fal.run/fal-ai/bytedance/seedream/v4.5/edit",
                                    headers={
                                        "Authorization": f"Key {seedream_key}",
                                        "Content-Type": "application/json",
                                    },
                                    json=sd_payload,
                                )
                            sd_resp.raise_for_status()

                            sd_result = sd_resp.json()
                            sd_images = sd_result.get("images", [])
                            if not sd_images:
                                raise RuntimeError("SeedDream returned no images")

                            sd_image_url = sd_images[0].get("url")
                            if not sd_image_url:
                                raise RuntimeError("SeedDream response contained no image URL")

                            if sd_image_url.startswith("data:"):
                                _, sd_encoded = sd_image_url.split(",", 1)
                                image_data = base64.b64decode(sd_encoded)
                            else:
                                async with httpx.AsyncClient(timeout=60.0) as sd_client:
                                    img_resp = await sd_client.get(sd_image_url)
                                img_resp.raise_for_status()
                                image_data = img_resp.content

                            print(f"✅ [SeedDream] Retrieved fallback image: {len(image_data)} bytes")
                        except Exception as sd_err:
                            print(f"❌ [SeedDream] Fallback failed: {sd_err}")
                            base_error = vertex_error or gemini_error or fallback_err
                            raise HTTPException(
                                status_code=500,
                                detail=f"Image generation failed (Vertex + Gemini + Fal.ai + SeedDream). Reason: {base_error}"
                            )
                    else:
                        print("ℹ️ [SeedDream] SEEDREAM_KEY not configured, skipping direct SeedDream fallback")
                        base_error = vertex_error or gemini_error or fallback_err
                        raise HTTPException(
                            status_code=500,
                            detail=f"Image generation failed (Vertex + Gemini + Fal.ai). Reason: {base_error}"
                        )
                else:
                    base_error = vertex_error or gemini_error or fallback_err
                    raise HTTPException(
                        status_code=500,
                        detail=f"Image generation failed (Vertex + Gemini + Fal.ai). Reason: {base_error}"
                    )

        # 5. Post-process: Resize to exact requested dimensions
        # Standard ratio → pixel mapping for consistent output
        RATIO_TO_PIXELS = {
            '16:9':  (1920, 1080),
            '9:16':  (1080, 1920),
            '1:1':   (1080, 1080),
            '3:4':   (1080, 1440),
            '4:3':   (1440, 1080),
            '21:9':  (2520, 1080),
            '2:3':   (1080, 1620),
            '3:2':   (1620, 1080),
            '4:5':   (1080, 1350),
            '5:4':   (1350, 1080),
        }
        
        target_width = target_height = None
        try:
            # First check if it's a known ratio
            if original_aspect_ratio in RATIO_TO_PIXELS:
                target_width, target_height = RATIO_TO_PIXELS[original_aspect_ratio]
                print(f"🎯 [RESIZE] Mapped ratio '{original_aspect_ratio}' to {target_width}x{target_height}")
            else:
                # Try parsing as exact pixel dimensions (e.g., "1920x1080" or "1920:1080")
                original_ratio_str = original_aspect_ratio.replace(':', 'x')
                if 'x' in original_ratio_str:
                    w_val, h_val = map(int, original_ratio_str.split('x'))
                    if w_val >= 100 and h_val >= 100:
                        target_width, target_height = w_val, h_val
                        print(f"🎯 [RESIZE] Detected exact target dimensions: {target_width}x{target_height}")
                    else:
                        print(f"ℹ️ [RESIZE] Ratio '{original_aspect_ratio}' has small values. Using default mapping.")
                        # Try as ratio lookup with normalized format
                        normalized = f"{w_val}:{h_val}"
                        if normalized in RATIO_TO_PIXELS:
                            target_width, target_height = RATIO_TO_PIXELS[normalized]
                            print(f"🎯 [RESIZE] Mapped normalized ratio '{normalized}' to {target_width}x{target_height}")
        except Exception as parse_err:
            print(f"⚠️ [RESIZE] Could not parse dimensions from '{original_aspect_ratio}': {parse_err}")
            target_width = target_height = None
        
        # Only post-process if we have exact target dimensions
        if target_width and target_height:
            try:
                # Load the generated image
                generated_image = Image.open(io.BytesIO(image_data))
                orig_w, orig_h = generated_image.size
                print(f"📐 [RESIZE] Generated image size: {orig_w}x{orig_h}, Target: {target_width}x{target_height}")
                
                # Calculate the aspect ratios
                gen_ratio = orig_w / orig_h
                target_ratio = target_width / target_height
                
                # Strategy: Center crop to exact ratio, then resize to exact dimensions
                if abs(gen_ratio - target_ratio) > 0.01:  # Ratios differ
                    print(f"✂️ [RESIZE] Cropping to match target ratio {target_ratio:.2f}")
                    if gen_ratio > target_ratio:
                        # Generated image is wider, crop width
                        new_width = int(orig_h * target_ratio)
                        left = (orig_w - new_width) // 2
                        generated_image = generated_image.crop((left, 0, left + new_width, orig_h))
                    else:
                        # Generated image is taller, crop height
                        new_height = int(orig_w / target_ratio)
                        top = (orig_h - new_height) // 2
                        generated_image = generated_image.crop((0, top, orig_w, top + new_height))
                
                # Resize to exact target dimensions
                if generated_image.size != (target_width, target_height):
                    print(f"🔄 [RESIZE] Resizing from {generated_image.size} to {target_width}x{target_height}")
                    generated_image = generated_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Convert back to bytes
                output_buffer = io.BytesIO()
                generated_image.save(output_buffer, format='PNG')
                image_data = output_buffer.getvalue()
                print(f"✅ [RESIZE] Post-processed to exact dimensions: {target_width}x{target_height}")
                
            except Exception as resize_err:
                print(f"⚠️ [RESIZE] Post-processing failed: {resize_err}. Using original generated image.")
                # Continue with original image_data if post-processing fails
        
        # 6. Upload to Digital Ocean Spaces (matching NestJS implementation exactly)
        uploaded_url = None
        image_name = None
        
        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"resized_images/{timestamp}_{unique_id}.png"
        image_name = f"{timestamp}_{unique_id}.png"
        
        print(f"☁️ [DEBUG] Uploading to DO Spaces: {filename}")
        
        try:
            bucket_name = DO_SPACES_BUCKET_NAME
            
            # Upload to Digital Ocean Spaces (matching NestJS implementation)
            s3_client.put_object(
                Bucket=bucket_name,
                Key=filename,
                Body=image_data,
                ContentType='image/png',
                ACL='public-read'  # Make the image publicly accessible
            )
            
            # Construct the public URL (matching NestJS format: https://{bucketName}.{endpoint}/{fileName})
            # Clean endpoint for URL construction (remove protocol if present)
            endpoint_for_url = DO_SPACES_ENDPOINT.replace('https://', '').replace('http://', '').strip()
            uploaded_url = f"https://{bucket_name}.{endpoint_for_url}/{filename}"
            print(f"Image uploaded to Digital Ocean Spaces: {uploaded_url}")
        except Exception as upload_error:
            print(f"Error uploading to Digital Ocean Spaces: {upload_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Image generated but failed to upload to storage: {str(upload_error)}"
            )
        
        # 7. Return JSON response with URL and name
        if not uploaded_url or not image_name:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate upload URL or image name"
            )
        
        response_data = {
            "url": uploaded_url,
            "name": image_name
        }
        print(f"Returning response: {response_data}")
        
        # Deduct credits ONLY on success
        consumed = consume_units(user_id, tokens_to_deduct, engine_type=engine_type)
        if not consumed:
            raise HTTPException(status_code=429, detail="Insufficient credits to complete request")

        # Keep legacy counter best-effort (do NOT enforce off this)
        increment_user_units(user_id)

        # Log usage (include prompt and target dims for archive)
        log_usage(
            user_id=user_id,
            operation="resize",
            aspect_ratio=aspect_ratio,
            success=True,
            image_url=uploaded_url,
            prompt=prompt,
            target_dims=[target_width, target_height] if target_width and target_height else None
        )

        return JSONResponse(content=response_data, status_code=200)

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions to keep their detail messages
        raise http_exc
    except Exception as e:
        print(f"❌ [RESIZE] Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        
        # Best-effort log failure
        try:
            log_usage(
                user_id=user_id if 'user_id' in locals() else "unknown",
                operation="resize",
                aspect_ratio=aspect_ratio,
                success=False,
                image_url=None,
                prompt=prompt
            )
        except:
            pass
            
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error during image processing: {str(e)}"
        )


@app.post("/api/custom-resize", response_class=JSONResponse)
@app.post("/custom-resize", response_class=JSONResponse)
async def custom_resize_image(
    width: int = Form(...),
    height: int = Form(...),
    file: UploadFile = File(None),
    prompt: str = Form(None),
    engine_type: str = Form("transformation"),
    current_user = Depends(get_current_user),
):
    """Custom resize endpoint using explicit pixel dimensions and shared resize pipeline."""
    if not _can_use_custom_resize(current_user):
        raise HTTPException(
            status_code=403,
            detail="Custom resize is only enabled for the Glen account and approved sub-org users.",
        )

    MIN_DIM, MAX_DIM = 64, 4096
    if not (MIN_DIM <= width <= MAX_DIM and MIN_DIM <= height <= MAX_DIM):
        raise HTTPException(
            status_code=400,
            detail=f"Dimensions must be between {MIN_DIM}px and {MAX_DIM}px. Got {width}x{height}.",
        )

    prompt_text = (prompt or "").strip()
    if file is None and not prompt_text:
        raise HTTPException(
            status_code=400,
            detail="Either a file or a prompt must be provided",
        )

    # Keep behavior aligned with /api/resize pricing/validation paths.
    effective_engine = (engine_type or "transformation").strip().lower()
    if effective_engine not in {"transformation", "creation"}:
        raise HTTPException(
            status_code=400,
            detail="engine_type must be either 'transformation' or 'creation'",
        )
    if prompt_text and effective_engine == "transformation":
        effective_engine = "creation"
    if file is None and prompt_text:
        effective_engine = "creation"

    requested_ratio = f"{width}:{height}"
    mapped_ratio, _, _ = validate_aspect_ratio_smart(requested_ratio)


    ratio_val = width / height if height > 0 else 1.0
    EXTREME_WIDE_AR = 2.5

    # If it's an extreme wide image, intercept and try OpenAI first!
    if file and ratio_val > EXTREME_WIDE_AR and effective_engine == "transformation":
        print(f"🚀 [CUSTOM-RESIZE] Ultra-wide detected (AR {ratio_val:.2f} > 2.5). Routing to OpenAI Intelligent Reflow pipeline.")
        try:
            from openai_service import call_openai_image_edit
            
            # Cost logic (same as resize_image for transformation)
            is_postpaid = current_user.get("is_postpaid", False)
            cost = 1.0 if is_postpaid else 4.0
            user_id = str(current_user["_id"])
            
            # Credit check
            if not is_postpaid:
                engine_data = current_user.get("engine_data", {})
                target_engine_info = engine_data.get(effective_engine, {})
                engine_credits = target_engine_info.get("credits", {}) if target_engine_info else {}
                if not engine_credits and current_user.get("engineType") == effective_engine:
                    engine_credits = current_user.get("credits", {})
                remaining = float(engine_credits.get("remaining_units", 0.0))
                if remaining < cost:
                    raise HTTPException(status_code=429, detail=f"Insufficient credits. Need {cost}, have {remaining}")

            # Read file bytes
            file_bytes = await file.read()
            # Reset file pointer so resize_image fallback can still read it
            await file.seek(0)
            
            pil_img = await run_blocking(Image.open, io.BytesIO(file_bytes))
            src_w, src_h = pil_img.size

            if ratio_val >= 3.5:
                ai_prompt = build_openai_banner_prompt(prompt_text, width, height, source_dims=(src_w, src_h))
            else:
                ai_prompt = build_openai_outpaint_prompt(prompt_text, width, height, source_dims=(src_w, src_h))

            print(f"🤖 [CUSTOM-RESIZE] Calling OpenAI gpt-image-2 for {width}x{height} banner...")
            openai_image_bytes = await call_openai_image_edit(
                image_bytes=file_bytes,
                prompt=ai_prompt,
                target_width=width,
                target_height=height
            )
            
            print(f"✅ [CUSTOM-RESIZE] OpenAI success! Uploading to Digital Ocean...")
            import uuid
            filename = f"custom-resized/{uuid.uuid4().hex}.png"
            await run_blocking(
                s3_client.put_object,
                Bucket=DO_SPACES_BUCKET_NAME,
                Key=filename,
                Body=openai_image_bytes,
                ACL="public-read",
                ContentType="image/png",
            )
            uploaded_url = f"https://{DO_SPACES_BUCKET_NAME}.{DO_SPACES_ENDPOINT.replace('https://','')}/{filename}"
            
            # Consume units
            if cost > 0:
                consume_units(user_id, cost, effective_engine)
            
            log_usage(user_id, "custom_resize", requested_ratio, True, uploaded_url, prompt_text, (width, height), model="gpt-image-2")
            
            return JSONResponse(content={
                "url": uploaded_url, 
                "credits_used": cost,
                "width": width,
                "height": height,
                "gemini_ratio": mapped_ratio,
                "requested_ratio": requested_ratio,
                "engine_type": effective_engine,
                "provider": "openai/gpt-image-2"
            })
            
        except Exception as openai_err:
            print(f"⚠️ [CUSTOM-RESIZE] OpenAI failed for wide, falling back to standard pipeline: {openai_err}")

    # Reuse existing resize pipeline to keep all checks and post-processing consistent.
    base_response = await resize_image(
        aspect_ratio=f"{width}x{height}",
        engine_type=effective_engine,
        file=file,
        prompt=prompt,
        current_user=current_user,
    )

    payload = {}
    if isinstance(base_response, JSONResponse):
        try:
            import json

            payload = json.loads(base_response.body.decode("utf-8")) if base_response.body else {}
        except Exception:
            payload = {}

    payload.update(
        {
            "width": width,
            "height": height,
            "gemini_ratio": mapped_ratio,
        }
    )

    return JSONResponse(content=payload, status_code=base_response.status_code)

@app.get("/api/history")
async def get_history(current_user = Depends(get_current_user)):
    """Return the user's past successful image generations for the archive page."""
    try:
        user_id = str(current_user["_id"])
        
        # Query usage_logs for successful operations with an image URL
        cursor = auth_module.usage_logs_collection.find(
            {
                "userId": user_id,
                "success": True,
                "imageUrl": {"$ne": None},
                "is_deleted_from_s3": {"$ne": True}
            },
            sort=[("timestamp", -1)],
            limit=100
        )
        
        history = []
        for doc in cursor:
            history.append({
                "id": str(doc["_id"]),
                "url": doc.get("imageUrl", ""),
                "prompt": doc.get("prompt", ""),
                "aspectRatio": doc.get("aspectRatio", "1:1"),
                "targetDims": doc.get("targetDims", None),
                "timestamp": doc.get("timestamp", "").isoformat() if doc.get("timestamp") else "",
                "operation": doc.get("operation", "resize"),
            })
        
        return JSONResponse(content={"history": history}, status_code=200)
    except Exception as e:
        print(f"❌ [HISTORY] Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {str(e)}")

from urllib.parse import urlparse

@app.delete("/api/dev/clean-user-archive")
async def clean_user_archive(email: str = Body(..., embed=True), current_user = Depends(get_current_user)):
    """
    Delete a user's generated images from S3 and usage_logs DB.
    Requires a valid Bearer Token from ANY authenticated user.
    Usage: DELETE /api/dev/clean-user-archive with body {"email": "user@example.com"}
    """
    user = auth_module.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with email {email} not found")

    user_id = str(user["_id"])
    cursor = auth_module.usage_logs_collection.find(
        {"userId": user_id, "imageUrl": {"$ne": None}, "success": True}
    )
    
    docs = list(cursor)
    if not docs:
        return {"message": "No archive images found for user.", "deleted_count": 0}

    # Gather S3 keys to delete
    keys_to_delete = []
    object_ids = []
    
    for doc in docs:
        img_url = doc.get("imageUrl")
        if img_url:
            parsed = urlparse(img_url)
            s3_key = parsed.path.lstrip('/')
            
            keys_to_delete.append({'Key': s3_key})
            object_ids.append(doc["_id"])
            
    # S3 allows up to 1000 keys per delete_objects call
    deleted_s3_count = 0
    chunk_size = 1000
    for i in range(0, len(keys_to_delete), chunk_size):
        chunk = keys_to_delete[i:i+chunk_size]
        try:
            response = await run_blocking(
                s3_client.delete_objects,
                Bucket=DO_SPACES_BUCKET_NAME,
                Delete={'Objects': chunk, 'Quiet': True}
            )
            deleted_s3_count += len(chunk)
        except Exception as e:
            print(f"Error deleting chunk from S3: {e}")
            raise HTTPException(status_code=500, detail=f"S3 deletion error: {str(e)}")
            
    # Mark as deleted in DB
    update_result = auth_module.usage_logs_collection.update_many(
        {"_id": {"$in": object_ids}},
        {"$set": {"is_deleted_from_s3": True, "deletedAt": datetime.utcnow()}}
    )
    
    return {
        "message": f"Successfully deleted {deleted_s3_count} objects from S3 and hidden from archive.",
        "deleted_s3_count": deleted_s3_count,
        "hidden_logs_count": update_result.modified_count
    }

@app.post("/api/admin/trigger-billing-rollover")
async def trigger_billing_rollover(current_user = Depends(get_admin_user)):
    """
    Manually trigger the monthly billing rollover for all postpaid users.
    Useful for testing or if the automated task was missed.
    We run this in a thread to prevent blocking the entire server during bulk processing.
    """
    try:
        success = await asyncio.to_thread(perform_all_postpaid_rollovers, force=True)
        if success:
            return {"message": "Monthly rollover triggered and processed successfully."}
        else:
            return {"message": "Monthly rollover already completed for the current month."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    # Configure to accept large file uploads (100MB limit)
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        limit_max_size=100 * 1024 * 1024,
        limit_request_fields=32000,
        limit_request_line=8190,
        limit_concurrency=1000,
        timeout_keep_alive=65
    )
