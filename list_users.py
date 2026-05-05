from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME', 'visual_engine')]
for u in db.users.find({}):
    print(u.get('email'), repr(u.get('plan')), u.get('is_postpaid'), u.get('engine_data', {}).get('transformation', {}).get('plan'))
