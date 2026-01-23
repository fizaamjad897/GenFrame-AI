import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

from auth import (
    users_collection, 
    hash_password, 
    generate_api_key_for_user,
    get_user_by_email
)
from models import UserRegister
from bson import ObjectId

load_dotenv()

def setup_client():
    email = "glenn@fmctv.co.nz"
    password = "VisualEngine2026!"
    
    print(f"🚀 Setting up client account for: {email}...")
    
    # 1. Check if user exists, or create
    user = get_user_by_email(email)
    if not user:
        user_doc = {
            "email": email,
            "password": hash_password(password),
            "fullName": "Glenn FMCTV",
            "plan": "Trial",
            "engineType": "transformation",
            "credits": {
                "monthly_units_used": 0.0,
                "monthly_units_max": 20.0,
                "addon_units_used": 0.0,
                "addon_units_max": 0.0,
                "remaining_units": 20.0
            },
            "api_keys": {
                "resize_hash": None,
                "create_hash": None
            },
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
        }
        result = users_collection.insert_one(user_doc)
        user_id = str(result.inserted_id)
        print("✅ User created successfully.")
    else:
        user_id = str(user["_id"])
        # Reset credits for testing
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "credits.monthly_units_max": 20.0,
                "credits.monthly_units_used": 0.0,
                "credits.remaining_units": 20.0,
                "plan": "Trial"
            }}
        )
        print("✅ User existing, credits reset to 20.0.")

    # 2. Generate API Keys
    transformation_key = generate_api_key_for_user(user_id, "resize")
    creation_key = generate_api_key_for_user(user_id, "create")
    
    print("\n" + "="*50)
    print("🔑 CLIENT API CREDENTIALS")
    print("="*50)
    print(f"Email:    {email}")
    print(f"Password: {password}")
    print(f"\nTransformation Engine Key (Resize):")
    print(f"👉 {transformation_key}")
    print(f"\nCreation Engine Key (Prompt + Resize):")
    print(f"👉 {creation_key}")
    print("="*50)
    print("\n⚠️ IMPORTANT: Copy these keys now! For security, the raw keys are NOT stored in the database.")

if __name__ == "__main__":
    setup_client()
