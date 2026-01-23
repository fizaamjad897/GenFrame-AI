import os
import stripe
from dotenv import load_dotenv
from auth import users_collection, add_addon_credits
from bson import ObjectId
import requests

load_dotenv()

# We need a real user ID from the DB to test
def test_addon_sync():
    print("Starting Add-on Sync Test...")
    
    # 1. Find a test user
    user = users_collection.find_one({"email": "fizaamjad888@gmail.com"})
    if not user:
        user = users_collection.find_one({})
        
    if not user:
        print("No users found in database.")
        return
        
    user_id = str(user["_id"])
    email = user["email"]
    print(f"Testing with User: {email} (ID: {user_id})")
    
    # Current state
    initial_credits = user.get("credits", {})
    initial_addon_max = initial_credits.get("addon_units_max", 0.0)
    print(f"Initial Add-on Max: {initial_addon_max}")
    
    # 2. Simulate the manual-sync call
    print("Testing Credits Addition...")
    add_addon_credits(user_id, 100.0)
    
    updated_user = users_collection.find_one({"_id": ObjectId(user_id)})
    new_credits = updated_user.get("credits", {})
    new_addon_max = new_credits.get("addon_units_max", 0.0)
    remaining = new_credits.get("remaining_units", 0.0)
    
    print(f"New Add-on Max: {new_addon_max}")
    print(f"New Remaining: {remaining}")
    
    if new_addon_max == initial_addon_max + 100.0:
        print("SUCCESS: Credits stacked correctly!")
    else:
        print("FAILURE: Credits did not stack.")
        
    # Check plan didn't change (using top-level plan)
    initial_plan = user.get("plan", "")
    updated_plan = updated_user.get("plan", "")
    if updated_plan == initial_plan:
        print(f"SUCCESS: Plan remained '{initial_plan}'")
    else:
        print(f"FAILURE: Plan changed from '{initial_plan}' to '{updated_plan}'")

if __name__ == "__main__":
    test_addon_sync()
