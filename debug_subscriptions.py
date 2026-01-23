#!/usr/bin/env python3
"""
Debug subscription flow - identify why subscription IDs aren't being saved
"""

import os
import sys
from dotenv import load_dotenv
import stripe
from bson import ObjectId
from auth import users_collection, create_access_token
from datetime import datetime

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def debug_user_subscription(email: str):
    """Deep dive into a user's subscription state"""
    
    print("\n" + "="*80)
    print(f"🔍 DEBUGGING SUBSCRIPTION FOR: {email}")
    print("="*80 + "\n")
    
    # 1. Find user in database
    user = users_collection.find_one({"email": email})
    
    if not user:
        print(f"❌ User not found in database: {email}")
        return
    
    user_id = str(user["_id"])
    print(f"✓ User found: {user_id}\n")
    
    # 2. Check what's stored in database
    print("📊 DATABASE STATE:")
    print(f"  Email: {email}")
    print(f"  Plan: {user.get('plan', '—')}")
    print(f"  Engine Type: {user.get('engineType', '—')}")
    print(f"  Stripe Customer ID: {user.get('stripeCustomerId', '—')}")
    print(f"  Stripe Subscription ID: {user.get('stripeSubscriptionId', '—')}")
    print()
    
    # 3. Check Stripe customer
    stripe_customer_id = user.get("stripeCustomerId")
    if not stripe_customer_id:
        print("⚠️  No Stripe Customer ID in database")
        print("  This means user hasn't created a checkout session yet\n")
        return
    
    print(f"✓ Stripe Customer ID found: {stripe_customer_id}\n")
    
    # 4. Get customer from Stripe
    try:
        customer = stripe.Customer.retrieve(stripe_customer_id)
        print(f"✓ Customer found in Stripe")
        print(f"  Name: {customer.get('name', 'N/A')}")
        print(f"  Email: {customer.email}")
        print()
    except stripe.error.InvalidRequestError as e:
        print(f"❌ Customer not found in Stripe: {e}")
        return
    
    # 5. Get all subscriptions for this customer
    try:
        subs_list = stripe.Subscription.list(customer=stripe_customer_id, limit=10)
        subscriptions_data = list(subs_list)
        
        if not subscriptions_data:
            print("⚠️  NO SUBSCRIPTIONS found for this customer in Stripe!")
            print("  This explains why cancel fails.\n")
            print("🔧 WHAT TO DO:")
            print("  1. Go to http://localhost:3000/billing")
            print("  2. Click 'Upgrade' on any plan")
            print("  3. Complete payment with: 4242 4242 4242 4242")
            print("  4. Run this script again\n")
            return
        
        print(f"✓ Found {len(subscriptions_data)} subscription(s) in Stripe:\n")
        
        for i, sub in enumerate(subscriptions_data, 1):
            print(f"  Subscription #{i}:")
            print(f"    ID: {sub.id}")
            print(f"    Status: {sub.status}")
            plan_name = "N/A"
            try:
                if hasattr(sub, 'items') and sub.items:
                    items_list = list(sub.items)
                    if items_list:
                        price = items_list[0].price
                        plan_name = price.nickname or price.id
            except:
                pass
            print(f"    Plan: {plan_name}")
            try:
                period_start = datetime.fromtimestamp(sub.current_period_start).strftime('%Y-%m-%d')
                period_end = datetime.fromtimestamp(sub.current_period_end).strftime('%Y-%m-%d')
                print(f"    Current Period: {period_start} → {period_end}")
            except:
                pass
            print()
        
        # 6. Compare stored vs actual
        stored_sub_id = user.get("stripeSubscriptionId")
        actual_sub_id = subscriptions_data[0].id if subscriptions_data else None
        
        if stored_sub_id and actual_sub_id:
            if stored_sub_id == actual_sub_id:
                print("✅ STORED ID MATCHES STRIPE!")
                print(f"   {stored_sub_id}\n")
            else:
                print("⚠️  MISMATCH!")
                print(f"  Stored: {stored_sub_id}")
                print(f"  Stripe: {actual_sub_id}")
                print("\n🔧 FIX: Update database with correct ID?")
                fix_response = input("  Type 'fix' to update database: ")
                if fix_response.lower() == 'fix':
                    users_collection.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$set": {"stripeSubscriptionId": actual_sub_id}}
                    )
                    print(f"  ✓ Updated database with: {actual_sub_id}\n")
        elif stored_sub_id:
            print(f"⚠️  STORED ID NOT IN STRIPE!")
            print(f"  Stored: {stored_sub_id}")
            print(f"  Stripe has: {actual_sub_id}")
            print("\n🔧 FIX: Update database with correct ID?")
            fix_response = input("  Type 'fix' to update database: ")
            if fix_response.lower() == 'fix':
                users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"stripeSubscriptionId": actual_sub_id}}
                )
                print(f"  ✓ Updated database with: {actual_sub_id}\n")
        else:
            print(f"⚠️  NO STORED ID IN DATABASE!")
            print(f"  Stripe has: {actual_sub_id}")
            print("\n🔧 FIX: Update database with correct ID?")
            fix_response = input("  Type 'fix' to update database: ")
            if fix_response.lower() == 'fix':
                users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"stripeSubscriptionId": actual_sub_id}}
                )
                print(f"  ✓ Updated database with: {actual_sub_id}\n")
    
    except Exception as e:
        print(f"❌ Error fetching subscriptions: {e}\n")
        return
    
    # 7. Test cancellation
    print("="*80)
    print("🧪 TEST CANCELLATION\n")
    
    token = create_access_token(user_id)
    print(f"User Token: {token[:50]}...\n")
    
    if actual_sub_id:
        print(f"Ready to test cancel with subscription: {actual_sub_id}")
        print("\nYou can now:")
        print(f"  1. Go to http://localhost:3000/billing")
        print(f"  2. Click 'Cancel Now'")
        print(f"  3. Or use curl:")
        print(f"\n     curl -X POST http://localhost:8000/api/stripe/cancel-subscription \\")
        print(f"       -H 'Authorization: Bearer {token}' \\")
        print(f"       -H 'Content-Type: application/json' \\")
        print(f"       -d '{{\"at_period_end\": false}}'")
    
    print("\n" + "="*80 + "\n")

def show_all_subscriptions():
    """Show all subscriptions across all users"""
    
    print("\n" + "="*80)
    print("📊 ALL USERS & SUBSCRIPTIONS")
    print("="*80 + "\n")
    
    users = list(users_collection.find({}))
    
    for user in users:
        email = user.get("email", "unknown")
        plan = user.get("plan") or "—"
        sub_id = user.get("stripeSubscriptionId") or "—"
        
        # Verify subscription exists in Stripe
        status = "?"
        if sub_id and sub_id != "—":
            try:
                sub = stripe.Subscription.retrieve(sub_id)
                status = f"✅ {sub.status}"
            except:
                status = "❌ NOT FOUND"
        
        print(f"  {email:<30} | Plan: {str(plan):<10} | Sub: {str(sub_id):<20} | {status}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        debug_user_subscription(email)
    else:
        print("Usage: python debug_subscriptions.py <email>")
        print("\nExample:")
        print("  python debug_subscriptions.py user@example.com\n")
        print("Or view all users:")
        show_all_subscriptions()
