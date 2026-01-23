import os
import stripe
from dotenv import load_dotenv
from auth import (
    users_collection,
    stripe_events_collection,
    update_user_plan,
    add_addon_credits,
    cancel_user_plan,
    reset_monthly_credits,
)
from bson import ObjectId

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Production mode detection
def is_production_mode():
    """Check if we're running in production mode based on Stripe API key"""
    api_key = stripe.api_key or ""
    return api_key.startswith("sk_live_")

# Note: Stripe automatically rejects test cards when using production keys (sk_live_)
# We don't need to validate card numbers - Stripe handles this at the API level
# Our validation focuses on catching configuration errors (test keys in production)

def validate_stripe_configuration():
    """Validate Stripe configuration and warn about potential issues"""
    api_key = stripe.api_key or ""
    
    if not api_key:
        print("❌ CRITICAL: STRIPE_SECRET_KEY is not set!")
        return False
    
    # Check if using test key in production environment
    is_prod_env = os.getenv("ENVIRONMENT", "").lower() in ("production", "prod", "live")
    is_test_key = api_key.startswith("sk_test_")
    is_live_key = api_key.startswith("sk_live_")
    
    if is_prod_env and is_test_key:
        print("⚠️  WARNING: Production environment detected but using TEST Stripe key!")
        print("⚠️  This will cause all payments to fail in production!")
        print("⚠️  Please set STRIPE_SECRET_KEY to a live key (sk_live_...)")
        return False
    
    if not is_live_key and not is_test_key:
        print("⚠️  WARNING: Stripe API key format is invalid!")
        print("⚠️  Expected format: sk_test_... or sk_live_...")
        return False
    
    if is_live_key:
        print("✅ Production Stripe key detected (sk_live_...)")
    else:
        print("ℹ️  Test Stripe key detected (sk_test_...)")
    
    return True

# Validate on module load
if not validate_stripe_configuration():
    print("⚠️  Stripe configuration validation failed. Please check your environment variables.")

def create_checkout_session(user_id: str, plan_code: str = None, engine_type: str = "transformation", order_type: str = "subscription"):
    """
    Create a Stripe Checkout Session for a specific plan or addon.
    order_type: "subscription" or "addon"
    """
    try:
        user = users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
            
        # 1. Determine Price ID based on Plan & Engine
        price_id = None
        included_units = 0
        
        if order_type == "subscription":
            # Map plan_code + engine_type to Price ID in .env
            env_key = f"STRIPE_PRICE_{'M' if engine_type == 'creation' else 'T'}_{plan_code.upper()}"
            price_id = os.getenv(env_key)
            
            # Get plan details from database for metadata
            from auth import plans_collection
            plan_doc = plans_collection.find_one({"name": (plan_code or "").capitalize()})
            if plan_doc:
                included_units = int(plan_doc.get("includedUnits", 0))
        else:
            # For Addons (e.g. 'ADDON_100', 'ADDON_50')
            env_key = f"STRIPE_PRICE_{plan_code.upper()}"
            price_id = os.getenv(env_key)
            print(f"🔍 Looked up add-on price ID with key {env_key}: {price_id}")

        if not price_id:
            print(f"Error: Price ID for {plan_code} ({engine_type}) not found in .env")
            return None

        # 2. Get or Create Stripe Customer
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

        # 3. Dynamic Mode Detection (Robustness)
        # Fetch price object to see if it's recurring or one-time
        try:
            price_obj = stripe.Price.retrieve(price_id)
            is_recurring = price_obj.type == "recurring"
            print(f"💰 Stripe Price Detection: {price_id} is {'RECURRING' if is_recurring else 'ONE-TIME'}")
            
            # If it's an addon but the price is recurring, we have a configuration mismatch
            if order_type == "addon" and is_recurring:
                print(f"⚠️  CRITICAL CONFIG ERROR: You are using a RECURRING price ({price_id}) for a one-time ADDON.")
                print(f"👉 Please create a NEW price in Stripe for this product and set 'Pricing' to 'One-time' (not 'Recurring').")
                # We'll stay with 'payment' mode to let it fail or 'subscription' to let it work, 
                # but 'subscription' for an addon is usually wrong. We'll stick to the logic but warn.
        except Exception as e:
            print(f"⚠️  Could not retrieve price info from Stripe: {e}")
            is_recurring = (order_type == "subscription") # Fallback to order_type

        # 4. Create Session with enhanced metadata
        session_metadata = {
            "user_id": user_id,
            "plan_code": plan_code,
            "engine_type": engine_type,
            "order_type": order_type
        }
        
        # Add included_units for subscriptions to ensure webhook has this info
        if order_type == "subscription" and included_units > 0:
            session_metadata["included_units"] = str(included_units)
        
        session_args = {
            "customer": customer_id,
            "payment_method_types": ["card"],
            "line_items": [{
                "price": price_id,
                "quantity": 1,
            }],
            "mode": "subscription" if is_recurring else "payment",
            "success_url": os.getenv("FRONTEND_URL") + "/billing/success?session_id={CHECKOUT_SESSION_ID}",
            "cancel_url": os.getenv("FRONTEND_URL") + "/billing/cancel",
            "metadata": session_metadata
        }
        
        # Propagate metadata to subscription so it's available in all webhooks
        if is_recurring:
            session_args["subscription_data"] = {"metadata": session_metadata}
            
        session = stripe.checkout.Session.create(**session_args)
        
        print(f"✅ Created checkout session for user {user_id}: {plan_code} ({engine_type}) - {included_units} units")
        return session.url
    except Exception as e:
        print(f"Stripe Error: {e}")
        return None

def create_portal_session(customer_id: str):
    """
    Create a Stripe Billing Portal session for users to manage subscriptions.
    """
    try:
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=os.getenv("FRONTEND_URL") + "/billing",
        )
        return session.url
    except Exception as e:
        print(f"Portal Error: {e}")
        return None

def handle_webhook_event(payload, sig_header):
    """
    Handle Stripe webhook events: 
    - checkout.session.completed (First buy / Addon)
    - invoice.paid (Renewal)
    - customer.subscription.deleted (Cancellation)
    """
    endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    # Validate webhook secret in production
    if is_production_mode() and not endpoint_secret:
        print("❌ CRITICAL: STRIPE_WEBHOOK_SECRET is not set in production mode!")
        print("❌ Webhook signature verification will fail!")
        return False
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except Exception as e:
        print(f"Webhook Signature Error: {e}")
        # In production, log this as a security event
        if is_production_mode():
            print("🚨 SECURITY ALERT: Invalid webhook signature in production!")
        return False

    event_id = event.get("id")
    event_type = event.get("type")
    
    # Idempotency: ignore already-processed events
    try:
        if event_id:
            existing = stripe_events_collection.find_one({"event_id": event_id})
            if existing:
                print(f"⏭️  Webhook event {event_id} already processed")
                return True
    except Exception as e:
        print(f"Webhook Idempotency Lookup Error: {e}")

    # Mark as processing BEFORE we do the work to prevent double-processing on retries
    try:
        if event_id:
            stripe_events_collection.insert_one({
                "event_id": event_id,
                "type": event_type,
                "created": event.get("created"),
                "processedAt": __import__("datetime").datetime.utcnow(),
                "status": "completed"
            })
    except Exception as e:
        print(f"Warning: Could not record event {event_id}: {e}")
        # Continue processing anyway

    # A) Payment Success (Subscription or One-time)
    if event_type == "checkout.session.completed":
        session = event["data"]["object"]
        metadata = session.get("metadata", {})
        user_id = metadata.get("user_id")
        plan_code = metadata.get("plan_code")
        engine_type = metadata.get("engine_type", "transformation")
        order_type = metadata.get("order_type")
        subscription_id = session.get("subscription")
        
        # Extract included_units from metadata (passed during checkout session creation)
        included_units_str = metadata.get("included_units", "0")
        try:
            included_units = float(included_units_str)
        except (ValueError, TypeError):
            included_units = 0.0
        
        print(f"🔔 Processing checkout.session.completed for user {user_id}, plan {plan_code}, engine {engine_type}, units: {included_units}")

        if user_id:
            if order_type == "subscription":
                # First, try to get subscription_id from the session
                if not subscription_id:
                    print(f"⚠️  No subscription_id in session object, attempting to retrieve from customer...")
                    customer_id = session.get("customer")
                    if customer_id:
                        try:
                            # Fetch the subscription from the customer
                            subscriptions = stripe.Subscription.list(customer=customer_id, limit=10)
                            if subscriptions.data:
                                # Find the active or most recent subscription for this plan
                                for sub in subscriptions.data:
                                    if sub.status in ['active', 'trialing', 'past_due']:
                                        subscription_id = sub.id
                                        print(f"✅ Found active subscription: {subscription_id}")
                                        break
                                # If still not found, get the most recent one
                                if not subscription_id:
                                    subscription_id = subscriptions.data[0].id
                                    print(f"ℹ️  Using most recent subscription: {subscription_id}")
                        except Exception as e:
                            print(f"❌ Error fetching subscription from customer {customer_id}: {e}")
                else:
                    print(f"✅ Subscription ID found in session: {subscription_id}")
                
                # CRITICAL FIX: Save subscription ID to user document FIRST before updating plan
                # This ensures subscription_id is always available for cancellation
                if subscription_id:
                    try:
                        users_collection.update_one(
                            {"_id": ObjectId(user_id)},
                            {"$set": {
                                "stripeSubscriptionId": subscription_id,
                                "updatedAt": __import__("datetime").datetime.utcnow()
                            }}
                        )
                        print(f"✅ Saved Subscription ID: {subscription_id} for user {user_id}")
                    except Exception as e:
                        print(f"⚠️  Error saving subscription ID: {e}")
                else:
                    print(f"⚠️  No subscription_id found, will retry later if needed")
                
                # Update the plan
                print(f"📝 Updating user plan: {user_id} -> {plan_code} ({engine_type}) with {included_units} units")
                update_result = update_user_plan(user_id, plan_code, engine_type, subscription_id=subscription_id)
                
                if update_result:
                    print(f"✅ User plan updated successfully")
                else:
                    print(f"⚠️  User plan update returned False")
                
                # Verify credits were assigned
                try:
                    user = users_collection.find_one({"_id": ObjectId(user_id)})
                    if user:
                        credits = user.get("credits", {})
                        remaining = credits.get("remaining_units", 0)
                        monthly_max = credits.get("monthly_units_max", 0)
                        print(f"💰 User credits after update: {remaining} remaining, {monthly_max} monthly max")
                        
                        # Validate that credits match the plan
                        if monthly_max > 0:
                            print(f"✅ Subscription completed: User {user_id} -> {plan_code} (Sub: {subscription_id})")
                        else:
                            print(f"⚠️  WARNING: Credits not properly set for user {user_id}")
                    else:
                        print(f"⚠️  Could not retrieve user {user_id} for verification")
                except Exception as e:
                    print(f"⚠️  Error verifying credits: {e}")
            
            elif order_type == "addon":
                # One-time payment (Addon)
                # Supports ADDON_50/100/200
                amount = 100.0
                if isinstance(plan_code, str):
                    if "50" in plan_code:
                        amount = 50.0
                    elif "200" in plan_code:
                        amount = 200.0
                    else:
                        amount = 100.0
                
                print(f"💰 Processing add-on for {amount} units (Plan: {plan_code}, Engine: {engine_type})")
                
                add_addon_credits(user_id, amount, engine_type=engine_type)
                print(f"✅ Addon completed: User {user_id} -> {amount} units for engine {engine_type}")

    # B) Renewal or Update (Invoice Paid / Subscription Updated)
    elif event_type == "invoice.paid":
        invoice = event["data"]["object"]
        customer_id = invoice.get("customer")
        if customer_id:
            user = users_collection.find_one({"stripeCustomerId": customer_id})
            if user:
                reset_monthly_credits(str(user["_id"]))
                print(f"🔄 Subscription renewed: User {user['_id']}")

    elif event_type == "customer.subscription.updated":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        cancel_at_period_end = subscription.get("cancel_at_period_end", False)
        cancel_at = subscription.get("cancel_at")
        
        if customer_id:
            user = users_collection.find_one({"stripeCustomerId": customer_id})
            if user:
                # Determine engine
                engine_type = None
                metadata = subscription.get("metadata", {})
                engine_type = metadata.get("engine_type")
                
                if not engine_type:
                    engine_data = user.get("engine_data", {})
                    for eng_type, eng_info in engine_data.items():
                        if eng_info and eng_info.get("stripeSubscriptionId") == subscription_id:
                            engine_type = eng_type
                            break

                # 1. Detect Cancellation Pending
                if (cancel_at_period_end or cancel_at):
                    print(f"❌ Portal cancellation detected: {user['_id']}, Engine: {engine_type or 'all'}")
                    cancel_user_plan(str(user["_id"]), engine_type=engine_type, is_pending=True)
                    print(f"✅ User plan marked as cancelling locally via Portal Sync")
                
                # 2. Detect Resumption (Canceled status or schedule was cleared)
                else:
                    print(f"🔄 Portal resumption/update detected: {user['_id']}, Engine: {engine_type or 'all'}")
                    # We use update_user_plan to reactivate. 
                    # The determine_plan logic in _perform_stripe_sync is better, but here we can at least trigger a sub update
                    # To keep it simple and robust, let's just trigger update_user_plan if we can find the plan_code
                    plan_code = metadata.get("plan_code")
                    if not plan_code:
                        # Try to find plan_code from price mapping if possible
                        items = subscription.get("items", {}).get("data", [])
                        if items:
                            price_id = items[0].get("price", {}).get("id")
                            # We can't easily import the mapping from main.py here without circular imports
                            # So we rely on metadata or the next sync
                            pass
                    
                    if plan_code:
                        update_user_plan(str(user["_id"]), plan_code, engine_type=engine_type, subscription_id=subscription_id)
                        print(f"✅ User plan resumed locally via Portal Sync")
                    else:
                        print(f"⚠️  Could not resume automatically: No plan_code in metadata. Sync will catch this later.")

    # C) Cancellation (Subscription Deleted)
    elif event_type == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription.get("customer")
        subscription_id = subscription.get("id")
        
        if customer_id:
            user = users_collection.find_one({"stripeCustomerId": customer_id})
            if user:
                # Try to determine which engine this subscription was for
                engine_type = None
                
                # Check subscription metadata first
                subscription_metadata = subscription.get("metadata", {})
                if subscription_metadata:
                    if subscription_metadata.get("order_type") == "addon":
                        print(f"⏭️  Ignoring deletion of add-on subscription {subscription_id} to protect base plan.")
                        return True
                    engine_type = subscription_metadata.get("engine_type")
                
                # If not in metadata, check which engine has this subscription_id
                if not engine_type:
                    engine_data = user.get("engine_data", {})
                    # Check if any engine has this specific subscription_id
                    for eng_type, eng_info in engine_data.items():
                        if eng_info and eng_info.get("stripeSubscriptionId") == subscription_id:
                            engine_type = eng_type
                            break
                    
                    # Fallback: if not found in engine_data, check top-level for legacy
                    if not engine_type and user.get("stripeSubscriptionId") == subscription_id:
                        # Best guess based on user's current engineType
                        engine_type = user.get("engineType")
                
                # Cancel the plan (with engine_type if we found it)
                # CRITICAL FIX: Only cancel if we found the engine_type, otherwise log error
                if engine_type:
                    print(f"❌ Cancelling plan for user {user['_id']}, Engine: {engine_type}, Sub: {subscription_id}")
                    cancel_user_plan(str(user["_id"]), engine_type=engine_type)
                    print(f"❌ Subscription cancelled: User {user['_id']}, Engine: {engine_type}")
                else:
                    print(f"⚠️  WARNING: Could not determine engine_type for subscription {subscription_id}. Skipping cancellation to prevent affecting other engines.")
                    # Don't cancel if we can't determine which engine - this prevents accidental cancellation of other engines

    return True


def cancel_subscription(subscription_id: str, at_period_end: bool = False):
    """
    Cancel a Stripe subscription.
    If at_period_end is True, it will cancel at period end; otherwise immediately.

    Raises:
        ValueError: if Stripe returns an error while cancelling.
    """
    try:
        if at_period_end:
            subscription = stripe.Subscription.modify(subscription_id, cancel_at_period_end=True)
        else:
            subscription = stripe.Subscription.delete(subscription_id)
        return subscription
    except Exception as e:
        # Surface the Stripe error message to the caller for better debugging
        print(f"Cancel Error for subscription {subscription_id}: {e}")
        raise ValueError(str(e))