import os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()
MONGODB_URL = os.getenv("MONGODB_URL")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure")

def setup_client_account():
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    users_collection = db["users"]

    email = "glenn@fmctv.co.nz"
    full_name = "Glenn Tong"
    # Secure random password if needed, but here we set a specific one for testing
    password = "VisualEngine2026!"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    client_data = {
        "email": email,
        "fullName": full_name,
        "password": hashed_password,
        "plan": "Free Tier",
        "units": 0,
        "maxUnits": 50,
        "updatedAt": datetime.utcnow()
    }

    # Check if user exists
    existing_user = users_collection.find_one({"email": email})
    
    if existing_user:
        # Update existing user
        users_collection.update_one(
            {"email": email},
            {"$set": client_data}
        )
        print(f"✅ Updated existing client account: {email}")
    else:
        # Create new user
        client_data["createdAt"] = datetime.utcnow()
        users_collection.insert_one(client_data)
        print(f"✅ Created new client account: {email}")

    print(f"\nCredentials for {full_name}:")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print(f"Credits: 50")

if __name__ == "__main__":
    setup_client_account()
