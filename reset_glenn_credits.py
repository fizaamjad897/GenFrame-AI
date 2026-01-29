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
    get_user_by_email
)

load_dotenv()

def reset_user_credits_to_zero(email):
    print(f"🧹 Resetting credits to zero for: {email}...")
    
    user = get_user_by_email(email)
    if not user:
        print(f"❌ User {email} not found.")
        return

    user_id = str(user["_id"])
    engine_data = user.get("engine_data", {}) or {}
    
    # Reset all engines in engine_data
    for engine in engine_data:
        if "credits" in engine_data[engine]:
            engine_data[engine]["credits"]["monthly_units_used"] = 0.0
            engine_data[engine]["credits"]["monthly_units_max"] = 0.0
            engine_data[engine]["credits"]["addon_units_used"] = 0.0
            engine_data[engine]["credits"]["addon_units_max"] = 0.0
            engine_data[engine]["credits"]["remaining_units"] = 0.0
            engine_data[engine]["updatedAt"] = datetime.utcnow()

    # Update top-level
    top_credits = {
        "monthly_units_used": 0.0,
        "monthly_units_max": 0.0,
        "addon_units_used": 0.0,
        "addon_units_max": 0.0,
        "remaining_units": 0.0,
        "overageRate": user.get("credits", {}).get("overageRate", 0.19)
    }

    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {
            "$set": {
                "credits": top_credits,
                "engine_data": engine_data,
                "maxUnits": 0,
                "units": 0,
                "updatedAt": datetime.utcnow()
            }
        }
    )
    print(f"✅ All credits for {email} have been reset to 0.")

if __name__ == "__main__":
    reset_user_credits_to_zero("glenn@fmctv.co.nz")
