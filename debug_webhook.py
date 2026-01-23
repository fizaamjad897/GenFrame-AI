"""
Debug script to check webhook processing and manually sync subscription
Run this from the Visual-Engine-BE directory
"""
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import stripe

load_dotenv()

# Initialize
MONGODB_URL = os.getenv("MONGODB_URL", "").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure").strip("'\" ")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
db = client[DB_NAME]
users_collection = db["users"]
stripe_events_collection = db["stripe_events"]
plans_collection = db["plans"]

def check_user_account(email):
    """Check user account status"""
    print(f"\n🔍 Checking account for: {email}")
    user = users_collection.find_one({"email": email})
    
    if not user:
        print(f"❌ User not found: {email}")
        return None
    
    print(f"\n📋 User Account Status:")
    print(f"  User ID: {user['_id']}")
    print(f"  Email: {user['email']}")
    print(f"  Plan: {user.get('plan', 'None')}")
    print(f"  Engine Type: {user.get('engineType', 'None')}")
    print(f"  Stripe Customer ID: {user.get('stripeCustomerId', 'None')}")
    print(f"  Stripe Subscription ID: {user.get('stripeSubscriptionId', 'None')}")
    
    credits = user.get('credits', {})
    print(f"\n💰 Credits:")
    print(f"  Monthly Max: {credits.get('monthly_units_max', 0)}")
    print(f"  Monthly Used: {credits.get('monthly_units_used', 0)}")
    print(f"  Addon Max: {credits.get('addon_units_max', 0)}")
    print(f"  Addon Used: {credits.get('addon_units_used', 0)}")
    print(f"  Remaining: {credits.get('remaining_units', 0)}")
    
    return user

def check_stripe_customer(customer_id):
    """Check Stripe customer and subscriptions"""
    if not customer_id:
        print("\n⚠️  No Stripe customer ID found")
        return None
    
    print(f"\n🔍 Checking Stripe customer: {customer_id}")
    
    try:
        customer = stripe.Customer.retrieve(customer_id)
        print(f"✅ Customer found: {customer.email}")
        
        # Get subscriptions
        subscriptions = stripe.Subscription.list(customer=customer_id, limit=10)
        
        print(f"\n📋 Subscriptions ({len(subscriptions.data)}):")
        for sub in subscriptions.data:
            print(f"\n  Subscription ID: {sub.id}")
            print(f"  Status: {sub.status}")
            print(f"  Created: {sub.created}")
            
            if sub.items.data:
                for item in sub.items.data:
                    price = item.price
                    print(f"  Price ID: {price.id}")
                    print(f"  Amount: ${price.unit_amount / 100}")
            
            metadata = sub.get('metadata', {})
            print(f"  Metadata: {metadata}")
        
        return subscriptions.data
    except Exception as e:
        print(f"❌ Error checking Stripe: {e}")
        return None

def check_webhook_events(user_id):
    """Check processed webhook events"""
    print(f"\n🔍 Checking webhook events for user: {user_id}")
    
    events = list(stripe_events_collection.find().sort("created", -1).limit(10))
    
    print(f"\n📋 Recent Webhook Events ({len(events)}):")
    for event in events:
        print(f"\n  Event ID: {event.get('event_id')}")
        print(f"  Type: {event.get('type')}")
        print(f"  Processed At: {event.get('processedAt')}")
        print(f"  Status: {event.get('status')}")

def manually_sync_subscription(user_id, subscription_id, plan_code="Growth", engine_type="transformation"):
    """Manually sync subscription to user account"""
    print(f"\n🔄 Manually syncing subscription...")
    print(f"  User ID: {user_id}")
    print(f"  Subscription ID: {subscription_id}")
    print(f"  Plan: {plan_code}")
    print(f"  Engine: {engine_type}")
    
    # Get plan details
    plan_doc = plans_collection.find_one({"name": plan_code.capitalize()})
    if not plan_doc:
        print(f"❌ Plan not found: {plan_code}")
        return False
    
    included_units = float(plan_doc.get("includedUnits", 0))
    print(f"  Included Units: {included_units}")
    
    # Update user
    from datetime import datetime
    
    new_credits = {
        "monthly_units_used": 0.0,
        "monthly_units_max": included_units,
        "addon_units_used": 0.0,
        "addon_units_max": 0.0,
        "remaining_units": included_units
    }
    
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "plan": plan_code.capitalize(),
            "engineType": engine_type,
            "credits": new_credits,
            "maxUnits": int(included_units),
            "units": 0,
            "stripeSubscriptionId": subscription_id,
            "updatedAt": datetime.utcnow()
        }}
    )
    
    if result.modified_count > 0:
        print(f"✅ User account updated successfully!")
        return True
    else:
        print(f"⚠️  No changes made (user may already be updated)")
        return False

if __name__ == "__main__":
    # Replace with your test account email
    EMAIL = input("Enter your test account email: ")
    
    # Check user account
    user = check_user_account(EMAIL)
    
    if user:
        # Check Stripe customer
        customer_id = user.get('stripeCustomerId')
        subscriptions = check_stripe_customer(customer_id)
        
        # Check webhook events
        check_webhook_events(str(user['_id']))
        
        # If subscription exists but not synced, offer to manually sync
        if subscriptions and len(subscriptions) > 0:
            active_sub = None
            for sub in subscriptions:
                if sub.status in ['active', 'trialing']:
                    active_sub = sub
                    break
            
            if active_sub and not user.get('plan'):
                print(f"\n⚠️  Found active subscription but user has no plan!")
                sync = input(f"\nSync subscription {active_sub.id}? (yes/no): ")
                
                if sync.lower() == 'yes':
                    # Try to get plan from metadata or price
                    plan_code = "Growth"  # Default
                    engine_type = "transformation"  # Default
                    
                    manually_sync_subscription(
                        str(user['_id']),
                        active_sub.id,
                        plan_code,
                        engine_type
                    )
                    
                    # Verify
                    print("\n✅ Verification:")
                    check_user_account(EMAIL)
    
    client.close()
