import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
import secrets
import hmac
import hashlib
import sys
from models import User, UserRegister, UserLogin, ForgotPasswordRequest, ResetPasswordRequest
from passlib.context import CryptContext
from jose import JWTError, jwt
import smtplib
import bcrypt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT
# Use JWT_SECRET to avoid conflict with Digital Ocean SECRET_KEY
JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
SECRET_KEY = JWT_SECRET.strip("'\" ")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Extend to 1 week for better UX during development

# MongoDB
# Check both MONGODB_URI (production) and MONGODB_URL (fallback)
MONGODB_URL = os.getenv("MONGODB_URI") or os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "visual_engine")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "your-app-password")

# Initialize MongoDB
# Check both MONGODB_URI (production) and MONGODB_URL (fallback)
MONGODB_URL = (os.getenv("MONGODB_URI") or os.getenv("MONGODB_URL", "mongodb://localhost:27017")).strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine").strip("'\" ")

def get_db_client(url, max_retries=3):
    import time
    for i in range(max_retries):
        try:
            client = MongoClient(url, serverSelectionTimeoutMS=5000)
            # Force a command to verify connection
            client.admin.command('ping')
            return client
        except Exception as e:
            if i < max_retries - 1:
                print(f"Connection attempt {i+1} failed ({e}). Retrying in 2 seconds...")
                time.sleep(2)
            else:
                print(f"Failed to connect to MongoDB after {max_retries} attempts: {e}")
                raise

REQUIRE_MONGO = os.getenv("REQUIRE_MONGO", "true").lower() in ("1", "true", "yes", "on")
_is_pytest = ("pytest" in sys.modules) or bool(os.getenv("PYTEST_CURRENT_TEST"))

try:
    client = get_db_client(MONGODB_URL)
    db = client[DB_NAME]
    users_collection = db["users"]
    password_resets_collection = db["password_resets"]
    plans_collection = db["plans"]
    usage_logs_collection = db["usage_logs"]
    billing_records_collection = db["billing_records"]
    stripe_events_collection = db["stripe_events"]
    glenn_key_usage_collection = client["visual_engine"]["glenn_key_usage"]  # Shared DB for both backends
    org_db_name = os.getenv("ORG_DB_NAME", "organisation_db").strip("'\" ")
    org_users_collection = client[org_db_name]["users"]
    print("Connected to MongoDB successfully")

    # Create indexes
    users_collection.create_index("email", unique=True)
    password_resets_collection.create_index("createdAt", expireAfterSeconds=3600)  # Expire after 1 hour
    usage_logs_collection.create_index("userId")
    usage_logs_collection.create_index("timestamp")
    billing_records_collection.create_index("userId")
    billing_records_collection.create_index("billingPeriodStart")
    stripe_events_collection.create_index("event_id", unique=True)
except Exception as e:
    # Allow import in unit tests / dev without hard failing, unless explicitly required.
    client = None
    db = None
    users_collection = None
    password_resets_collection = None
    plans_collection = None
    usage_logs_collection = None
    billing_records_collection = None
    stripe_events_collection = None
    glenn_key_usage_collection = None
    org_users_collection = None
    print(f"Warning: MongoDB unavailable during import ({e}).")
    if REQUIRE_MONGO and not _is_pytest:
        raise


def _sync_org_module_credits_used(user_doc: dict) -> None:
    """Best-effort sync of creditsUsed into Organisation Module users collection."""
    if not user_doc or org_users_collection is None:
        return

    org_user_id = user_doc.get("org_module_user_id")
    if not org_user_id:
        return

    engine_data = user_doc.get("engine_data", {}) or {}
    transformation_credits = ((engine_data.get("transformation") or {}).get("credits") or {})
    creation_credits = ((engine_data.get("creation") or {}).get("credits") or {})

    transformation_used = float(transformation_credits.get("monthly_units_used", 0.0)) + float(
        transformation_credits.get("addon_units_used", 0.0)
    )
    creation_used = float(creation_credits.get("monthly_units_used", 0.0)) + float(
        creation_credits.get("addon_units_used", 0.0)
    )
    total_used = transformation_used + creation_used

    try:
        org_users_collection.update_one(
            {"id": org_user_id},
            {"$set": {"creditsUsed": total_used}},
        )
    except Exception as e:
        print(f"[CREDITS_SYNC] Failed syncing org creditsUsed for {org_user_id}: {e}")

# API key hashing secret (prefer explicit API_KEY_SECRET; fallback to JWT secret)
API_KEY_SECRET = (os.getenv("API_KEY_SECRET") or SECRET_KEY).encode("utf-8")

DEFAULT_SIGNUP_CREDITS = float(os.getenv("DEFAULT_SIGNUP_CREDITS", "0"))

# Utility functions
def hash_password(password: str) -> str:
    # Use bcrypt directly to avoid passlib compatibility issues with newer bcrypt versions
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Use bcrypt directly to avoid passlib compatibility issues with newer bcrypt versions
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def create_access_token(user_id: str, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except JWTError:
        return None

def get_user_by_email(email: str):
    user = users_collection.find_one({"email": email})
    return user

def get_user_by_id(user_id: str):
    from bson import ObjectId
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        return user
    except:
        return None

def create_user(user_data: UserRegister):
    from bson import ObjectId
    
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        return None
    
    user_doc = {
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "fullName": user_data.fullName or "",
        "fingerprint": user_data.fingerprint,
        "presentationId": user_data.presentationId,
        "plan": "",
        "engineType": "transformation",
        # Legacy counters (kept for backward compatibility; prefer credits.*)
        "units": 0,
        "maxUnits": int(DEFAULT_SIGNUP_CREDITS),
        # Unified credits ledger (monthly resets; addon persists)
        "credits": {
            "monthly_units_used": 0.0,
            "monthly_units_max": float(DEFAULT_SIGNUP_CREDITS),
            "addon_units_used": 0.0,
            "addon_units_max": 0.0,
            "remaining_units": float(DEFAULT_SIGNUP_CREDITS),
            "overageRate": 0.19,
        },
        # Engine-specific isolated data
        "engine_data": {
            "transformation": {
                "plan": "",
                "credits": {
                    "monthly_units_used": 0.0,
                    "monthly_units_max": float(DEFAULT_SIGNUP_CREDITS),
                    "addon_units_used": 0.0,
                    "addon_units_max": 0.0,
                    "remaining_units": float(DEFAULT_SIGNUP_CREDITS),
                    "overageRate": 0.19,
                },
                "is_pending_cancellation": False,
                "stripeSubscriptionId": None,
                "updatedAt": datetime.utcnow()
            },
            "creation": {
                "plan": "",
                "credits": {
                    "monthly_units_used": 0.0,
                    "monthly_units_max": 0.0,
                    "addon_units_used": 0.0,
                    "addon_units_max": 0.0,
                    "remaining_units": 0.0,
                    "overageRate": 0.19,
                },
                "is_pending_cancellation": False,
                "stripeSubscriptionId": None,
                "updatedAt": datetime.utcnow()
            }
        },
        # Scoped API keys (HMAC hashes only)
        "api_keys": {
            "resize_hash": None,
            "create_hash": None
        },
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    
    result = users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    return user_doc

def verify_user_credentials(email: str, password: str):
    user = get_user_by_email(email)
    if not user:
        return None
    
    if not verify_password(password, user["password"]):
        return None
    
    return user

def increment_user_units(user_id: str):
    from bson import ObjectId
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"units": 1}, "$set": {"updatedAt": datetime.utcnow()}}
    )
    return result.modified_count > 0

def _recompute_remaining_units(credits: dict) -> float:
    """Compute remaining units from monthly/addon max/used."""
    monthly_remaining = max(0.0, float(credits.get("monthly_units_max", 0.0)) - float(credits.get("monthly_units_used", 0.0)))
    addon_remaining = max(0.0, float(credits.get("addon_units_max", 0.0)) - float(credits.get("addon_units_used", 0.0)))
    return float(monthly_remaining + addon_remaining)


def update_user_plan(user_id: str, plan_code: str, engine_type: str = "transformation", subscription_id: str = None):
    """
    Update a specific engine subscription and keep its credit pool ISOLATED.
    """
    from bson import ObjectId
    plan_doc = plans_collection.find_one({"name": (plan_code or "").capitalize()})
    included_units = float(plan_doc["includedUnits"]) if plan_doc and "includedUnits" in plan_doc else 0.0
    
    user = users_collection.find_one({"_id": ObjectId(user_id)}) or {}
    engine_data = user.get("engine_data", {}) or {}
    
    # Get current engine state or default
    current_engine = engine_data.get(engine_type, {}) or {}
    credits_per_engine = current_engine.get("credits", {}) or {}
    
    addon_used = float(credits_per_engine.get("addon_units_used", 0.0))
    addon_max = float(credits_per_engine.get("addon_units_max", 0.0))
    
    # Preserve existing usage if engine already has a plan
    current_used = float(credits_per_engine.get("monthly_units_used", 0.0))
    # Reset usage to 0 ONLY if this is a brand new subscription (or if legacy units were 0)
    # If we are resuming or syncing an existing sub, we keep the usage.
    monthly_used = current_used
    
    new_engine_credits = {
        "monthly_units_used": monthly_used,
        "monthly_units_max": included_units,
        "addon_units_used": addon_used,
        "addon_units_max": addon_max,
        "overageRate": float(plan_doc.get("overageRate", 0.19)) if plan_doc else 0.19,
    }
    new_engine_credits["remaining_units"] = _recompute_remaining_units(new_engine_credits)
    
    # Update this specific engine's data
    engine_data[engine_type] = {
        "plan": (plan_code or ""),
        "credits": new_engine_credits,
        "is_pending_cancellation": False,
        "stripeSubscriptionId": subscription_id,
        "updatedAt": datetime.utcnow()
    }
    
    # Also update legacy/top-level fields (matches this engine as the active context)
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "plan": (plan_code or ""),
            "engineType": engine_type,
            "credits": new_engine_credits, # Sync top-level for FE convenience
            "is_pending_cancellation": False,
            "engine_data": engine_data, 
            "maxUnits": int(included_units),
            "units": 0,
            "stripeSubscriptionId": subscription_id, # Most recent sub ID
            "updatedAt": datetime.utcnow()
        }}
    )
    return result.modified_count > 0

def cancel_user_plan(user_id: str, engine_type: str = None, is_pending: bool = False):
    """
    Revert user to free tier for specific engine (no monthly credits). 
    Addon credits remain.
    If engine_type is None, clears the top-level plan (legacy behavior).
    If is_pending=True, we keep the plan name but reset credits (shows Cancelling in UI).
    """
    from bson import ObjectId
    user = users_collection.find_one({"_id": ObjectId(user_id)}) or {}
    credits = user.get("credits", {}) or {}
    engine_data = user.get("engine_data", {}) or {}
    
    new_credits = {
        "monthly_units_used": 0.0,
        "monthly_units_max": 0.0,
        "addon_units_used": float(credits.get("addon_units_used", 0.0)),
        "addon_units_max": float(credits.get("addon_units_max", 0.0)),
        "overageRate": float(credits.get("overageRate", 0.19)),
        "is_pending_cancellation": is_pending
    }
    new_credits["remaining_units"] = _recompute_remaining_units(new_credits)
    
    # If engine_type specified, only cancel that engine's subscription
    if engine_type:
        if engine_type in engine_data:
            # Clear this engine's plan (unless pending) and reset its credits
            prev_plan = engine_data[engine_type].get("plan", "")
            prev_sub_id = engine_data[engine_type].get("stripeSubscriptionId", "")
            engine_data[engine_type] = {
                "plan": prev_plan if is_pending else "",
                "credits": {
                    "monthly_units_used": 0.0,
                    "monthly_units_max": 0.0,
                    "addon_units_used": float(engine_data[engine_type].get("credits", {}).get("addon_units_used", 0.0)),
                    "addon_units_max": float(engine_data[engine_type].get("credits", {}).get("addon_units_max", 0.0)),
                    "overageRate": float(engine_data[engine_type].get("credits", {}).get("overageRate", 0.19)),
                    "is_pending_cancellation": is_pending
                },
                "is_pending_cancellation": is_pending,
                "stripeSubscriptionId": prev_sub_id if is_pending else "",
                "updatedAt": datetime.utcnow()
            }
            engine_data[engine_type]["credits"]["remaining_units"] = _recompute_remaining_units(engine_data[engine_type]["credits"])
        
        # Decide if we should unset the top-level stripeSubscriptionId
        # We only unset it if NO OTHER ENGINE has a subscription ID left
        remaining_subs = [
            info.get("stripeSubscriptionId") 
            for info in engine_data.values() 
            if info and info.get("stripeSubscriptionId")
        ]
        
        update_doc = {
            "engine_data": engine_data,
            "updatedAt": datetime.utcnow()
        }
        
        # If this was the active engine, clear top-level plan/credits too
        # CRITICAL FIX: Only update top-level if this specific engine is the active one
        user_engine_type = user.get("engineType", "transformation")
        if user_engine_type == engine_type:
             prev_top_plan = user.get("plan", "")
             prev_top_sub_id = user.get("stripeSubscriptionId", "")
             update_doc.update({
                "plan": prev_top_plan if is_pending else "",
                "credits": new_credits,
                "is_pending_cancellation": is_pending,
                "maxUnits": 0,
                "units": 0,
             })
             # Only set/update stripeSubscriptionId if we are in pending mode
             # If not pending, we will either unset it (if no other engines have it) or update it to another engine's ID
             if is_pending:
                update_doc["stripeSubscriptionId"] = prev_top_sub_id
             else:
                # If not pending, and this was our active sub, we should clear it top-level
                # BUT if we are about to unset it globally, we don't need to set it to "" here.
                # We'll handle top-level sub ID consolidation below.
                pass

        # Consolidate top-level stripeSubscriptionId
        unset_doc = {}
        if is_pending:
            # For pending, keep the current sub ID top-level if we are resetting the active engine
            if user_engine_type == engine_type or not engine_type:
                update_doc["stripeSubscriptionId"] = user.get("stripeSubscriptionId")
        else:
            if remaining_subs:
                # Pick any remaining active sub ID for the top-level
                update_doc["stripeSubscriptionId"] = remaining_subs[0]
            else:
                # No subs left anywhere, unset globally
                unset_doc["stripeSubscriptionId"] = ""

        # Perform the update
        if unset_doc:
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_doc, "$unset": unset_doc}
            )
        else:
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_doc}
            )
    else:
        # Legacy: cancel all engines' plans
        for engine in list(engine_data.keys()):
            if engine_data[engine]:
                engine_data[engine]["plan"] = ""
                # Keep addon credits
                addon_used = float(engine_data[engine].get("credits", {}).get("addon_units_used", 0.0))
                addon_max = float(engine_data[engine].get("credits", {}).get("addon_units_max", 0.0))
                engine_data[engine]["credits"] = {
                    "monthly_units_used": 0.0,
                    "monthly_units_max": 0.0,
                    "addon_units_used": addon_used,
                    "addon_units_max": addon_max,
                }
                engine_data[engine]["credits"]["remaining_units"] = _recompute_remaining_units(engine_data[engine]["credits"])
                engine_data[engine]["updatedAt"] = datetime.utcnow()
        
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "plan": "",
                "credits": new_credits,
                "maxUnits": 0,
                "units": 0,
                "engine_data": engine_data,
                "updatedAt": datetime.utcnow()
            }, "$unset": {"stripeSubscriptionId": ""}}
        )
    return result.modified_count > 0


def reset_monthly_credits(user_id: str):
    """Reset monthly usage to 0 for all engines with active plans."""
    from bson import ObjectId
    user = users_collection.find_one({"_id": ObjectId(user_id)}) or {}
    engine_data = user.get("engine_data", {}) or {}
    
    updated_any = False
    for engine_type, engine_info in engine_data.items():
        plan_name = (engine_info.get("plan") or "").capitalize()
        if plan_name:
            plan_doc = plans_collection.find_one({"name": plan_name})
            included_units = float(plan_doc["includedUnits"]) if plan_doc and "includedUnits" in plan_doc else 0.0
            
            credits = engine_info.get("credits", {}) or {}
            new_credits = {
                "monthly_units_used": 0.0,
                "monthly_units_max": included_units,
                "addon_units_used": float(credits.get("addon_units_used", 0.0)),
                "addon_units_max": float(credits.get("addon_units_max", 0.0)),
                "overageRate": float(plan_doc.get("overageRate", 0.19)) if plan_doc else 0.19,
            }
            new_credits["remaining_units"] = _recompute_remaining_units(new_credits)
            
            engine_data[engine_type]["credits"] = new_credits
            engine_data[engine_type]["updatedAt"] = datetime.utcnow()
            updated_any = True
    
    if updated_any:
        # Also sync top-level if the active engine was reset
        active_engine = user.get("engineType", "transformation")
        top_credits = engine_data.get(active_engine, {}).get("credits", user.get("credits", {}))
        
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "engine_data": engine_data,
                "credits": top_credits,
                "maxUnits": int(top_credits.get("monthly_units_max", 0)),
                "units": 0,
                "updatedAt": datetime.utcnow()
            }}
        )
        return True
    
    # Fallback legacy behavior
    plan_name = (user.get("plan") or "").capitalize()
    plan_doc = plans_collection.find_one({"name": plan_name}) if plan_name else None
    included_units = float(plan_doc["includedUnits"]) if plan_doc and "includedUnits" in plan_doc else 0.0
    credits = user.get("credits", {}) or {}
    new_credits = {
        "monthly_units_used": 0.0,
        "monthly_units_max": included_units,
        "addon_units_used": float(credits.get("addon_units_used", 0.0)),
        "addon_units_max": float(credits.get("addon_units_max", 0.0)),
    }
    new_credits["remaining_units"] = _recompute_remaining_units(new_credits)
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"credits": new_credits, "maxUnits": int(included_units), "units": 0, "updatedAt": datetime.utcnow()}}
    )
    return True


def add_addon_credits(user_id: str, amount: float, engine_type: str = "transformation"):
    """Add one-time addon units (persist across billing cycles)."""
    from bson import ObjectId
    user = users_collection.find_one({"_id": ObjectId(user_id)}) or {}
    engine_data = user.get("engine_data", {}) or {}
    
    # Update engine-specific credits
    current_engine = engine_data.get(engine_type, {}) or {}
    credits = current_engine.get("credits", {}) or {}
    
    # If no engine credits yet, fallback to top-level or default
    if not credits:
        credits = user.get("credits", {}) or {}

    addon_max = float(credits.get("addon_units_max", 0.0)) + float(amount)
    new_engine_credits = {
        "monthly_units_used": float(credits.get("monthly_units_used", 0.0)),
        "monthly_units_max": float(credits.get("monthly_units_max", 0.0)),
        "addon_units_used": float(credits.get("addon_units_used", 0.0)),
        "addon_units_max": addon_max,
        "overageRate": float(credits.get("overageRate", 0.19)),
    }
    new_engine_credits["remaining_units"] = _recompute_remaining_units(new_engine_credits)
    
    # Update engine_data entry
    if engine_type not in engine_data:
        engine_data[engine_type] = {
            "plan": user.get("plan", ""),
            "credits": new_engine_credits,
            "updatedAt": datetime.utcnow()
        }
    else:
        engine_data[engine_type]["credits"] = new_engine_credits
        engine_data[engine_type]["updatedAt"] = datetime.utcnow()

    # Also sync top-level if the active engine was updated
    active_engine = user.get("engineType", "transformation")
    top_update = {
        "engine_data": engine_data,
        "updatedAt": datetime.utcnow()
    }
    
    if active_engine == engine_type:
        top_update["credits"] = new_engine_credits
        # Keep legacy maxUnits roughly in sync
        top_update["maxUnits"] = int(new_engine_credits["monthly_units_max"] + new_engine_credits["addon_units_max"])

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": top_update}
    )
    return result.modified_count > 0


def consume_units(user_id: str, amount: float = 1.0, engine_type: str = "transformation") -> bool:
    """
    Deduct units from a specific engine pool using priority monthly -> addon.
    """
    from bson import ObjectId
    user = users_collection.find_one({"_id": ObjectId(user_id)}) or {}
    engine_data = user.get("engine_data", {}) or {}
    
    # Get credits for the specific engine
    credits = (engine_data.get(engine_type) or {}).get("credits", {})
    if not credits:
        # Fallback to top-level if engine_data is missing (unlikely now)
        credits = user.get("credits", {}) or {}

    monthly_used = float(credits.get("monthly_units_used", 0.0))
    monthly_max = float(credits.get("monthly_units_max", 0.0))
    addon_used = float(credits.get("addon_units_used", 0.0))
    addon_max = float(credits.get("addon_units_max", 0.0))

    # PostPaid users are pay-as-you-go: never block on remaining units.
    if user.get("is_postpaid", False):
        monthly_used += float(amount)

        new_engine_credits = {
            "monthly_units_used": monthly_used,
            "monthly_units_max": monthly_max,
            "addon_units_used": addon_used,
            "addon_units_max": addon_max,
            "overageRate": float(credits.get("overageRate", 0.19)),
            "remaining_units": 0.0,
        }

        if engine_type not in engine_data:
            engine_data[engine_type] = {"plan": user.get("plan", ""), "credits": new_engine_credits}
        else:
            engine_data[engine_type]["credits"] = new_engine_credits

        update_payload = {
            "engine_data": engine_data,
            "updatedAt": datetime.utcnow(),
            "is_postpaid": True,
        }

        if user.get("engineType") == engine_type:
            update_payload["credits"] = new_engine_credits
            update_payload["units"] = int(monthly_used)

        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_payload}
        )
        if result.modified_count > 0:
            refreshed_user = users_collection.find_one({"_id": ObjectId(user_id)})
            try:
                _sync_org_module_credits_used(refreshed_user)
            except Exception as e:
                print(f"[CREDITS_SYNC] Non-fatal postpaid sync error for {user_id}: {e}")
        return result.modified_count > 0

    monthly_remaining = max(0.0, monthly_max - monthly_used)
    addon_remaining = max(0.0, addon_max - addon_used)

    if monthly_remaining + addon_remaining < float(amount):
        return False

    remaining_to_deduct = float(amount)
    if monthly_remaining > 0:
        take = min(monthly_remaining, remaining_to_deduct)
        monthly_used += take
        remaining_to_deduct -= take

    if remaining_to_deduct > 0:
        addon_used += remaining_to_deduct

    new_engine_credits = {
        "monthly_units_used": monthly_used,
        "monthly_units_max": monthly_max,
        "addon_units_used": addon_used,
        "addon_units_max": addon_max,
        "overageRate": float(credits.get("overageRate", 0.19)),
    }
    new_engine_credits["remaining_units"] = _recompute_remaining_units(new_engine_credits)

    # Update engine_data
    if engine_type not in engine_data:
        engine_data[engine_type] = {"plan": user.get("plan", ""), "credits": new_engine_credits}
    else:
        engine_data[engine_type]["credits"] = new_engine_credits

    update_payload = {
        "engine_data": engine_data,
        "updatedAt": datetime.utcnow()
    }

    # If this is the engine currently displayed at top-level, sync it
    if user.get("engineType") == engine_type:
        update_payload["credits"] = new_engine_credits
        update_payload["units"] = int(monthly_used)

    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_payload}
    )
    if result.modified_count > 0:
        refreshed_user = users_collection.find_one({"_id": ObjectId(user_id)})
        try:
            _sync_org_module_credits_used(refreshed_user)
        except Exception as e:
            print(f"[CREDITS_SYNC] Non-fatal prepaid sync error for {user_id}: {e}")
    return result.modified_count > 0


def update_user_engine(user_id: str, engine_type: str):
    from bson import ObjectId
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"engineType": engine_type, "updatedAt": datetime.utcnow()}}
    )
    return result.modified_count > 0


def _hash_api_key(raw_api_key: str) -> str:
    digest = hmac.new(API_KEY_SECRET, raw_api_key.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest


def generate_api_key_for_user(user_id: str, key_type: str = None) -> str:
    """
    Generate a new raw API key (returned once) and store only its HMAC hash.
    If key_type is provided ("resize" or "create"), store under `api_keys.{type}_hash`.
    Otherwise store under legacy `apiKeyHash`.
    """
    from bson import ObjectId
    raw = secrets.token_urlsafe(32)
    hashed = _hash_api_key(raw)

    user = users_collection.find_one({"_id": ObjectId(user_id)}) or {}
    if key_type in ("resize", "create"):
        field = f"api_keys.{key_type}_hash"
        if user.get("api_keys", {}).get(f"{key_type}_hash"):
            raise ValueError("API key already exists for this type")
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {field: hashed, "updatedAt": datetime.utcnow()}})
    else:
        if user.get("apiKeyHash"):
            raise ValueError("API key already exists")
        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"apiKeyHash": hashed, "updatedAt": datetime.utcnow()}})

    return raw


def verify_api_key(raw_api_key: str):
    """Verify an API key against stored HMAC hashes (scoped or legacy)."""
    hashed = _hash_api_key(raw_api_key)
    user = users_collection.find_one({
        "$or": [
            {"apiKeyHash": hashed},
            {"api_keys.resize_hash": hashed},
            {"api_keys.create_hash": hashed},
        ]
    })
    return user


def get_api_key_type(user_doc: dict, raw_api_key: str) -> str | None:
    """Return key scope ('resize'|'create'|None) for a given authenticated raw key."""
    if not user_doc:
        return None
    hashed = _hash_api_key(raw_api_key)
    api_keys = user_doc.get("api_keys", {}) or {}
    if api_keys.get("resize_hash") == hashed:
        return "resize"
    if api_keys.get("create_hash") == hashed:
        return "create"
    return None


def delete_api_key(user_id: str, key_type: str = None) -> bool:
    """Delete stored API key hash (scoped or legacy)."""
    from bson import ObjectId
    if key_type in ("resize", "create"):
        field = f"api_keys.{key_type}_hash"
        result = users_collection.update_one(
            {"_id": ObjectId(user_id), field: {"$ne": None}},
            {"$set": {field: None, "updatedAt": datetime.utcnow()}}
        )
        return result.modified_count > 0

    result = users_collection.update_one(
        {"_id": ObjectId(user_id), "apiKeyHash": {"$exists": True}},
        {"$unset": {"apiKeyHash": ""}, "$set": {"updatedAt": datetime.utcnow()}}
    )
    return result.modified_count > 0

def reset_user_units(user_id: str):
    from bson import ObjectId
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"units": 0, "updatedAt": datetime.utcnow()}}
    )
    return result.modified_count > 0

def create_password_reset_token(email: str) -> str:
    token = str(uuid.uuid4())
    password_resets_collection.insert_one({
        "email": email,
        "token": token,
        "createdAt": datetime.utcnow(),
    })
    return token

def verify_password_reset_token(token: str):
    reset_doc = password_resets_collection.find_one({"token": token})
    return reset_doc

def reset_password_by_token(token: str, new_password: str):
    reset_doc = verify_password_reset_token(token)
    if not reset_doc:
        return False
    
    email = reset_doc["email"]
    user = get_user_by_email(email)
    if not user:
        return False
    
    from bson import ObjectId
    users_collection.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"password": hash_password(new_password), "updatedAt": datetime.utcnow()}}
    )
    
    password_resets_collection.delete_one({"token": token})
    return True

def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email - returns token for development mode"""
    # Check if we're in development mode (no valid email credentials)
    is_dev_mode = (
        not SENDER_EMAIL or SENDER_EMAIL == "your-email@gmail.com" or
        not SENDER_PASSWORD or SENDER_PASSWORD == "your-app-password"
    )
    
    if is_dev_mode:
        print(f"[DEV MODE] Password reset token for {email}: {reset_token}")
        return True, reset_token  # Return token for testing
    
    try:
        reset_link = f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/auth?form=reset&token={reset_token}"
        
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Request"
        message["From"] = SENDER_EMAIL
        message["To"] = email
        
        html = f"""\
        <html>
            <body>
                <h2>Password Reset Request</h2>
                <p>You have requested to reset your password. Click the link below to proceed:</p>
                <a href="{reset_link}">Reset Password</a>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </body>
        </html>
        """
        
        part = MIMEText(html, "html")
        message.attach(part)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, email, message.as_string())
        
        print(f"Password reset email sent to {email}")
        return True, None
    except Exception as e:
        print(f"Error sending email to {email}: {e}")
        print(f"Reset token (for manual testing): {reset_token}")
        return False, reset_token  # Return token even if email fails

def user_doc_to_response(user_doc):
    """Convert MongoDB user document to response format"""
    # Use the credits object (which is the current active engine's context)
    credits = user_doc.get("credits", {}) or {}
    
    # Robust remaining units calculation
    # 1. Try explicit remaining_units in the active credits pool
    remaining = credits.get("remaining_units")
    
    # 2. If not found or None (often the case in manual DB edits), calculate from max-used
    if remaining is None:
        remaining = float(user_doc.get("maxUnits", 0) - user_doc.get("units", 0))
    else:
        remaining = float(remaining)

    engine_data = user_doc.get("engine_data", {}) or {}
    org_context = user_doc.get("_org_context", {}) or {}
    selected_engines = org_context.get("selected_engines") or []
    available_engines = selected_engines if selected_engines else ["transformation", "creation"]
    
    # Lazy migration: ensure both engines are present in the response
    for etype in ["transformation", "creation"]:
        if etype not in engine_data:
            # If missing, use top-level credits if this was once the only engine
            # or default to empty
            source_credits = credits if user_doc.get("engineType") == etype else {
                "monthly_units_used": 0.0,
                "monthly_units_max": 0.0,
                "addon_units_used": 0.0,
                "addon_units_max": 0.0,
                "remaining_units": 0.0,
                "overageRate": 0.19
            }
            engine_data[etype] = {
                "plan": user_doc.get("plan", "") if user_doc.get("engineType") == etype else "",
                "credits": source_credits,
                "is_pending_cancellation": user_doc.get("is_pending_cancellation", False) if user_doc.get("engineType") == etype else False,
                "stripeSubscriptionId": user_doc.get("stripeSubscriptionId") if user_doc.get("engineType") == etype else None,
                "updatedAt": user_doc.get("updatedAt", datetime.utcnow())
            }

    return {
        "id": str(user_doc["_id"]),
        "email": user_doc["email"],
        "fullName": user_doc.get("fullName", ""),
        "avatar": user_doc.get("avatar"),
        "plan": user_doc.get("plan", ""),
        "engineType": user_doc.get("engineType", "transformation"),
        "units": user_doc.get("units", 0),
        "maxUnits": user_doc.get("maxUnits", 0),
        "remainingUnits": remaining,
        "credits": credits,
        "engine_data": engine_data,
        "available_engines": available_engines,
        "stripeCustomerId": user_doc.get("stripeCustomerId"),
        "stripeSubscriptionId": user_doc.get("stripeSubscriptionId"),
        "is_postpaid": user_doc.get("is_postpaid", False),
        "createdAt": user_doc.get("createdAt"),
    }

def log_usage(user_id: str, operation: str, aspect_ratio: str, success: bool, image_url: str = None, prompt: str = None, target_dims: list = None):
    """Log a usage operation for billing purposes"""
    usage_doc = {
        "userId": user_id,
        "operation": operation,
        "aspectRatio": aspect_ratio,
        "timestamp": datetime.utcnow(),
        "success": success,
        "imageUrl": image_url
    }
    if prompt:
        usage_doc["prompt"] = prompt
    if target_dims:
        usage_doc["targetDims"] = target_dims
    usage_logs_collection.insert_one(usage_doc)
    return True

def get_user_usage_stats(user_id: str, engine_type: str = None):
    """Get usage statistics for a user, optionally for a specific engine."""
    from bson import ObjectId
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    # If engine_type is specified, use engine-specific data
    if engine_type:
        engine_data = user.get("engine_data", {})
        engine_info = engine_data.get(engine_type)
        if engine_info:
            credits = engine_info.get("credits", {})
            return {
                "userId": user_id,
                "engineType": engine_type,
                "plan": engine_info.get("plan") or "free tier",
                "unitsUsed": credits.get("monthly_units_used", 0) + credits.get("addon_units_used", 0),
                "maxUnits": credits.get("monthly_units_max", 0) + credits.get("addon_units_max", 0),
                "remaining_units": credits.get("remaining_units", 0),
                "overageRate": credits.get("overageRate", 0.19),
                "monthlyRemaining": max(0, credits.get("monthly_units_max", 0) - credits.get("monthly_units_used", 0)),
                "addonRemaining": max(0, credits.get("addon_units_max", 0) - credits.get("addon_units_used", 0))
            }

    # Fallback to legacy/top-level behavior
    # Get current billing period usage
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    usage_count = usage_logs_collection.count_documents({
        "userId": user_id,
        "timestamp": {"$gte": current_month_start},
        "success": True
    })
    
    credits = user.get("credits", {})
    return {
        "userId": user_id,
        "plan": user.get("plan") or "free tier",
        "unitsUsed": user.get("units", 0),
        "maxUnits": user.get("maxUnits", 200),
        "remainingUnits": user.get("maxUnits", 200) - user.get("units", 0),
        "remaining_units": credits.get("remaining_units", user.get("maxUnits", 200) - user.get("units", 0)),
        "overageUnits": max(0, user.get("units", 0) - user.get("maxUnits", 200)),
        "overageRate": credits.get("overageRate", 0.19),
        "currentMonthOperations": usage_count
    }

def calculate_overage_charge(units_used: int, max_units: int, overage_rate: float = 0.19):
    """Calculate overage charges"""
    if units_used <= max_units:
        return 0.0
    overage_units = units_used - max_units
    return round(overage_units * overage_rate, 2)

def send_billing_statement_email(user: dict, bill_doc: dict):
        """Send billing statement email to the user after bill generation."""
        recipient = (user or {}).get("email")
        if not recipient:
                return False, "Missing recipient email"

        is_dev_mode = (
                not SENDER_EMAIL or SENDER_EMAIL == "your-email@gmail.com" or
                not SENDER_PASSWORD or SENDER_PASSWORD == "your-app-password"
        )

        period_start = bill_doc.get("billingPeriodStart")
        period_end = bill_doc.get("billingPeriodEnd")
        period_start_str = period_start.strftime("%Y-%m-%d") if isinstance(period_start, datetime) else "-"
        period_end_str = period_end.strftime("%Y-%m-%d") if isinstance(period_end, datetime) else "-"

        plan_name = bill_doc.get("plan", "-")
        total_amount = float(bill_doc.get("totalAmount", 0.0))
        units_used = float(bill_doc.get("unitsUsed", 0.0))
        overage_charge = float(bill_doc.get("overageCharge", 0.0))

        engine_breakdown = bill_doc.get("engineBreakdown") or {}
        has_engine_breakdown = bool(engine_breakdown)

        breakdown_rows = ""
        if has_engine_breakdown:
                for engine_name in ["transformation", "creation"]:
                        data = engine_breakdown.get(engine_name) or {}
                        breakdown_rows += f"""
                                <tr>
                                        <td style='padding:8px;border:1px solid #e5e7eb;text-transform:capitalize'>{engine_name}</td>
                                        <td style='padding:8px;border:1px solid #e5e7eb'>{float(data.get('unitsUsed', 0.0)):.4f}</td>
                                        <td style='padding:8px;border:1px solid #e5e7eb'>${float(data.get('ratePerCredit', 0.0)):.4f}</td>
                                        <td style='padding:8px;border:1px solid #e5e7eb'>${float(data.get('amount', 0.0)):.2f}</td>
                                </tr>
                        """

        html = f"""
        <html>
            <body style='font-family:Arial,sans-serif;color:#111827'>
                <h2 style='margin-bottom:4px'>Your Billing Statement</h2>
                <p style='margin-top:0;color:#6b7280'>Billing period: {period_start_str} to {period_end_str}</p>

                <table style='border-collapse:collapse;width:100%;max-width:680px;margin-top:16px'>
                    <tr>
                        <td style='padding:8px;border:1px solid #e5e7eb;background:#f8fafc'><strong>Plan</strong></td>
                        <td style='padding:8px;border:1px solid #e5e7eb'>{plan_name}</td>
                    </tr>
                    <tr>
                        <td style='padding:8px;border:1px solid #e5e7eb;background:#f8fafc'><strong>Total Units Used</strong></td>
                        <td style='padding:8px;border:1px solid #e5e7eb'>{units_used:.4f}</td>
                    </tr>
                    <tr>
                        <td style='padding:8px;border:1px solid #e5e7eb;background:#f8fafc'><strong>Overage Charge</strong></td>
                        <td style='padding:8px;border:1px solid #e5e7eb'>${overage_charge:.2f}</td>
                    </tr>
                    <tr>
                        <td style='padding:8px;border:1px solid #e5e7eb;background:#f8fafc'><strong>Total Amount</strong></td>
                        <td style='padding:8px;border:1px solid #e5e7eb'><strong>${total_amount:.2f}</strong></td>
                    </tr>
                </table>

                {f"<h3 style='margin-top:24px'>Engine Breakdown</h3><table style='border-collapse:collapse;width:100%;max-width:680px'><tr><th style='text-align:left;padding:8px;border:1px solid #e5e7eb;background:#f8fafc'>Engine</th><th style='text-align:left;padding:8px;border:1px solid #e5e7eb;background:#f8fafc'>Units Used</th><th style='text-align:left;padding:8px;border:1px solid #e5e7eb;background:#f8fafc'>Rate / Credit</th><th style='text-align:left;padding:8px;border:1px solid #e5e7eb;background:#f8fafc'>Amount</th></tr>{breakdown_rows}</table>" if has_engine_breakdown else ""}

                <p style='margin-top:20px;color:#6b7280'>If you have any questions about this statement, please contact support.</p>
            </body>
        </html>
        """

        if is_dev_mode:
                print(f"[DEV MODE] Billing statement for {recipient}: total=${total_amount:.2f}, period={period_start_str}..{period_end_str}")
                return True, None

        try:
                message = MIMEMultipart("alternative")
                message["Subject"] = f"Visual Engine Billing Statement ({period_start_str} to {period_end_str})"
                message["From"] = SENDER_EMAIL
                message["To"] = recipient
                message.attach(MIMEText(html, "html"))

                with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SENDER_EMAIL, SENDER_PASSWORD)
                        server.sendmail(SENDER_EMAIL, recipient, message.as_string())

                print(f"Billing statement email sent to {recipient}")
                return True, None
        except Exception as e:
                print(f"Error sending billing statement email to {recipient}: {e}")
                return False, str(e)

def generate_monthly_bill(user_id: str):
    """Generate a monthly bill for a user"""
    from bson import ObjectId
    user = get_user_by_id(user_id)
    if not user:
        return None

    # Postpaid users are billed manually: usage * org-configured per-credit rate.
    if user.get("is_postpaid", False):
        now = datetime.utcnow()
        period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            period_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)

        engine_data = user.get("engine_data", {}) or {}
        transformation_credits = ((engine_data.get("transformation") or {}).get("credits") or {})
        creation_credits = ((engine_data.get("creation") or {}).get("credits") or {})

        transformation_used = float(transformation_credits.get("monthly_units_used", 0.0))
        creation_used = float(creation_credits.get("monthly_units_used", 0.0))

        transformation_rate = float(transformation_credits.get("overageRate", 0.19))
        creation_rate = float(creation_credits.get("overageRate", 0.19))

        transformation_amount = round(transformation_used * transformation_rate, 2)
        creation_amount = round(creation_used * creation_rate, 2)
        total_amount = round(transformation_amount + creation_amount, 2)

        bill_doc = {
            "userId": user_id,
            "billingPeriodStart": period_start,
            "billingPeriodEnd": period_end,
            "plan": "PostPaid Manual Invoice",
            "basePrice": 0.0,
            "includedUnits": 0,
            "unitsUsed": round(transformation_used + creation_used, 4),
            "overageUnits": round(transformation_used + creation_used, 4),
            "overageCharge": total_amount,
            "totalAmount": total_amount,
            "engineBreakdown": {
                "transformation": {
                    "unitsUsed": round(transformation_used, 4),
                    "ratePerCredit": transformation_rate,
                    "amount": transformation_amount,
                },
                "creation": {
                    "unitsUsed": round(creation_used, 4),
                    "ratePerCredit": creation_rate,
                    "amount": creation_amount,
                },
            },
            "generatedAt": datetime.utcnow(),
            "status": "pending",
        }

        result = billing_records_collection.insert_one(bill_doc)
        bill_doc["_id"] = result.inserted_id
        email_sent, email_error = send_billing_statement_email(user, bill_doc)
        billing_records_collection.update_one(
            {"_id": result.inserted_id},
            {
                "$set": {
                    "emailSent": email_sent,
                    "emailSentAt": datetime.utcnow() if email_sent else None,
                    "emailError": email_error,
                }
            },
        )
        bill_doc["emailSent"] = email_sent
        bill_doc["emailSentAt"] = datetime.utcnow() if email_sent else None
        bill_doc["emailError"] = email_error
        return bill_doc
    
    # Get plan details
    plan_name = user.get("plan", "")
    if not plan_name:
        # For users with no plan, we can use a free tier logic or return empty
        return None
    plan = plans_collection.find_one({"name": plan_name.capitalize()})
    if not plan:
        return None
    
    # Calculate billing period (current month)
    now = datetime.utcnow()
    period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Get last day of current month
    if now.month == 12:
        period_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        period_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    units_used = user.get("units", 0)
    max_units = user.get("maxUnits", 200)
    overage_units = max(0, units_used - max_units)
    
    # Use plan's overageRate if available
    overage_rate = plan.get("overageRate", 0.19)
    overage_charge = calculate_overage_charge(units_used, max_units, overage_rate=overage_rate)
    
    base_price = plan["price"]
    total_amount = base_price + overage_charge
    
    bill_doc = {
        "userId": user_id,
        "billingPeriodStart": period_start,
        "billingPeriodEnd": period_end,
        "plan": plan_name,
        "basePrice": base_price,
        "includedUnits": max_units,
        "unitsUsed": units_used,
        "overageUnits": overage_units,
        "overageCharge": overage_charge,
        "totalAmount": total_amount,
        "generatedAt": datetime.utcnow(),
        "status": "pending"
    }
    
    result = billing_records_collection.insert_one(bill_doc)
    bill_doc["_id"] = result.inserted_id
    billing_records_collection.update_one(
        {"_id": result.inserted_id},
        {
            "$set": {
                "emailSent": False,
                "emailSentAt": None,
                "emailError": "Not applicable for prepaid billing",
            }
        },
    )
    bill_doc["emailSent"] = False
    bill_doc["emailSentAt"] = None
    bill_doc["emailError"] = "Not applicable for prepaid billing"
    return bill_doc

def get_billing_history(user_id: str, limit: int = 10):
    """Get billing history for a user"""
    bills = list(billing_records_collection.find(
        {"userId": user_id}
    ).sort("billingPeriodStart", -1).limit(limit))
    
    return bills

def get_all_plans():
    """Get all active pricing plans"""
    plans = list(plans_collection.find({"isActive": True}))
    return plans
