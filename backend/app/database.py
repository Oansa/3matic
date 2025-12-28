from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "3matic")

client = None
db = None

async def init_db():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client[DATABASE_NAME]
        # Test connection
        await client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create indexes
        try:
            await db.users.create_index("email", unique=True)
            await db.communities.create_index("userId")
            await db.communities.create_index("platform")
        except Exception as e:
            print(f"⚠️  Warning: Could not create indexes: {e}")
        
    except (ConnectionFailure, Exception) as e:
        print(f"⚠️  Warning: MongoDB not available ({e})")
        print("   Server will start in test mode without database")
        client = None
        db = None

def get_db():
    if db is None:
        raise Exception("Database not initialized. Please start MongoDB or configure connection.")
    return db

