from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine").strip("'\" ")

def reset_test_user():
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    users_collection = db["users"]
    
    # We'll update ALL users to 200 units and reset plan to empty
    result = users_collection.update_many(
        {},
        {"$set": {"maxUnits": 200, "units": 0, "plan": ""}}
    )
    
    print(f"✅ Reset {result.modified_count} users to 200 units, 0 usage, and No Plan.")
    
    # Also ensure the Starter plan in 'plans' collection is correct
    plans_collection = db["plans"]
    plans_collection.update_one(
        {"name": "Starter"},
        {"$set": {"includedUnits": 200}}
    )
    print("✅ Updated 'Starter' plan to 200 units in database.")

if __name__ == "__main__":
    reset_test_user()
