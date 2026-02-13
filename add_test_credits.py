import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

load_dotenv()

# MongoDB setup
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure").strip("'\" ")

def add_test_credits(email, amount=500, plan="Starter", engine="transformation"):
    print(f"🚀 Adding {amount} test credits to {email} ({engine} engine)...")
    
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    users_collection = db["users"]
    
    user = users_collection.find_one({"email": email})
    if not user:
        print(f"❌ User {email} not found.")
        return

    user_id = user["_id"]
    engine_data = user.get("engine_data", {}) or {}
    
    # Mock credits structure
    new_credits = {
        "monthly_units_used": 0.0,
        "monthly_units_max": float(amount),
        "addon_units_used": 0.0,
        "addon_units_max": 0.0,
        "remaining_units": float(amount),
        "overageRate": 0.19,
        "is_pending_cancellation": False
    }
    
    # Update specific engine
    engine_data[engine] = {
        "plan": plan,
        "credits": new_credits,
        "stripeSubscriptionId": "sub_test_manual_" + str(ObjectId()), # Mock sub ID for UI
        "is_pending_cancellation": False,
        "updatedAt": datetime.utcnow()
    }
    
    # Update user document
    users_collection.update_one(
        {"_id": user_id},
        {
            "$set": {
                "plan": plan,
                "engineType": engine,
                "credits": new_credits,
                "engine_data": engine_data,
                "remainingUnits": float(amount),
                "maxUnits": int(amount),
                "stripeSubscriptionId": engine_data[engine]["stripeSubscriptionId"],
                "updatedAt": datetime.utcnow()
            }
        }
    )
    
    print(f"✅ Credits and plan '{plan}' assigned to {email}.")
    print(f"ℹ️  Mock Subscription ID: {engine_data[engine]['stripeSubscriptionId']}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_test_credits.py <email>")
    else:
        add_test_credits(sys.argv[1])
