#!/usr/bin/env python3
"""
Check all subscriptions for admin11
"""

import os
from dotenv import load_dotenv
import stripe

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

customer_id = "cus_TpKoI3j5nfqT9o"

print(f"Checking all subscriptions for: {customer_id}\n")

subs = stripe.Subscription.list(customer=customer_id, limit=10)

for i, sub in enumerate(subs, 1):
    print(f"Subscription #{i}:")
    print(f"  ID: {sub.id}")
    print(f"  Status: {sub.status}")
    print()

# Find an active one
active_subs = [s for s in stripe.Subscription.list(customer=customer_id, status='active', limit=10)]

if active_subs:
    print(f"✅ Found {len(active_subs)} ACTIVE subscription(s)\n")
    for sub in active_subs:
        print(f"Ready to test cancel with: {sub.id}")
        print(f"\nTrying to cancel...")
        try:
            result = stripe.Subscription.delete(sub.id)
            print(f"✅ CANCELLED!")
            print(f"  ID: {result.id}")
            print(f"  Status: {result.status}")
        except Exception as e:
            print(f"❌ Error: {e}")
else:
    print("❌ No ACTIVE subscriptions found!")
