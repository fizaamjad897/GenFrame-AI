import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from auth import (
    users_collection, 
    plans_collection,
    hash_password, 
    generate_api_key_for_user,
    get_user_by_email,
    _recompute_remaining_units
)

load_dotenv()

def setup_dual_engine_user(email, password="VisualEngine2026!", plan_name="Scale"):
    print(f"\n🚀 Setting up dual-engine account for: {email}...")
    
    # 1. Check if user exists, or create
    user = get_user_by_email(email)
    if not user:
        user_doc = {
            "email": email,
            "password": hash_password(password),
            "fullName": email.split('@')[0].capitalize(),
            "plan": plan_name,
            "engineType": "transformation",
            "credits": {}, # Will be populated below
            "engine_data": {},
            "api_keys": {
                "resize_hash": None,
                "create_hash": None
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        user = user_doc
        print(f"✅ User {email} created.")
    else:
        user_id = str(user["_id"])
        print(f"✅ User {email} found.")

    # 2. Fetch Plan Data
    plan_doc = plans_collection.find_one({"name": plan_name})
    if not plan_doc:
        print(f"❌ Plan {plan_name} not found in database. Please run seed_plans.py first.")
        return

    included_units = float(plan_doc["includedUnits"])
    overage_rate = float(plan_doc.get("overageRate", 0.12))

    # 3. Setup Engine Data for BOTH engines
    engines = ["transformation", "creation"]
    engine_data = user.get("engine_data", {}) or {}
    
    for engine in engines:
        credits = {
            "monthly_units_used": 0.0,
            "monthly_units_max": included_units,
            "addon_units_used": 0.0,
            "addon_units_max": 0.0,
            "overageRate": overage_rate,
        }
        credits["remaining_units"] = _recompute_remaining_units(credits)
        
        engine_data[engine] = {
            "plan": plan_name,
            "credits": credits,
            "is_pending_cancellation": False,
            "stripeSubscriptionId": f"sub_db_setup_{engine}_{datetime.utcnow().strftime('%Y%m%d')}",
            "updatedAt": datetime.utcnow()
        }

    # 4. Update User Document
    # Use 'transformation' as the default active engine top-level
    active_engine = "transformation"
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "plan": plan_name,
                "engineType": active_engine,
                "credits": engine_data[active_engine]["credits"],
                "engine_data": engine_data,
                "maxUnits": int(included_units),
                "units": 0,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    print(f"✅ Dual-engine subscription ({plan_name}) configured for {email}.")

    # 5. Ensure API Keys exist (scoped)
    api_keys = user.get("api_keys", {}) or {}
    
    if not api_keys.get("resize_hash"):
        try:
            resize_key = generate_api_key_for_user(user_id, "resize")
            print(f"🔑 Transformation Key: {resize_key}")
        except ValueError:
            print("ℹ️ Transformation key already exists.")
            
    if not api_keys.get("create_hash"):
        try:
            create_key = generate_api_key_for_user(user_id, "create")
            print(f"🔑 Creation Key: {create_key}")
        except ValueError:
            print("ℹ️ Creation key already exists.")

    print(f"🏁 Setup complete for {email}")

if __name__ == "__main__":
    emails = ["glenn@fmctv.co.nz", "muhammadhamzafaisal146@gmail.com"]
    for email in emails:
        setup_dual_engine_user(email)
