from auth import get_user_by_email
import json
from bson import json_util

user = get_user_by_email("fizaamjad541@gmail.com")
if user:
    # Print clean JSON for me to read
    print(json.dumps(user, indent=2, default=json_util.default))
else:
    print("User not found.")
