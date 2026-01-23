#!/usr/bin/env python3
"""
Update database with correct active subscription ID
"""

import os
from dotenv import load_dotenv
from auth import users_collection
from bson import ObjectId
import stripe

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

email = "admin11@gmail.com"
customer_id = "cus_TpKoI3j5nfqT9o"

print(f"Fixing subscription for: {email}\n")

# Find active subscription
subs = stripe.Subscription.list(customer=customer_id, status='active', limit=1)

if subs:
    new_sub_id = list(subs)[0].id
    print(f"Found active subscription: {new_sub_id}\n")
    
    # Update database
    result = users_collection.update_one(
        {"email": email},
        {"$set": {"stripeSubscriptionId": new_sub_id}}
    )
    
    if result.modified_count > 0:
        print(f"✅ Database updated with: {new_sub_id}\n")
        print(f"Now you can test cancel! Try:")
        print(f"  1. Go to http://localhost:3000/billing")
        print(f"  2. Click 'Cancel Now'")
        print(f"  3. Or run: python test_cancel_api.py")
    else:
        print(f"❌ Failed to update database")
else:
    print(f"❌ No active subscriptions found!")
