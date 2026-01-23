"""
Quick fix script to manually sync your subscription
This will check your Stripe account and update your database
"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import stripe
from datetime import datetime

load_dotenv()

# Initialize
MONGODB_URL = os.getenv("MONGODB_URL", "").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure").strip("'\" ")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
users_collection = db["users"]
plans_collection = db["plans"]

def fix_subscription(email):
    """Fix subscription for a user"""
    print(f"\n🔍 Looking up user: {email}")
    user = users_collection.find_one({"email": email})
    
    if not user:
        print(f"❌ User not found: {email}")
        return False
    
    user_id = str(user['_id'])
    customer_id = user.get('stripeCustomerId')
    
    print(f"✅ User found: {user_id}")
    print(f"   Current Plan: {user.get('plan', 'None')}")
    print(f"   Current Credits: {user.get('credits', {}).get('remaining_units', 0)}")
    
    if not customer_id:
        print(f"❌ No Stripe customer ID found")
        return False
    
    print(f"\n🔍 Checking Stripe for customer: {customer_id}")
    
    try:
        # Get active subscriptions
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='active',
            limit=10
        )
        
        if not subscriptions.data:
            print(f"❌ No active subscriptions found in Stripe")
            print(f"   The payment may not have completed successfully")
            return False
        
        # Get the most recent active subscription
        sub = subscriptions.data[0]
        print(f"\n✅ Found active subscription:")
        print(f"   Subscription ID: {sub.id}")
        print(f"   Status: {sub.status}")
        
        # Get price info
        items = sub.get('items', {})
        if items and 'data' in items and len(items['data']) > 0:
            price_id = items['data'][0]['price']['id']
            amount = items['data'][0]['price']['unit_amount'] / 100
            print(f"   Price ID: {price_id}")
            print(f"   Amount: ${amount}")
            
            # Map price ID to plan
            plan_mapping = {
                os.getenv("STRIPE_PRICE_T_STARTER"): ("Starter", 1000),
                os.getenv("STRIPE_PRICE_T_GROWTH"): ("Growth", 3000),
                os.getenv("STRIPE_PRICE_T_SCALE"): ("Scale", 5000),
                os.getenv("STRIPE_PRICE_M_STARTER"): ("Starter", 1000),
                os.getenv("STRIPE_PRICE_M_GROWTH"): ("Growth", 3000),
                os.getenv("STRIPE_PRICE_M_SCALE"): ("Scale", 5000),
            }
            
            plan_info = plan_mapping.get(price_id)
            if not plan_info:
                print(f"⚠️  Unknown price ID, defaulting to Growth plan")
                plan_code = "Growth"
                included_units = 3000
            else:
                plan_code, included_units = plan_info
            
            # Determine engine type from price ID
            engine_type = "creation" if price_id == os.getenv(f"STRIPE_PRICE_M_{plan_code.upper()}") else "transformation"
            
            print(f"\n📝 Updating user account:")
            print(f"   Plan: {plan_code}")
            print(f"   Engine: {engine_type}")
            print(f"   Units: {included_units}")
            
            # Update user account
            new_credits = {
                "monthly_units_used": 0.0,
                "monthly_units_max": float(included_units),
                "addon_units_used": 0.0,
                "addon_units_max": 0.0,
                "remaining_units": float(included_units)
            }
            
            result = users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "plan": plan_code,
                    "engineType": engine_type,
                    "credits": new_credits,
                    "maxUnits": int(included_units),
                    "units": 0,
                    "stripeSubscriptionId": sub.id,
                    "updatedAt": datetime.utcnow()
                }}
            )
            
            if result.modified_count > 0:
                print(f"\n✅ SUCCESS! Account updated:")
                print(f"   Plan: {plan_code}")
                print(f"   Credits: {included_units}")
                print(f"   Subscription ID: {sub.id}")
                print(f"\n🎉 You can now use your account!")
                return True
            else:
                print(f"⚠️  Account may already be up to date")
                return True
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Enter your email address: ")
    
    fix_subscription(email)
