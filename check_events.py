from auth import db
import json
from bson import json_util

# Check last 10 stripe events
events = list(db["stripe_events"].find().sort("processedAt", -1).limit(10))
print(json.dumps(events, indent=2, default=json_util.default))
