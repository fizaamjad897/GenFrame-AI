from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import stripe
from bson import ObjectId
from datetime import datetime
import os

# This will be added to main.py
router = APIRouter()

class ManualSyncRequest(BaseModel):
    email: str

@router.post("/api/stripe/manual-sync")
async def manual_sync_subscription(request: ManualSyncRequest):
    """
    Manually sync a user's Stripe subscription to their account.
    This is useful when webhooks fail to process.
    """
    from auth import users_collection, plans_collection
    
    print(f"\n🔍 Manual sync requested for: {request.email}")
    
    # Find user
    user = users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_id = str(user["_id"])
    customer_id = user.get("stripeCustomerId")
    
    if not customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer ID found")
    
    print(f"✅ User found: {user_id}")
    print(f"🔍 Checking Stripe for customer: {customer_id}")
    
    try:
        # Get active subscriptions from Stripe
        subscriptions = stripe.Subscription.list(
            customer=customer_id,
            status='active',
            limit=10
        )
        
        if not subscriptions.data:
            raise HTTPException(
                status_code=404,
                detail="No active subscriptions found in Stripe. Payment may not have completed."
            )
        
        # Get the most recent active subscription
        sub = subscriptions.data[0]
        subscription_id = sub.id
        
        print(f"✅ Found active subscription: {subscription_id}")
        
        # Get price info to determine plan
        if not sub.items or not sub.items.data:
            raise HTTPException(status_code=400, detail="Subscription has no items")
        
        price_id = sub.items.data[0].price.id
        amount = sub.items.data[0].price.unit_amount / 100
        
        print(f"   Price ID: {price_id}")
        print(f"   Amount: ${amount}")
        
        # Map price ID to plan
        plan_mapping = {
            os.getenv("STRIPE_PRICE_T_STARTER"): ("Starter", 1000),
            os.getenv("STRIPE_PRICE_T_GROWTH"): ("Growth", 3000),
            os.getenv("STRIPE_PRICE_T_SCALE"): ("Scale", 5000),
            os.getenv("STRIPE_PRICE_M_STARTER"): ("Starter", 1000),
            os.getenv("STRIPE_PRICE_M_GROWTH"): ("Growth", 3000),
            os.getenv("STRIPE_PRICE_M_SCALE"): ("Scale", 5000),
        }
        
        plan_info = plan_mapping.get(price_id)
        if not plan_info:
            # Default to Growth if unknown
            plan_code = "Growth"
            included_units = 3000
        else:
            plan_code, included_units = plan_info
        
        # Determine engine type from price ID
        engine_type = "creation" if price_id in [
            os.getenv("STRIPE_PRICE_M_STARTER"),
            os.getenv("STRIPE_PRICE_M_GROWTH"),
            os.getenv("STRIPE_PRICE_M_SCALE")
        ] else "transformation"
        
        print(f"\n📝 Updating user account:")
        print(f"   Plan: {plan_code}")
        print(f"   Engine: {engine_type}")
        print(f"   Units: {included_units}")
        
        # Update user account
        new_credits = {
            "monthly_units_used": 0.0,
            "monthly_units_max": float(included_units),
            "addon_units_used": 0.0,
            "addon_units_max": 0.0,
            "remaining_units": float(included_units)
        }
        
        result = users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {
                "plan": plan_code,
                "engineType": engine_type,
                "credits": new_credits,
                "maxUnits": int(included_units),
                "units": 0,
                "stripeSubscriptionId": subscription_id,
                "updatedAt": datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            print(f"\n✅ SUCCESS! Account updated")
            return {
                "success": True,
                "plan": plan_code,
                "engine_type": engine_type,
                "credits": included_units,
                "subscription_id": subscription_id
            }
        else:
            print(f"⚠️  Account may already be up to date")
            return {
                "success": True,
                "plan": plan_code,
                "engine_type": engine_type,
                "credits": included_units,
                "subscription_id": subscription_id,
                "message": "Account was already up to date"
            }
            
    except stripe.error.StripeError as e:
        print(f"❌ Stripe error: {e}")
        raise HTTPException(status_code=400, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
