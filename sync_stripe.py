import stripe
import os
from dotenv import load_dotenv
from auth import users_collection, update_user_plan
from bson import ObjectId

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def sync_user_purchase(email):
    print(f"Searching for successful payments for: {email}")
    
    # 1. Find user in DB
    user = users_collection.find_one({"email": email})
    if not user:
        print(f"Error: User with email {email} not found in database.")
        return

    user_id = str(user["_id"])
    customer_id = user.get("stripeCustomerId")
    
    if not customer_id:
        print("Error: No Stripe Customer ID found for this user in DB.")
        return

    # 2. Get successful checkout sessions from Stripe
    try:
        sessions = stripe.checkout.Session.list(limit=5, customer=customer_id)
        
        latest_valid_session = None
        for s in sessions.data:
            if s.payment_status == "paid":
                latest_valid_session = s
                break
        
        if not latest_valid_session:
            print("No successful (paid) checkout sessions found on Stripe for this customer.")
            return

        # 3. Extract plan details from metadata
        metadata = latest_valid_session.get("metadata", {})
        plan_code = metadata.get("plan_code")
        engine_type = metadata.get("engine_type", "transformation")
        
        if not plan_code:
            print("Found paid session, but 'plan_code' metadata is missing.")
            print("Looking at line items instead...")
            # Fallback to line items if metadata is somehow missing
            line_items = stripe.checkout.Session.list_line_items(latest_valid_session.id)
            description = line_items.data[0].description.lower()
            if "scale" in description: plan_code = "Scale"
            elif "growth" in description: plan_code = "Growth"
            elif "starter" in description: plan_code = "Starter"
            else: plan_code = "Scale" # Default fallback for the $477 price point

        print(f"Found successful purchase: {plan_code}")
        
        # 4. Update the DB manually
        success = update_user_plan(user_id, plan_code, engine_type)
        if success:
            # Also update subscription ID if present
            sub_id = latest_valid_session.get("subscription")
            if sub_id:
                users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"stripeSubscriptionId": sub_id}}
                )
            print(f"SUCCESS: Account {email} has been updated to {plan_code} plan!")
            print("Please refresh your dashboard UI now.")
        else:
            print("Failed to update database record.")

    except Exception as e:
        print(f"Error during synchronization: {e}")

if __name__ == "__main__":
    sync_user_purchase("teststripe@gmail.com")
