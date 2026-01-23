import json
import os
import requests
from bson import ObjectId
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Simulation settings
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017").strip("'\" ")
DB_NAME = os.getenv("DB_NAME", "visual_engine_secure").strip("'\" ")
API_URL = "http://localhost:8000/api/stripe/webhook"

def test_webhook_logic():
    print("🚀 Starting Stripe Webhook Logic Test...")
    
    # 1. Setup Mongo
    client = MongoClient(MONGODB_URL)
    db = client[DB_NAME]
    users = db["users"]
    
    # 2. Find a test user or create one
    test_email = "stripe_tester@example.com"
    users.delete_one({"email": test_email})
    user_id = users.insert_one({
        "email": test_email,
        "plan": "",
        "credits": {
            "monthly_units_used": 0.0,
            "monthly_units_max": 0.0,
            "addon_units_used": 0.0,
            "addon_units_max": 0.0,
            "remaining_units": 0.0
        },
        "stripeCustomerId": "cus_test_123"
    }).inserted_id

    print(f"Created test user: {user_id}")

    # 3. Simulate checkout.session.completed (SUBSCRIPTION)
    print("\nTest 1: checkout.session.completed (Subscription: Starter)")
    from stripe_manager import handle_webhook_event
    
    # We bypass the actual HTTP call to avoid signature verification issues in testing
    # Instead, we test the manager logic directly or mock the event
    
    class MockEvent:
        def __getitem__(self, key):
            if key == "type": return "checkout.session.completed"
            return None
        def get(self, key, default=None):
            return self[key] or default
            
    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_1",
                "customer": "cus_test_123",
                "subscription": "sub_test_1",
                "metadata": {
                    "user_id": str(user_id),
                    "plan_code": "Starter",
                    "engine_type": "creation",
                    "order_type": "subscription"
                }
            }
        }
    }
    
    # We'll use a trick: Mock stripe.Webhook.construct_event
    import stripe
    original_construct = stripe.Webhook.construct_event
    stripe.Webhook.construct_event = lambda p, s, secret: payload
    
    from stripe_manager import handle_webhook_event
    handle_webhook_event(json.dumps(payload), "mock_sig")
    
    # Verify User
    updated_user = users.find_one({"_id": user_id})
    print(f"Plan after sub: {updated_user['plan']}")
    print(f"Engine after sub: {updated_user['engineType']}")
    print(f"Credits after sub: {updated_user['credits']['monthly_units_max']}")
    
    # 4. Simulate checkout.session.completed (ADDON)
    print("\nTest 2: checkout.session.completed (Addon: ADDON_100)")
    payload["data"]["object"]["metadata"]["order_type"] = "addon"
    payload["data"]["object"]["metadata"]["plan_code"] = "ADDON_100"
    
    handle_webhook_event(json.dumps(payload), "mock_sig")
    updated_user = users.find_one({"_id": user_id})
    print(f"Addon Max after addon: {updated_user['credits']['addon_units_max']}")
    print(f"Total Remaining: {updated_user['credits']['remaining_units']}")

    # 5. Simulate Renewal (Must happen while plan is active)
    print("\nTest 3: invoice.paid")
    users.update_one({"_id": user_id}, {"$set": {"credits.monthly_units_used": 10.0}})
    
    payload = {
        "type": "invoice.paid",
        "data": {
            "object": {
                "customer": "cus_test_123"
            }
        }
    }
    stripe.Webhook.construct_event = lambda p, s, secret: payload
    handle_webhook_event(json.dumps(payload), "mock_sig")
    
    updated_user = users.find_one({"_id": user_id})
    print(f"Monthly units used after renewal: {updated_user['credits']['monthly_units_used']}")

    # 6. Simulate Cancellation
    print("\nTest 4: customer.subscription.deleted")
    payload = {
        "type": "customer.subscription.deleted",
        "data": {
            "object": {
                "customer": "cus_test_123"
            }
        }
    }
    stripe.Webhook.construct_event = lambda p, s, secret: payload
    handle_webhook_event(json.dumps(payload), "mock_sig")
    
    updated_user = users.find_one({"_id": user_id})
    print(f"Plan after cancel: '{updated_user['plan']}'")
    print(f"Monthly Max after cancel: {updated_user['credits']['monthly_units_max']}")

    # Cleanup
    # users.delete_one({"email": test_email})
    stripe.Webhook.construct_event = original_construct
    print("\n✨ Verification complete!")

if __name__ == "__main__":
    test_webhook_logic()
