#!/usr/bin/env python3
"""
Fix Stripe subscriptions in the database.
Removes or updates invalid subscription IDs.
"""

import os
from dotenv import load_dotenv
import stripe
from bson import ObjectId
from auth import users_collection

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def fix_invalid_subscriptions(dry_run=True):
    """Find and fix invalid subscription IDs."""
    
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"🔧 Fixing Stripe Subscriptions ({mode})...\n")
    
    users = users_collection.find({})
    fixed = 0
    removed = 0
    
    for user in users:
        user_id = str(user["_id"])
        email = user.get("email", "unknown")
        stored_sub_id = user.get("stripeSubscriptionId")
        stripe_customer_id = user.get("stripeCustomerId")
        
        if not stored_sub_id:
            continue
        
        # Try to fetch subscription from Stripe
        try:
            subscription = stripe.Subscription.retrieve(stored_sub_id)
            # Subscription is valid, skip
            continue
            
        except stripe.error.InvalidRequestError:
            # Subscription is invalid, try to fix it
            print(f"❌ Invalid subscription for {email} ({user_id[:8]}...): {stored_sub_id}")
            
            if stripe_customer_id:
                try:
                    # Try to find an active subscription for this customer
                    subs = stripe.Subscription.list(
                        customer=stripe_customer_id,
                        status='active',
                        limit=1
                    )
                    
                    if subs.data:
                        new_sub_id = subs.data[0].id
                        print(f"  ✅ Found active subscription: {new_sub_id}")
                        
                        if not dry_run:
                            users_collection.update_one(
                                {"_id": ObjectId(user_id)},
                                {"$set": {"stripeSubscriptionId": new_sub_id}}
                            )
                            print(f"  ✓ Updated in database")
                        fixed += 1
                    else:
                        print(f"  ⏭️  No active subscriptions found, removing invalid ID")
                        
                        if not dry_run:
                            users_collection.update_one(
                                {"_id": ObjectId(user_id)},
                                {"$unset": {"stripeSubscriptionId": ""}}
                            )
                            print(f"  ✓ Removed from database")
                        removed += 1
                
                except Exception as e:
                    print(f"  ⚠️  Error: {e}")
            else:
                print(f"  ⏭️  No customer ID, removing subscription ID")
                
                if not dry_run:
                    users_collection.update_one(
                        {"_id": ObjectId(user_id)},
                        {"$unset": {"stripeSubscriptionId": ""}}
                    )
                    print(f"  ✓ Removed from database")
                removed += 1
        
        except Exception as e:
            print(f"⚠️  Error checking subscription for {email}: {e}")
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"Fixed (updated with valid ID): {fixed}")
    print(f"Removed (no valid subscription): {removed}")
    
    if dry_run:
        print(f"\n💡 This was a DRY RUN. Run with --apply to make changes.")

if __name__ == "__main__":
    import sys
    dry_run = "--apply" not in sys.argv
    fix_invalid_subscriptions(dry_run=dry_run)
