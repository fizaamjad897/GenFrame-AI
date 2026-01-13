import os
import stripe
from dotenv import load_dotenv
from auth import users_collection, update_user_plan
from bson import ObjectId

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Mapping Stripe Products to Internal Internal Plans & Engine Types
# In production, these would be the Stripe Price IDs (e.g., price_123...)
PLAN_MAPPING = {
    # Creation Engine (M)
    "M_Starter": {"plan": "Starter", "engine": "creation"},
    "M_Growth": {"plan": "Growth", "engine": "creation"},
    "M_Scale": {"plan": "Scale", "engine": "creation"},
    
    # Transformation Engine (T)
    "T_Starter": {"plan": "Starter", "engine": "transformation"},
    "T_Growth": {"plan": "Growth", "engine": "transformation"},
    "T_Scale": {"plan": "Scale", "engine": "transformation"},
}

def create_checkout_session(user_id: str, plan_key: str):
    """
    Create a Stripe Checkout Session for a specific plan.
    plan_key should be one of the keys in PLAN_MAPPING (e.g., 'M_Starter')
    """
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
            
        # Get Price ID from environment or mapping
        # For simplicity, we assume environment variables match the keys
        price_id = os.getenv(f"STRIPE_PRICE_{plan_key.upper()}")
        
        if not price_id:
            print(f"Error: Price ID for {plan_key} not found in .env")
            return None

        # Create or use existing Stripe Customer
        customer_id = user.get("stripeCustomerId")
        if not customer_id:
            customer = stripe.Customer.create(
                email=user["email"],
                metadata={"user_id": user_id}
            )
            customer_id = customer.id
            users_collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"stripeCustomerId": customer_id}}
            )

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=os.getenv("FRONTEND_URL") + "/dashboard?payment=success",
            cancel_url=os.getenv("FRONTEND_URL") + "/dashboard?payment=cancel",
            metadata={
                "user_id": user_id,
                "plan_key": plan_key
            }
        )
        return session.url
    except Exception as e:
        print(f"Stripe Error: {e}")
        return None

def handle_webhook_event(payload, sig_header):
    """
    Handle Stripe webhook events (e.g., checkout.session.completed)
    """
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print(f"Webhook Signature Error: {e}")
        return False

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        user_id = session["metadata"].get("user_id")
        plan_key = session["metadata"].get("plan_key")
        subscription_id = session.get("subscription")

        if user_id and plan_key:
            # Map plan key to internal plan and engine
            mapping = PLAN_MAPPING.get(plan_key)
            if mapping:
                # 1. Update user's plan and credits
                update_user_plan(user_id, mapping["plan"])
                
                # 2. Update engine type
                from auth import update_user_engine
                update_user_engine(user_id, mapping["engine"])
                
                # 3. Save subscription ID
                users_collection.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"stripeSubscriptionId": subscription_id}}
                )
                print(f"✅ User {user_id} upgraded to {plan_key}")
                return True
                
    return True
