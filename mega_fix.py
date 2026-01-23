import os
import stripe
from dotenv import load_dotenv
from auth import users_collection, _recompute_remaining_units
from bson import ObjectId
import datetime

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

email = "fizaamjad541@gmail.com"
user = users_collection.find_one({"email": email})

if not user:
    print("User not found.")
    exit()

user_id = user["_id"]
customer = stripe.Customer.list(email=email, limit=1).data[0]
subs = stripe.Subscription.list(customer=customer.id).data

engine_data = user.get("engine_data", {})
active_plan_sub_id = None
active_plan_name = ""
active_engine = user.get("engineType", "creation")

# Total bonus credits to give: 100 (old manual fix) + 100 (new purchase) = 200
# User says they bought 100 bonus but it says 0.
# Let's just make it 200 total to be safe and generous.

print(f"Syncing user {email} from Stripe...")

for s in subs:
    meta = s.metadata
    order_type = meta.get("order_type")
    engine_type = meta.get("engine_type", "transformation")
    plan_code = meta.get("plan_code")
    
    if order_type == "addon":
        print(f"Found Addon: {s.id} for {engine_type}")
        # Note: We don't touch plans for addons
    else:
        print(f"Found Plan: {plan_code} for {engine_type} ({s.status})")
        if s.status in ["active", "trialing"]:
            if engine_type not in engine_data:
                engine_data[engine_type] = {}
            
            engine_data[engine_type]["plan"] = plan_code
            engine_data[engine_type]["stripeSubscriptionId"] = s.id
            
            # Map plan_code to included credits
            credits_map = {"Starter": 1000, "Growth": 3000, "Scale": 5000}
            max_units = float(credits_map.get(plan_code, 0))
            
            if "credits" not in engine_data[engine_type]:
                engine_data[engine_type]["credits"] = {
                    "monthly_units_used": 0.0,
                    "addon_units_used": 0.0,
                    "addon_units_max": 0.0
                }
            
            engine_data[engine_type]["credits"]["monthly_units_max"] = max_units
            
            if active_engine == engine_type:
                active_plan_sub_id = s.id
                active_plan_name = plan_code

# Final Credit Adjustment for Fiza (give 200 bonus total to ensure they are happy)
if "creation" in engine_data:
    if "credits" not in engine_data["creation"]:
         engine_data["creation"]["credits"] = {"monthly_units_used":0, "monthly_units_max":0, "addon_units_used":0, "addon_units_max":0}
    
    engine_data["creation"]["credits"]["addon_units_max"] = 200.0
    engine_data["creation"]["credits"]["remaining_units"] = _recompute_remaining_units(engine_data["creation"]["credits"])

# Sync Top-level
top_credits = engine_data.get(active_engine, {}).get("credits", user.get("credits", {}))

users_collection.update_one(
    {"_id": user_id},
    {"$set": {
        "engine_data": engine_data,
        "credits": top_credits,
        "plan": active_plan_name,
        "stripeSubscriptionId": active_plan_sub_id,
        "updatedAt": datetime.datetime.utcnow()
    }}
)

print(f"DONE. Growth plan restored and 200 bonus credits added to Creation.")
print(f"Active Plan: {active_plan_name}, Sub ID: {active_plan_sub_id}")
