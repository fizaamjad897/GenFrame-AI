from auth import users_collection, _recompute_remaining_units
from bson import ObjectId
import datetime

email = "fizaamjad541@gmail.com"
user = users_collection.find_one({"email": email})
if user:
    user_id = user["_id"]
    engine_data = user.get("engine_data", {})
    
    # 1. Fix Transformation (Remove ADDON plan)
    if "transformation" in engine_data:
        engine_data["transformation"]["plan"] = ""
        # Credits are likely 0 there anyway based on my check
    
    # 2. Add 100 units to Creation addon pool
    if "creation" in engine_data:
        credits = engine_data["creation"].get("credits", {})
        credits["addon_units_max"] = float(credits.get("addon_units_max", 0.0)) + 100.0
        credits["remaining_units"] = _recompute_remaining_units(credits)
        engine_data["creation"]["credits"] = credits
    
    # 3. Handle top-level sync (make creation active)
    active_credits = engine_data.get("creation", {}).get("credits", {})
    
    users_collection.update_one(
        {"_id": user_id},
        {"$set": {
            "engine_data": engine_data,
            "credits": active_credits,
            "maxUnits": int(active_credits.get("monthly_units_max", 0) + active_credits.get("addon_units_max", 0)),
            "plan": engine_data.get("creation", {}).get("plan", ""),
            "updatedAt": datetime.datetime.utcnow()
        }}
    )
    print("✅ User data fixed: 100 addon units added to Creation pool.")
else:
    print("User not found.")
