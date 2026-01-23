from auth import users_collection
import json
from bson import json_util

user = users_collection.find_one({"email": "fizaamjad541@gmail.com"})
if user:
    # Print only the fields that are interesting to avoid too much output
    interesting_fields = {
        "email": user.get("email"),
        "plan": user.get("plan"),
        "credits": user.get("credits"),
        "maxUnits": user.get("maxUnits"),
        "units": user.get("units"),
        "engineType": user.get("engineType"),
        "stripeSubscriptionId": user.get("stripeSubscriptionId"),
        "engine_data": user.get("engine_data")
    }
    print(json.dumps(interesting_fields, indent=2, default=json_util.default))
else:
    print("User not found.")
