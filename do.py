from motor.motor_asyncio import AsyncIOMotorClient; import asyncio, os; from dotenv import load_dotenv; load_dotenv(); async def run(): db = AsyncIOMotorClient(os.getenv('MONGODB_URI')).get_database(os.getenv('MONGODB_DB_NAME')); async for u in db.users.find({}): print(u.get('email'), u.get('plan'), u.get('engine_data', {}).get('transformation', {}).get('plan')); 
asyncio.run(run())
