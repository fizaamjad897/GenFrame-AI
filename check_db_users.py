from config import settings
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
async def main():
 client = AsyncIOMotorClient(settings.MONGODB_URI)
 db = client.visual_engine_secure
 async for doc in db.users.find({}):
  print(doc.get('email'), doc.get('is_postpaid', False), doc.get('plan'))
asyncio.run(main())
