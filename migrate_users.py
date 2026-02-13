from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine").strip("'\" ")

def migrate_users():
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    users_collection = db["users"]
    
    users = list(users_collection.find())
    print(f"🔍 Found {len(users)} users to check for migration.")
    
    migrated_count = 0
    for user in users:
        user_id = user["_id"]
        email = user.get("email")
        engine_data = user.get("engine_data", {})
        
        # We want to ensure both 'transformation' and 'creation' exist
        needs_update = False
        
        # Current system state
        current_credits = user.get("credits", {})
        current_plan = user.get("plan", "")
        current_engine_type = user.get("engineType", "transformation")
        is_pending_cancellation = user.get("is_pending_cancellation", False)
        stripe_sub_id = user.get("stripeSubscriptionId")
        
        updated_engine_data = engine_data.copy()
        
        for etype in ["transformation", "creation"]:
            if etype not in updated_engine_data:
                # Initialize missing engine
                if etype == current_engine_type:
                    # This engine already has data (in top-level credits), migrate it
                    updated_engine_data[etype] = {
                        "plan": current_plan,
                        "credits": current_credits,
                        "is_pending_cancellation": is_pending_cancellation,
                        "stripeSubscriptionId": stripe_sub_id,
                        "updatedAt": datetime.utcnow()
                    }
                else:
                    # New engine, initialize with 0
                    updated_engine_data[etype] = {
                        "plan": "",
                        "credits": {
                            "monthly_units_used": 0.0,
                            "monthly_units_max": 0.0,
                            "addon_units_used": 0.0,
                            "addon_units_max": 0.0,
                            "remaining_units": 0.0,
                            "overageRate": 0.19
                        },
                        "is_pending_cancellation": False,
                        "stripeSubscriptionId": None,
                        "updatedAt": datetime.utcnow()
                    }
                needs_update = True
        
        if needs_update:
            users_collection.update_one(
                {"_id": user_id},
                {"$set": {"engine_data": updated_engine_data, "updatedAt": datetime.utcnow()}}
            )
            migrated_count += 1
            print(f"✅ Migrated user: {email}")
            
    print(f"🏁 Migration complete. {migrated_count} users updated.")

if __name__ == "__main__":
    migrate_users()
