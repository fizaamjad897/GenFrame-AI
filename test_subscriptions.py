#!/usr/bin/env python3
"""
Quick start testing script for subscription features.
Displays test user tokens and endpoints for manual testing.
"""

import os
from dotenv import load_dotenv
from auth import users_collection, create_access_token
from datetime import datetime

load_dotenv()

def test_subscription_flow():
    """Display test credentials and endpoints"""
    
    print("\n" + "="*70)
    print("🧪 SUBSCRIPTION TESTING QUICK START")
    print("="*70 + "\n")
    
    # Get test users
    users = list(users_collection.find({}).limit(3))
    
    if not users:
        print("❌ No users found in database. Create a test user first!")
        return
    
    print("📋 TEST USERS:\n")
    
    for i, user in enumerate(users, 1):
        user_id = str(user["_id"])
        email = user.get("email", "unknown")
        plan = user.get("plan", "—")
        engine_type = user.get("engineType", "—")
        sub_id = user.get("stripeSubscriptionId", "—")
        
        # Generate token for this user
        token = create_access_token(user_id)
        
        print(f"{i}. {email}")
        print(f"   ID: {user_id}")
        print(f"   Plan: {plan}")
        print(f"   Engine: {engine_type}")
        print(f"   Subscription: {sub_id if sub_id != '—' else '❌ Not set'}")
        print(f"   Token: {token[:50]}...")
        print()
    
    print("="*70)
    print("🔗 API ENDPOINTS (localhost:8000)\n")
    
    print("1️⃣  GET CURRENT USER")
    print("   GET /api/users/me")
    print("   Header: Authorization: Bearer {token}")
    print()
    
    print("2️⃣  CREATE CHECKOUT SESSION")
    print("   POST /api/stripe/create-checkout")
    print("   Header: Authorization: Bearer {token}")
    print("""   Body: {
      "plan_code": "Starter",
      "engine_type": "transformation",
      "order_type": "subscription"
    }""")
    print()
    
    print("3️⃣  CANCEL SUBSCRIPTION")
    print("   POST /api/stripe/cancel-subscription")
    print("   Header: Authorization: Bearer {token}")
    print("""   Body: {
      "at_period_end": false,
      "engine_type": "transformation"
    }""")
    print()
    
    print("4️⃣  BUY ADDON CREDITS")
    print("   POST /api/stripe/create-checkout")
    print("   Header: Authorization: Bearer {token}")
    print("""   Body: {
      "plan_code": "ADDON_100",
      "engine_type": "transformation",
      "order_type": "addon"
    }""")
    print()
    
    print("="*70)
    print("💳 STRIPE TEST CARDS\n")
    print("Success:  4242 4242 4242 4242")
    print("Decline:  4000 0000 0000 0002")
    print("Expiry:   Any future date (e.g., 12/25)")
    print("CVC:      Any 3 digits (e.g., 123)")
    print()
    
    print("="*70)
    print("📝 TESTING CHECKLIST\n")
    
    print("✓ Test 1: Create first subscription")
    print("  - Select Transformation engine")
    print("  - Click Upgrade → Starter plan")
    print("  - Pay with test card")
    print("  - Verify webhook: checkout.session.completed")
    print()
    
    print("✓ Test 2: View subscription")
    print("  - Check 'Current Plan' shows Starter")
    print("  - Monthly credits: 0 / 1000")
    print("  - Buttons: Open Billing Portal, Cancel Now")
    print()
    
    print("✓ Test 3: Try to switch without cancelling")
    print("  - Click Growth plan")
    print("  - Button should be DISABLED")
    print("  - Alert: Cancel current plan to switch")
    print()
    
    print("✓ Test 4: Cancel subscription")
    print("  - Click 'Cancel Now'")
    print("  - Confirm cancellation")
    print("  - Verify: Plan resets, Monthly credits → 0 / 0")
    print("  - Addon credits remain unchanged")
    print()
    
    print("✓ Test 5: Switch engines and plans")
    print("  - Switch to Creation engine")
    print("  - Buy different plan (e.g., Growth)")
    print("  - Verify both plans active simultaneously")
    print()
    
    print("✓ Test 6: Buy addon credits")
    print("  - No active subscription needed")
    print("  - Click Buy Now ($20 for 100 credits)")
    print("  - Verify addon credits increase, never expire")
    print()
    
    print("="*70)
    print("🔍 VERIFICATION COMMANDS\n")
    
    print("Check all subscriptions:")
    print("  python verify_subscriptions.py")
    print()
    
    print("Fix invalid subscriptions:")
    print("  python fix_subscriptions.py --apply")
    print()
    
    print("Seed plans (if needed):")
    print("  python seed_plans.py")
    print()
    
    print("="*70 + "\n")

if __name__ == "__main__":
    test_subscription_flow()
