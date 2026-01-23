import os
import stripe
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

sub_id = "sub_1Ssd9oAzfbk6X9z4DhPsqG3k"
try:
    sub = stripe.Subscription.retrieve(sub_id)
    print(f"Subscription: {sub.id}")
    print(f"Status: {sub.status}")
    print(f"Metadata: {sub.metadata}")
    items = sub.get('items', {}).get('data', [])
    if items:
        print(f"Price ID: {items[0].price.id}")
except Exception as e:
    print(f"Error: {e}")
