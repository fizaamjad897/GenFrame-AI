#!/usr/bin/env python3
"""
Verify Stripe subscriptions for all users.
This script checks if stored subscription IDs match actual Stripe subscriptions.
"""

import os
import sys
from dotenv import load_dotenv
import stripe
from bson import ObjectId
from auth import users_collection

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def verify_subscriptions():
    """Check all users' subscriptions against Stripe."""
    
    print("🔍 Verifying Stripe Subscriptions...\n")
    
    users = users_collection.find({})
    total_users = 0
    users_with_subscriptions = 0
    valid_subscriptions = 0
    invalid_subscriptions = 0
    missing_subscriptions = 0
    
    for user in users:
        total_users += 1
        user_id = str(user["_id"])
        email = user.get("email", "unknown")
        stored_sub_id = user.get("stripeSubscriptionId")
        stripe_customer_id = user.get("stripeCustomerId")
        
        if not stored_sub_id:
            print(f"⏭️  {email} ({user_id[:8]}...): No stored subscription ID")
            continue
        
        users_with_subscriptions += 1
        print(f"\n✓ {email} ({user_id[:8]}...)")
        print(f"  Stored Sub ID: {stored_sub_id}")
        print(f"  Stripe Customer ID: {stripe_customer_id}")
        
        # Try to fetch subscription from Stripe
        try:
            subscription = stripe.Subscription.retrieve(stored_sub_id)
            print(f"  ✅ Subscription found in Stripe")
            print(f"     Status: {subscription.status}")
            # Safely get plan nickname
            plan_name = "N/A"
            if subscription.items and subscription.items.data and len(subscription.items.data) > 0:
                price = subscription.items.data[0].price
                plan_name = price.nickname or price.id
            print(f"     Plan: {plan_name}")
            valid_subscriptions += 1
            
        except stripe.error.InvalidRequestError as e:
            print(f"  ❌ Subscription NOT found in Stripe: {e.message}")
            invalid_subscriptions += 1
            
            # Try to find active subscriptions for this customer
            if stripe_customer_id:
                print(f"  Checking for other subscriptions for customer {stripe_customer_id}...")
                try:
                    subs = stripe.Subscription.list(customer=stripe_customer_id, limit=10)
                    if subs.data:
                        print(f"  Found {len(subs.data)} subscription(s) for this customer:")
                        for sub in subs.data:
                            print(f"    - {sub.id} (status: {sub.status})")
                    else:
                        print(f"  No subscriptions found for this customer")
                        missing_subscriptions += 1
                except Exception as e:
                    print(f"  Error fetching customer subscriptions: {e}")
        
        except Exception as e:
            print(f"  ⚠️  Error retrieving subscription: {e}")
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"Total users: {total_users}")
    print(f"Users with stored subscription IDs: {users_with_subscriptions}")
    print(f"  ✅ Valid subscriptions: {valid_subscriptions}")
    print(f"  ❌ Invalid/not found: {invalid_subscriptions}")
    print(f"  ⏭️  No subscriptions at all: {missing_subscriptions}")
    
    if invalid_subscriptions > 0:
        print("\n⚠️  ACTION REQUIRED: Some users have invalid subscription IDs in the database.")
        print("   These need to be cleared or updated with valid subscription IDs.")

if __name__ == "__main__":
    verify_subscriptions()
