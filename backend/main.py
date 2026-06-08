from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header, Request, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from typing import Optional, Tuple, Dict
import os, io, asyncio, uuid, warnings
from functools import partial
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import boto3
import stripe
from botocore.config import Config
from bson import ObjectId

from models import (UserRegister, UserLogin, ForgotPasswordRequest,
                    ResetPasswordRequest, TokenResponse, UserResponse)
from auth import (
    create_user, verify_user_credentials, create_access_token,
    verify_token, get_user_by_id, increment_user_units,
    create_password_reset_token, reset_password_by_token,
    send_password_reset_email, user_doc_to_response,
    get_all_plans, get_user_usage_stats, get_billing_history,
    generate_monthly_bill, log_usage, update_feedback,
    consume_units, cancel_user_plan, update_user_plan,
    perform_all_postpaid_rollovers,
)
import auth as auth_module
import org_auth
from stripe_manager import (
    create_checkout_session, create_portal_session,
    handle_webhook_event, cancel_subscription,
    validate_stripe_configuration,
)

warnings.filterwarnings("ignore", category=FutureWarning, module=r"google.api_core")

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not validate_stripe_configuration():
    print("⚠️  WARNING: Stripe configuration validation failed.")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Visual Engine API", root_path="/secure")

ALLOWED_ORIGINS = [
    o.strip() for o in (
        os.getenv("CORS_ORIGINS") or
        "http://localhost:3000,http://127.0.0.1:3000,"
        "https://transformation.slidexy.ai,https://recreative.slidexy.ai,"
        "https://transformation.signagexai.com"
    ).split(",") if o.strip()
]
_CORS_ORIGIN_REGEX = (os.getenv("CORS_ORIGIN_REGEX") or "").strip() or \
    r"^https?://(localhost|127\.0\.0\.1|\[::1\])(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Gemini ────────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None
if not client:
    print("Warning: GOOGLE_API_KEY not set")

# ── Digital Ocean Spaces ──────────────────────────────────────────────────────
DO_SPACES_ACCESS_KEY = (os.getenv("DO_ACCESS_KEY_ID") or os.getenv("ACCESS_KEY_ID", "")).strip("'\" ")
DO_SPACES_SECRET_KEY = (os.getenv("DO_SECRET_KEY") or os.getenv("SECRET_KEY", "")).strip("'\" ")
DO_SPACES_ENDPOINT   = os.getenv("ENDPOINT", "").strip("'\" ")
DO_SPACES_BUCKET_NAME = os.getenv("SPACENAME", "").strip("'\" ")

if not all([DO_SPACES_ENDPOINT, DO_SPACES_BUCKET_NAME, DO_SPACES_ACCESS_KEY, DO_SPACES_SECRET_KEY]):
    raise ValueError("ENDPOINT, SPACENAME, ACCESS_KEY_ID and SECRET_KEY must be set")

_ep = DO_SPACES_ENDPOINT.replace("https://", "").replace("http://", "").strip()
s3_client = boto3.client(
    "s3",
    endpoint_url=f"https://{_ep}",
    aws_access_key_id=DO_SPACES_ACCESS_KEY,
    aws_secret_access_key=DO_SPACES_SECRET_KEY,
    region_name=_ep.split(".")[0] if "." in _ep else "nyc3",
    config=Config(signature_version="s3v4", s3={"addressing_style": "virtual"}),
)
print("Digital Ocean Spaces client initialized")

# ── Startup / background tasks ────────────────────────────────────────────────
async def _billing_rollover_loop():
    print("🕒 [SYSTEM] Billing rollover background task started")
    while True:
        try:
            if datetime.utcnow().day == 1:
                if await asyncio.to_thread(perform_all_postpaid_rollovers):
                    print("✅ [SYSTEM] Automated rollover completed")
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"❌ [SYSTEM] Rollover error: {e}")
            await asyncio.sleep(600)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(_billing_rollover_loop())


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = await request.body()
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body_preview": body.decode("utf-8", errors="ignore")[:100],
        },
    )

# ── Helpers ───────────────────────────────────────────────────────────────────
async def run_blocking(fn, *args, **kwargs):
    return await asyncio.get_running_loop().run_in_executor(None, partial(fn, *args, **kwargs))


async def call_gemini_with_retry(model_name, contents, config=None, max_retries=3, api_client=None):
    _c = api_client or client
    for attempt in range(max_retries):
        try:
            if config:
                return await run_blocking(_c.models.generate_content, model=model_name, contents=contents, config=config)
            return await run_blocking(_c.models.generate_content, model=model_name, contents=contents)
        except Exception as e:
            err = str(e)
            retriable = any(k in err for k in ["503", "429", "overload", "resource_exhausted", "deadline_exceeded"])
            print(f"[Gemini attempt {attempt+1}/{max_retries}] {err[:120]}")
            if retriable and attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise

# ── Aspect ratio constants & helpers ─────────────────────────────────────────
GEMINI_NATIVE_RESOLUTIONS: Dict[str, Tuple[int, int]] = {
    "1:1":  (1024, 1024),
    "16:9": (1344, 768),
    "9:16": (768, 1344),
    "3:4":  (896, 1152),
    "21:9": (1536, 640),
}

PRESET_MAPPING = {
    "landscape": "16:9",
    "story": "9:16",
    "story/reel": "9:16",
    "square": "1:1",
    "portrait": "3:4",
    "ultrawide": "21:9",
    "16:9": "16:9",
    "9:16": "9:16",
    "1:1": "1:1",
    "3:4": "3:4",
    "21:9": "21:9",
}

def validate_aspect_ratio(aspect_ratio: str) -> Tuple[str, Tuple[int, int]]:
    """Map any aspect ratio string to (gemini_ratio, (width, height))."""
    key = (aspect_ratio or "").strip().lower().replace("x", ":").replace("-", ":")
    if key in PRESET_MAPPING:
        ratio = PRESET_MAPPING[key]
        return ratio, GEMINI_NATIVE_RESOLUTIONS[ratio]
        
    raise HTTPException(
        status_code=400,
        detail=f"Aspect ratio '{aspect_ratio}' is not supported. Supported presets: square (1:1), story (9:16), landscape (16:9), portrait (3:4), ultrawide (21:9)."
    )

# ── Auth dependencies ─────────────────────────────────────────────────────────
def get_current_user(
    request: Request,
    authorization: str = Header(None),
    x_api_key: str = Header(None, alias="X-API-KEY"),
):
    if x_api_key:
        user = auth_module.verify_api_key(x_api_key)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        request.state.auth_mode = "api_key"
        return user

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization.split(" ")[1]

    try:
        user = org_auth.validate_org_module_jwt(token)
        request.state.auth_mode = "org_jwt"
        return user
    except HTTPException as e:
        if e.status_code != 401:
            raise
    except Exception:
        pass

    user_id = verify_token(token)
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            request.state.auth_mode = "legacy_jwt"
            return user

    raise HTTPException(status_code=401, detail="Invalid or expired credentials")


def get_admin_user(current_user=Depends(get_current_user)):
    org_role = (current_user.get("_org_context") or {}).get("role", "").lower()
    local_role = str(current_user.get("role") or "").lower()
    is_owner = current_user.get("email") == "muhammadhamzafaisal146@gmail.com"
    if org_role == "admin" or local_role == "admin" or is_owner:
        return current_user
    raise HTTPException(status_code=403, detail="Administrative privileges required")

# ── User / auth routes ────────────────────────────────────────────────────────
@app.post("/api/users/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    new_user = create_user(user_data)
    if not new_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return {
        "access_token": create_access_token(str(new_user["_id"])),
        "token_type": "bearer",
        "user": auth_module.user_doc_to_response(new_user),
    }


@app.get("/api/status")
async def get_status():
    return {
        "status": "online",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "stripe_configured": bool(os.getenv("STRIPE_SECRET_KEY")),
        "db_connected": auth_module.client is not None,
    }


@app.post("/api/users/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = verify_user_credentials(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {
        "access_token": create_access_token(str(user["_id"])),
        "token_type": "bearer",
        "user": user_doc_to_response(user),
    }


@app.post("/api/users/request-password-reset")
async def request_password_reset(req: ForgotPasswordRequest):
    from auth import get_user_by_email
    user = get_user_by_email(req.email)
    if not user:
        return {"message": "If email exists, reset link has been sent"}
    reset_token = create_password_reset_token(req.email)
    _, token = send_password_reset_email(req.email, reset_token)
    resp = {"message": "Password reset token created"}
    if token:
        resp["dev_token"] = token
        resp["message"] += " (Dev Mode)"
    return resp


@app.post("/api/users/reset-password")
async def reset_password(req: ResetPasswordRequest):
    if not reset_password_by_token(req.token, req.newPassword):
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"message": "Password reset successfully"}


@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_info(current_user=Depends(get_current_user)):
    return user_doc_to_response(current_user)


@app.post("/api/users/api-key")
async def create_api_key(type: str | None = None, current_user=Depends(get_current_user)):
    try:
        if type is None:
            if current_user.get("apiKeyHash"):
                raise ValueError("API key already exists")
            raw = auth_module.generate_api_key_for_user(str(current_user["_id"]))
            return {"message": "API key created", "api_key": raw}
        if (current_user.get("api_keys") or {}).get(f"{type}_hash"):
            raise ValueError("API key already exists for this type")
        raw = auth_module.generate_api_key_for_user(str(current_user["_id"]), type)
        return {"message": "API key created", "api_key": raw, "type": type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/users/api-key")
async def remove_api_key(type: str | None = None, current_user=Depends(get_current_user)):
    ok = (auth_module.delete_api_key(str(current_user["_id"]), type)
          if type else auth_module.delete_api_key(str(current_user["_id"])))
    if not ok:
        raise HTTPException(status_code=400, detail="No API key to delete")
    return {"message": "API key deleted", "type": type}

# ── Stripe routes ─────────────────────────────────────────────────────────────
@app.post("/api/stripe/create-checkout")
@app.post("/stripe/create-checkout")
@app.post("/create-checkout")
async def stripe_create_checkout(request: Request, body: dict = Body(...), current_user=Depends(get_current_user)):
    plan_code  = body.get("plan_code")  or body.get("planCode")
    engine_type = body.get("engine_type") or body.get("engineType") or "transformation"
    order_type  = body.get("order_type")  or body.get("orderType")  or "subscription"
    if not plan_code:
        raise HTTPException(status_code=400, detail="plan_code is required")
    try:
        url = create_checkout_session(str(current_user["_id"]), plan_code=plan_code, engine_type=engine_type, order_type=order_type)
        if not url:
            raise HTTPException(status_code=500, detail="Failed to create checkout session")
        return {"url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stripe/create-portal")
@app.post("/stripe/create-portal")
@app.post("/create-portal")
async def stripe_create_portal(current_user=Depends(get_current_user)):
    customer_id = current_user.get("stripeCustomerId")
    if not customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer on file")
    url = create_portal_session(customer_id)
    if not url:
        raise HTTPException(status_code=500, detail="Failed to create portal session")
    return {"url": url}


@app.post("/api/stripe/create-test-checkout")
async def stripe_create_test_checkout(current_user=Depends(get_current_user)):
    price_id = os.getenv("STRIPE_PRICE_TEST_DAILY")
    if not price_id:
        raise HTTPException(status_code=500, detail="Test price ID not configured")
    user_id = str(current_user["_id"])
    customer_id = current_user.get("stripeCustomerId")
    if not customer_id:
        customer = stripe.Customer.create(
            email=current_user.get("email"),
            metadata={"user_id": user_id},
        )
        customer_id = customer.id
        auth_module.users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"stripeCustomerId": customer_id}},
        )
    try:
        price_obj = stripe.Price.retrieve(price_id)
        is_recurring = price_obj.type == "recurring"
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription" if is_recurring else "payment",
            success_url=os.getenv("FRONTEND_URL") + "/billing/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=os.getenv("FRONTEND_URL") + "/billing/cancel",
            metadata={"user_id": user_id, "engine_type": "transformation", "order_type": "test", "plan_code": "daily_tester"},
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create test checkout: {e}")


@app.post("/api/stripe/webhook")
@app.post("/stripe/webhook")
@app.post("/secure/api/stripe/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None, alias="Stripe-Signature")):
    payload = await request.body()
    if not handle_webhook_event(payload, stripe_signature):
        raise HTTPException(status_code=400, detail="Webhook error")
    return {"received": True}


@app.post("/api/stripe/cancel-subscription")
async def stripe_cancel_subscription(body: dict | None = None, current_user=Depends(get_current_user)):
    engine_type  = None
    at_period_end = False
    if isinstance(body, dict):
        at_period_end = bool(body.get("at_period_end", False))
        engine_type   = body.get("engine_type")

    subscription_id = None
    if engine_type:
        subscription_id = (current_user.get("engine_data") or {}).get(engine_type, {}).get("stripeSubscriptionId")
    if not subscription_id:
        subscription_id = current_user.get("stripeSubscriptionId")
    subscription_id = (subscription_id or "").strip() or None
    user_id = str(current_user["_id"])

    if not subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription found")

    try:
        try:
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
        except stripe.error.InvalidRequestError:
            auth_module.users_collection.update_one({"_id": ObjectId(user_id)}, {"$unset": {"stripeSubscriptionId": ""}})
            raise HTTPException(status_code=400, detail="Subscription not found in Stripe. Account updated.")

        if stripe_sub.status == "canceled":
            auth_module.users_collection.update_one({"_id": ObjectId(user_id)}, {"$unset": {"stripeSubscriptionId": ""}})
            cancel_user_plan(user_id, engine_type=engine_type)
            raise HTTPException(status_code=400, detail="Subscription already cancelled.")

        cancel_subscription(subscription_id, at_period_end=at_period_end)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not at_period_end:
        cancel_user_plan(user_id, engine_type=engine_type)
    else:
        cancel_user_plan(user_id, engine_type=engine_type, is_pending=True)

    return {"cancelled": True, "at_period_end": at_period_end, "engine_type": engine_type}


async def _perform_stripe_sync(user_id: str, email: str, stripe_customer_id: str = None, session_id: str = None):
    users_col = auth_module.users_collection
    print(f"\n--- 🔄 STRIPE SYNC ({email}) ---")
    user = users_col.find_one({"_id": ObjectId(user_id)})
    if user and user.get("is_postpaid", False):
        return {"success": True, "detail": "Postpaid user - Stripe sync not applicable.", "plan": None}
    try:
        if session_id:
            try:
                s = stripe.checkout.Session.retrieve(session_id)
                stripe_customer_id = getattr(s, "customer", None)
                meta = getattr(s, "metadata", {}) or {}
                if meta.get("order_type") == "addon":
                    plan_code = meta.get("plan_code", "")
                    eng = meta.get("engine_type", "transformation")
                    amount = 50.0 if "50" in plan_code else 200.0 if "200" in plan_code else 100.0
                    from auth import add_addon_credits
                    add_addon_credits(user_id, amount, engine_type=eng)
                    return {"success": True, "detail": "Add-on credits applied.", "plan": "Add-on", "credits": amount}
            except Exception as e:
                print(f"⚠️ [SYNC] Session error: {e}")

        if not stripe_customer_id:
            users_col.update_one({"_id": ObjectId(user_id)}, {"$unset": {"stripeSubscriptionId": ""}})
            cancel_user_plan(user_id)
            return {"success": True, "detail": "No Stripe customer found.", "plan": None}

        users_col.update_one({"_id": ObjectId(user_id)}, {"$set": {"stripeCustomerId": stripe_customer_id}})
        subs = stripe.Subscription.list(customer=stripe_customer_id, status="all", limit=20).data

        active_subs = []
        for s in subs:
            meta = (getattr(s, "metadata", {}) or {})
            if meta.get("order_type") == "addon":
                continue
            status = getattr(s, "status", "")
            is_cancelling = getattr(s, "cancel_at_period_end", False) or getattr(s, "cancel_at", None)
            if status in ["active", "trialing", "past_due"] and not is_cancelling:
                active_subs.append(s)

        if not active_subs:
            users_col.update_one({"_id": ObjectId(user_id)}, {"$unset": {"stripeSubscriptionId": ""}})
            cancel_user_plan(user_id)
            return {"success": True, "detail": "No active subscriptions.", "plan": None}

        price_map = {k: v for k, v in {
            os.getenv("STRIPE_PRICE_T_STARTER"): ("Starter", "transformation"),
            os.getenv("STRIPE_PRICE_T_GROWTH"):  ("Growth",  "transformation"),
            os.getenv("STRIPE_PRICE_T_SCALE"):   ("Scale",   "transformation"),
            os.getenv("STRIPE_PRICE_M_STARTER"): ("Starter", "creation"),
            os.getenv("STRIPE_PRICE_M_GROWTH"):  ("Growth",  "creation"),
            os.getenv("STRIPE_PRICE_M_SCALE"):   ("Scale",   "creation"),
        }.items() if k}

        latest_plan = None
        for sub in active_subs:
            items = sub.get("items", {}).get("data", [])
            price_id = items[0].get("price", {}).get("id") if items else None
            if price_id and price_id in price_map:
                plan_code, eng = price_map[price_id]
            else:
                meta = sub.get("metadata", {}) or {}
                plan_code = meta.get("plan_code", "Starter")
                eng = meta.get("engine_type", "transformation")
            update_user_plan(user_id, plan_code, eng, subscription_id=sub.id)
            latest_plan = plan_code

        stats = get_user_usage_stats(user_id)
        return {"success": True, "plan": latest_plan, "credits": stats.get("remaining_units")}
    except Exception as e:
        print(f"❌ SYNC ERROR: {e}")
        return {"success": False, "detail": str(e)}


@app.post("/api/stripe/manual-sync")
async def manual_sync_subscription(request: dict):
    email = request.get("email")
    session_id = request.get("session_id")
    if not email and not session_id:
        raise HTTPException(status_code=400, detail="Email or session_id is required")
    users_col = auth_module.users_collection
    user = users_col.find_one({"email": email}) if email else None
    if not user and session_id:
        try:
            s = stripe.checkout.Session.retrieve(session_id)
            cid = getattr(s, "customer", None)
            if cid:
                user = users_col.find_one({"stripeCustomerId": cid})
        except Exception:
            pass
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.get("is_postpaid", False):
        return {"success": True, "detail": "Postpaid user.", "plan": None}
    res = await _perform_stripe_sync(str(user["_id"]), user.get("email"), user.get("stripeCustomerId"), session_id)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["detail"])
    return res


@app.post("/api/stripe/refresh-subscription")
async def refresh_subscription(current_user=Depends(get_current_user)):
    if current_user.get("is_postpaid", False):
        return {"success": True, "detail": "Postpaid user.", "plan": None}
    res = await _perform_stripe_sync(str(current_user["_id"]), current_user.get("email"), current_user.get("stripeCustomerId"))
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["detail"])
    return res

# ── Plan / billing routes ─────────────────────────────────────────────────────
@app.get("/api/plans")
async def get_plans():
    plans = get_all_plans()
    for p in plans:
        p["_id"] = str(p["_id"])
    return plans


@app.get("/api/users/usage")
async def get_usage(engine_type: str = None, current_user=Depends(get_current_user)):
    stats = get_user_usage_stats(str(current_user["_id"]), engine_type=engine_type)
    if not stats:
        raise HTTPException(status_code=404, detail="User not found")
    return stats


@app.get("/api/users/billing-history")
async def get_billing(current_user=Depends(get_current_user)):
    history = get_billing_history(str(current_user["_id"]))
    for b in history:
        b["_id"] = str(b["_id"])
    return history


@app.post("/api/billing/generate")
async def generate_bill(current_user=Depends(get_current_user)):
    bill = generate_monthly_bill(str(current_user["_id"]))
    if not bill:
        raise HTTPException(status_code=400, detail="Failed to generate bill")
    bill["_id"] = str(bill["_id"])
    return bill

# ── Image resize ──────────────────────────────────────────────────────────────
@app.post("/api/resize", response_class=JSONResponse)
async def resize_image(
    aspect_ratio: str = Form("1:1"),
    engine_type: str = Form("transformation"),
    file: UploadFile = File(None),
    prompt: str = Form(None),
    current_user=Depends(get_current_user),
):
    global client

    # Engine allocation check
    allocated = (
        (current_user.get("_org_context") or {}).get("selected_engines")
        or current_user.get("available_engines")
        or current_user.get("engine_access")
        or ["transformation", "creation"]
    )
    if isinstance(allocated, list) and engine_type not in allocated:
        raise HTTPException(status_code=403, detail=f"Engine '{engine_type}' not allocated for this user")

    if engine_type == "creation":
        if not _is_creation_allowed_ratio((aspect_ratio or "").strip()):
            raise HTTPException(status_code=403, detail="Creation engine only supports standard presets.")
        if not (prompt and prompt.strip()):
            raise HTTPException(status_code=400, detail="Creation engine requires a prompt.")
    elif engine_type == "transformation":
        if not file:
            raise HTTPException(status_code=400, detail="Transformation engine requires an image upload.")
        prompt = None  # ignore any prompt for transformation

    pil_image = None
    image_bytes = None
    if file:
        image_bytes = await file.read()
        if len(image_bytes) > 10 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large. Max 10MB.")
        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
        try:
            pil_image = await run_blocking(Image.open, io.BytesIO(image_bytes))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image format: {e}")

    is_postpaid = bool(current_user.get("is_postpaid", False))
    has_image = pil_image is not None
    has_custom_prompt = bool(prompt and prompt.strip()) and engine_type == "creation"
    tokens_to_deduct = (
        1.0 if is_postpaid
        else 6.0 if (engine_type == "creation" and has_image and has_custom_prompt)
        else 4.0
    )

    user_id = str(current_user["_id"])
    if not is_postpaid:
        eng_data = current_user.get("engine_data") or {}
        eng_credits = (eng_data.get(engine_type) or {}).get("credits") or {}
        if not eng_credits and current_user.get("engineType") == engine_type:
            eng_credits = current_user.get("credits") or {}
        remaining = float(eng_credits.get("remaining_units", 0.0))
        if remaining < tokens_to_deduct:
            raise HTTPException(
                status_code=429,
                detail=f"Insufficient credits. Need {tokens_to_deduct}, have {remaining}.",
            )

    gemini_ratio, (tw, th) = validate_aspect_ratio(aspect_ratio)

    if not client:
        load_dotenv()
        key = os.getenv("GOOGLE_API_KEY")
        client = genai.Client(api_key=key) if key else None
    if not client:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

    if prompt and prompt.strip():
        use_prompt = prompt
    else:
        use_prompt = (
            f"recreate this image in {gemini_ratio} ratio format and keep all the the information of image intact . "
            "you can rearrange the elements to ensure it is perfect."
        )

    contents = [use_prompt, pil_image] if has_image else [use_prompt]

    try:
        response = await call_gemini_with_retry(
            model_name="gemini-3-pro-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(aspect_ratio=gemini_ratio),
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {e}")

    image_data = None
    if response.parts:
        for part in response.parts:
            if part.inline_data:
                image_data = part.inline_data.data
                break
    if not image_data:
        raise HTTPException(status_code=500, detail="No image returned from AI.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id  = str(uuid.uuid4())[:8]
    filename   = f"resized_images/{timestamp}_{unique_id}.png"
    try:
        await run_blocking(
            s3_client.put_object,
            Bucket=DO_SPACES_BUCKET_NAME,
            Key=filename,
            Body=image_data,
            ContentType="image/png",
            ACL="public-read",
        )
        ep = DO_SPACES_ENDPOINT.replace("https://", "").replace("http://", "").strip()
        uploaded_url = f"https://{DO_SPACES_BUCKET_NAME}.{ep}/{filename}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    if not consume_units(user_id, tokens_to_deduct, engine_type=engine_type):
        raise HTTPException(status_code=429, detail="Insufficient credits.")
    try:
        increment_user_units(user_id)
    except Exception:
        pass

    log_id = log_usage(user_id, "resize", aspect_ratio, True, uploaded_url, prompt, [tw, th])
    image_name = f"{timestamp}_{unique_id}.png"

    return JSONResponse(content={"url": uploaded_url, "name": image_name, "logId": log_id}, status_code=200)

# ── History & feedback ────────────────────────────────────────────────────────
@app.get("/api/history")
async def get_history(current_user=Depends(get_current_user)):
    try:
        user_id = str(current_user["_id"])
        cursor = auth_module.usage_logs_collection.find(
            {"userId": user_id, "success": True, "imageUrl": {"$ne": None}, "is_deleted_from_s3": {"$ne": True}},
            sort=[("timestamp", -1)],
            limit=100,
        )
        history = [{
            "id":          str(doc["_id"]),
            "url":         doc.get("imageUrl", ""),
            "prompt":      doc.get("prompt", ""),
            "aspectRatio": doc.get("aspectRatio", "1:1"),
            "targetDims":  doc.get("targetDims"),
            "timestamp":   doc.get("timestamp", "").isoformat() if doc.get("timestamp") else "",
            "operation":   doc.get("operation", "resize"),
            "feedback":    doc.get("feedback"),
        } for doc in cursor]
        return JSONResponse(content={"history": history})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch history: {e}")


@app.post("/api/feedback")
async def submit_feedback(
    logId: str = Body(...),
    feedback: str = Body(...),
    current_user=Depends(get_current_user),
):
    if feedback not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="Feedback must be 'like' or 'dislike'")
    if not update_feedback(logId, str(current_user["_id"]), feedback):
        raise HTTPException(status_code=404, detail="Log entry not found")
    return JSONResponse(content={"success": True, "feedback": feedback})


from urllib.parse import urlparse

@app.delete("/api/dev/clean-user-archive")
async def clean_user_archive(email: str = Body(..., embed=True), current_user=Depends(get_current_user)):
    user = auth_module.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_id = str(user["_id"])
    docs = list(auth_module.usage_logs_collection.find(
        {"userId": user_id, "imageUrl": {"$ne": None}, "success": True}
    ))
    if not docs:
        return {"message": "No archive images found.", "deleted_count": 0}
    keys = [{"Key": urlparse(d["imageUrl"]).path.lstrip("/")} for d in docs if d.get("imageUrl")]
    ids  = [d["_id"] for d in docs]
    deleted = 0
    for i in range(0, len(keys), 1000):
        await run_blocking(
            s3_client.delete_objects,
            Bucket=DO_SPACES_BUCKET_NAME,
            Delete={"Objects": keys[i:i+1000], "Quiet": True},
        )
        deleted += len(keys[i:i+1000])
    result = auth_module.usage_logs_collection.update_many(
        {"_id": {"$in": ids}},
        {"$set": {"is_deleted_from_s3": True, "deletedAt": datetime.utcnow()}},
    )
    return {"message": f"Deleted {deleted} objects.", "deleted_s3_count": deleted, "hidden_logs_count": result.modified_count}


@app.post("/api/admin/trigger-billing-rollover")
async def trigger_billing_rollover(current_user=Depends(get_admin_user)):
    try:
        success = await asyncio.to_thread(perform_all_postpaid_rollovers, force=True)
        return {"message": "Rollover completed." if success else "Rollover already done for this month."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def read_root():
    return {"status": "Visual Engine API is running", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        limit_max_size=100 * 1024 * 1024,
        limit_concurrency=1000,
        timeout_keep_alive=65,
    )
