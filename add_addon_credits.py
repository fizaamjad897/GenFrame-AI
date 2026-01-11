"""
Helper script to add addon credits to a user for testing.
Since addon credits don't reset monthly, this is useful for testing the fallback logic.
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure").strip("'\" ")

def add_addon_credits(user_email: str, resize_credits: int = 0, create_credits: int = 0):
    """Add addon credits to a user"""
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        db = client[DB_NAME]
        users_collection = db["users"]
        
        user = users_collection.find_one({"email": user_email})
        if not user:
            print(f"❌ User {user_email} not found")
            return
            
        # Get current addon credits
        credits = user.get("credits", {})
        current_resize = credits.get("addon_resize_max", 0)
        current_create = credits.get("addon_create_max", 0)
        
        # Add new credits
        new_resize = current_resize + resize_credits
        new_create = current_create + create_credits
        
        result = users_collection.update_one(
            {"email": user_email},
            {
                "$set": {
                    "credits.addon_resize_max": new_resize,
                    "credits.addon_create_max": new_create
                }
            }
        )
        
        if result.modified_count:
            print(f"✅ Added addon credits to {user_email}")
            print(f"   Resize: {current_resize} → {new_resize}")
            print(f"   Create: {current_create} → {new_create}")
        else:
            print(f"⚠️  No changes made")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python add_addon_credits.py <email> [resize_credits] [create_credits]")
        print("Example: python add_addon_credits.py user@example.com 100 50")
        sys.exit(1)
    
    email = sys.argv[1]
    resize = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    create = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    
    add_addon_credits(email, resize, create)
