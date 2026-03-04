import os
from auth import users_collection, hash_password
from dotenv import load_dotenv

load_dotenv()

def update_glenn_password():
    email = "glenn@fmctv.co.nz"
    new_password = "Password@123"
    
    print(f"🔄 Updating password for {email}...")
    
    user = users_collection.find_one({"email": email})
    if not user:
        print(f"❌ User {email} not found.")
        return

    hashed_psw = hash_password(new_password)
    
    result = users_collection.update_one(
        {"email": email},
        {"$set": {"password": hashed_psw}}
    )
    
    if result.modified_count > 0:
        print(f"✅ Password for {email} has been updated to '{new_password}'.")
    else:
        print(f"⚠️ Password was not updated (possibly already set to this value).")

if __name__ == "__main__":
    update_glenn_password()
