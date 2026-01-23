import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

email = "fizaamjad541@gmail.com"
customer = stripe.Customer.list(email=email, limit=1).data
if customer:
    cus_id = customer[0].id
    subs = stripe.Subscription.list(customer=cus_id).data
    for s in subs:
        print(f"Sub: {s.id}, Status: {s.status}, Metadata: {s.metadata}")
        items = s.get('items', {}).get('data', [])
        if items:
            print(f"  Price: {items[0].get('price', {}).get('id')}")
else:
    print("Customer not found in Stripe")
