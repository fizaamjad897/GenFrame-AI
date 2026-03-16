"""Find ALL user records for muhammadhamzafaisal146@gmail.com and update the one with id 695b9559653f91c8b27b6dd8"""
from dotenv import load_dotenv
load_dotenv()
import os
from pymongo import MongoClient
from datetime import datetime

MONGODB_URL = os.getenv("MONGODB_URL", "").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure").strip("'\" ")

print(f"Connecting to {DB_NAME}...")
client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=10000)
db = client[DB_NAME]
users = db["users"]

email = "muhammadhamzafaisal146@gmail.com"

# Find ALL users with this email
all_users = list(users.find({"email": email}))
print(f"\nFound {len(all_users)} user(s) with email {email}:")
for u in all_users:
    print(f"  ID: {u['_id']}")
    print(f"    plan: {u.get('plan')}")
    print(f"    maxUnits: {u.get('maxUnits')}")
    print(f"    units: {u.get('units')}")
    print(f"    engine_data keys: {list((u.get('engine_data') or {}).keys())}")
    print()

# Now specifically update the one the frontend is using
from bson import ObjectId
target_id = "695b9559653f91c8b27b6dd8"
target_user = users.find_one({"_id": ObjectId(target_id)})

if not target_user:
    print(f"User with ID {target_id} NOT FOUND - trying all DBs...")
    # Try the other database
    other_db = client["visual_engine"]
    other_users = other_db["users"]
    target_user = other_users.find_one({"_id": ObjectId(target_id)})
    if target_user:
        print(f"Found in 'visual_engine' database!")
        users = other_users  # switch to this collection
    else:
        print("Not found in any database!")
        exit(1)

print(f"Target user found: {target_user['email']}")
print(f"  plan: {target_user.get('plan')}")
print(f"  maxUnits: {target_user.get('maxUnits')}")

# Grant 500 credits for BOTH engines
CREDITS = 500.0
new_credits = {
    "monthly_units_used": 0.0,
    "monthly_units_max": CREDITS,
    "addon_units_used": 0.0,
    "addon_units_max": 0.0,
    "remaining_units": CREDITS,
    "overageRate": 0.19,
}

engine_data = target_user.get("engine_data", {}) or {}
for engine in ["transformation", "creation"]:
    engine_data[engine] = {
        "plan": "Scale",
        "credits": dict(new_credits),
        "is_pending_cancellation": False,
        "stripeSubscriptionId": None,
        "updatedAt": datetime.utcnow()
    }

result = users.update_one(
    {"_id": ObjectId(target_id)},
    {"$set": {
        "plan": "Scale",
        "engineType": target_user.get("engineType", "transformation"),
        "credits": dict(new_credits),
        "engine_data": engine_data,
        "maxUnits": int(CREDITS),
        "units": 0,
        "updatedAt": datetime.utcnow()
    }}
)

if result.modified_count > 0:
    print(f"\nSUCCESS! Updated user {target_id}")
    print(f"   Plan: Scale, Credits: {int(CREDITS)} for both engines")
else:
    print(f"\nFAILED to update user {target_id}")

client.close()
