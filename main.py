from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Header, Request, Body
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io
import httpx
from datetime import datetime
import uuid
import boto3
import stripe
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
    consume_units, cancel_user_plan, update_user_plan
)
import auth as auth_module
from stripe_manager import create_checkout_session, create_portal_session, handle_webhook_event, cancel_subscription

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
    # API Key auth (preferred for server-to-server usage)
    if x_api_key:
        user = auth_module.verify_api_key(x_api_key)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid API key")
        # store key scope for downstream authorization decisions
        request.state.api_key_type = auth_module.get_api_key_type(user, x_api_key)
        request.state.auth_mode = "api_key"
        return user

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.split(" ")[1]
    user_id = verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    request.state.auth_mode = "jwt"
    return user

# Initialize Gemini Client (lazy init or global if key is present)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Vertex AI via google-genai SDK (uses service account, separate quota) ---
import json as _json
_vertex_project_id_env = os.getenv("VERTEX_PROJECT_ID")
_vertex_project_id_file = None
_vertex_sa_path = None
try:
    _possible_paths = [
        os.getenv("VERTEX_SA_PATH"),
        os.path.join(os.path.dirname(__file__), "vertex.json"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "vertex.json"),
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

# Create the Vertex AI client (uses service account credentials, separate quota)
vertex_client = None
if VERTEX_PROJECT_ID and _vertex_sa_path:
    try:
        vertex_client = genai.Client(
            vertexai=True,
            project=VERTEX_PROJECT_ID,
            location=VERTEX_LOCATION,
        )
        print(f"✅ [VERTEX] Client initialized (project={VERTEX_PROJECT_ID}, location={VERTEX_LOCATION})")
    except Exception as vc_err:
        print(f"⚠️  [VERTEX] Failed to create Vertex client: {vc_err}")
else:
    print("⚠️  [VERTEX] No Project ID or credentials found. Vertex AI will be skipped.")

# Fallback image generation service (Fal.ai Nano Banana Pro wrapper)
FAL_FALLBACK_URL = os.getenv(
    "FAL_FALLBACK_URL",
    "https://recreative.signagexai.com/fal-ai-fallback/generate",
)

# Gemini SDK client (uses GOOGLE_API_KEY)
client = None
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
else:
    print("Warning: GOOGLE_API_KEY not set in .env")

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

    res = await _perform_stripe_sync(str(user["_id"]), user.get("email"), user.get("stripeCustomerId"), session_id)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["detail"])
    return res


@app.post("/api/stripe/refresh-subscription")
async def refresh_subscription(current_user = Depends(get_current_user)):
    """Authenticated endpoint to refresh subscription status."""
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
        
        # Calculate token cost based on user requirements:
        # Creation Engine: <= 1024: 2.0, > 1024: 4.4
        # Transformation Engine: <= 1024: 1.0, > 1024: 2.5
        tokens_to_deduct = 1.0
        if engine_type == "creation":
            tokens_to_deduct = 2.0 if max_dim <= 1024 else 4.4
        else:
            tokens_to_deduct = 1.0 if max_dim <= 1024 else 2.5

        if pil_image:
            width, height = pil_image.size
            print(f"🖼️ [RESIZE] Image: {width}x{height} ({max_dim}px). Engine: {engine_type}. Cost: {tokens_to_deduct} tokens.")
        else:
            print(f"🎨 [GENERATE] Prompt-only generation ({max_dim}px default). Engine: {engine_type}. Cost: {tokens_to_deduct} tokens.")

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
        
        if remaining < tokens_to_deduct:
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

        # Construct the structured prompt
        if prompt:
            use_prompt = prompt
        else:
            use_prompt = (
                f"recreate this image in {gemini_aspect_ratio} ratio format and keep all the the information of image intact . "
                "you can rearrange the elements to ensure it is perfect."
            )

        # --- Primary: Vertex AI via google-genai SDK (High Priority) ---
        if not image_data and vertex_client:
            try:
                # Use the same model via Vertex AI backend (separate quota)
                v_model_name = "gemini-2.0-flash-exp"
                print(f"🧭 [PRIMARY] Invoking Vertex AI ({v_model_name}, project={VERTEX_PROJECT_ID})")

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
                print(f"📡 [PRIMARY] Vertex AI response received. Parts: {len(v_response.parts) if v_response.parts else 0}")

                if v_response.parts:
                    for part in v_response.parts:
                        extracted = extract_img_bytes(part)
                        if extracted:
                            image_data = extracted
                            print(f"🖼️ [PRIMARY] Extracted Vertex image: {len(image_data)} bytes")
                            break

                if not image_data:
                    print("❌ [PRIMARY] Vertex AI did not return image bytes.")

            except Exception as ve:
                vertex_error = ve
                print(f"❌ [PRIMARY] Vertex AI failed: {ve}")

        # --- Second: Gemini (google-genai SDK - Fallback 1) ---
        if not image_data and client:
            try:
                model_name = "gemini-3-pro-image-preview"
                print(f"🤖 [FALLBACK] Calling {model_name} (Gemini SDK) with prompt: '{use_prompt[:50]}...'")

                # Build contents based on whether we have an image
                if pil_image:
                    contents = [use_prompt, pil_image]
                else:
                    contents = [use_prompt]

                response = client.models.generate_content(
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
                print(f"❌ [FALLBACK] Fal.ai fallback failed: {fallback_err}")
                # Final failure: throw the best error we had
                base_error = vertex_error or gemini_error or fallback_err
                raise HTTPException(
                    status_code=500,
                    detail=f"Image generation failed (Vertex + Gemini + Fal.ai). Reason: {base_error}"
                )

        # 5. Post-process: Resize to exact requested dimensions
        # Parse the original aspect_ratio request to get target dimensions
        try:
            # original_aspect_ratio comes in as "WIDTHxHEIGHT" or "WIDTH:HEIGHT"
            original_ratio_str = original_aspect_ratio.replace(':', 'x')
            if 'x' in original_ratio_str:
                w_val, h_val = map(int, original_ratio_str.split('x'))
                # Threshold: If dimensions are very small (e.g., < 100), it's likely just a ratio (like 16:9)
                # We only want to post-process if we have actual target PIXELS (like 288x608)
                if w_val >= 100 and h_val >= 100:
                    target_width, target_height = w_val, h_val
                    print(f"🎯 [RESIZE] Detected exact target dimensions: {target_width}x{target_height}. Proceeding to post-process.")
                else:
                    target_width = target_height = None
                    print(f"ℹ️ [RESIZE] Aspect ratio '{original_aspect_ratio}' looks like a ratio, not dimensions. Skipping post-processing.")
            else:
                target_width = target_height = None
                print(f"ℹ️ [RESIZE] Aspect ratio '{original_aspect_ratio}' doesn't specify exact dimensions. Skipping post-processing.")
        except Exception as parse_err:
            print(f"⚠️ [RESIZE] Could not parse dimensions from '{original_aspect_ratio}': {parse_err}. Skipping post-processing.")
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

        # Log usage
        log_usage(
            user_id=user_id,
            operation="resize",
            aspect_ratio=aspect_ratio,
            success=True,
            image_url=uploaded_url
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
                image_url=None
            )
        except:
            pass
            
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error during image processing: {str(e)}"
        )

@app.get("/")
async def read_root():
    return FileResponse('index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
