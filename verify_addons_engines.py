import os
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure").strip("'\" ")

def verify_addons_and_engines():
    print("🚀 Starting Extended Verification...")
    
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    users_collection = db["users"]
    
    # 1. Find a test user (or just use the first one)
    user = users_collection.find_one({})
    if not user:
        print("❌ No users found in database. Run registration first.")
        return
    
    user_id = str(user["_id"])
    print(f"👤 Testing with User: {user['email']} (ID: {user_id})")
    print(f"   Current Engine: {user.get('engineType', 'NOT SET')}")
    print(f"   Addon Max: {user.get('credits', {}).get('addon_units_max', 0)}")

    # 2. Test Addon Increment logic (Internal call test)
    from auth import add_addon_credits, update_user_engine
    
    print("\n🛠️ Testing Internal Logic...")
    
    # Test adding addon units
    initial_addon_max = user.get('credits', {}).get('addon_units_max', 0.0)
    add_addon_credits(user_id, 50.0)
    
    updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
    new_addon_max = updated_user.get('credits', {}).get('addon_units_max', 0.0)
    
    if new_addon_max == initial_addon_max + 50.0:
        print(f"✅ Add-on Max updated correctly: {initial_addon_max} -> {new_addon_max}")
    else:
        print(f"❌ Add-on Max mismatch: expected {initial_addon_max + 50.0}, got {new_addon_max}")

    # Test engine update
    update_user_engine(user_id, "creation")
    updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
    if updated_user.get("engineType") == "creation":
        print("✅ Engine Type updated correctly to 'creation'")
    else:
        print(f"❌ Engine Type mismatch: expected 'creation', got {updated_user.get('engineType')}")

    print("\n✨ Extended Verification Completed!")

if __name__ == "__main__":
    verify_addons_and_engines()
