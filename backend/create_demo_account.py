"""
One-off script: create (or refresh the flags on) a demo account that bypasses
pricing/credit gates so the Design Compliance Report feature can be exercised
without a paid plan. Safe to re-run — re-running only refreshes the postpaid/
engine flags on an existing account, it does not reset the password.

Usage: python create_demo_account.py
"""
import secrets
from datetime import datetime

from auth import users_collection, hash_password

DEMO_EMAIL = "demo@genframe.ai"
DEMO_FULL_NAME = "Demo Account"
DEMO_CREDITS_MAX = 100000.0


def _engine_credits(max_units: float) -> dict:
    return {
        "monthly_units_used": 0.0,
        "monthly_units_max": max_units,
        "addon_units_used": 0.0,
        "addon_units_max": 0.0,
        "remaining_units": max_units,
    }


def create_demo_account() -> str:
    existing = users_collection.find_one({"email": DEMO_EMAIL})

    if existing:
        users_collection.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "is_postpaid": True,
                "available_engines": ["transformation", "creation"],
                "engine_data.transformation.plan": "Demo",
                "engine_data.transformation.credits": _engine_credits(DEMO_CREDITS_MAX),
                "engine_data.creation.plan": "Demo",
                "engine_data.creation.credits": _engine_credits(DEMO_CREDITS_MAX),
                "updatedAt": datetime.utcnow(),
            }},
        )
        return "(existing account — password unchanged)"

    password = secrets.token_urlsafe(9)
    users_collection.insert_one({
        "email": DEMO_EMAIL,
        "password": hash_password(password),
        "fullName": DEMO_FULL_NAME,
        "fingerprint": None,
        "presentationId": None,
        "plan": "Demo",
        "engineType": "transformation",
        "units": 0,
        "maxUnits": int(DEMO_CREDITS_MAX),
        "credits": _engine_credits(DEMO_CREDITS_MAX),
        "engine_data": {
            "transformation": {
                "plan": "Demo",
                "credits": _engine_credits(DEMO_CREDITS_MAX),
                "is_pending_cancellation": False,
                "stripeSubscriptionId": None,
                "updatedAt": datetime.utcnow(),
            },
            "creation": {
                "plan": "Demo",
                "credits": _engine_credits(DEMO_CREDITS_MAX),
                "is_pending_cancellation": False,
                "stripeSubscriptionId": None,
                "updatedAt": datetime.utcnow(),
            },
        },
        "api_keys": {"resize_hash": None, "create_hash": None},
        "is_postpaid": True,
        "available_engines": ["transformation", "creation"],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    })
    return password


if __name__ == "__main__":
    result = create_demo_account()
    print(f"Email:    {DEMO_EMAIL}")
    print(f"Password: {result}")
