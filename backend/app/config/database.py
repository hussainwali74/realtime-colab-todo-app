from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "todo_db")

client = None

async def connect_to_mongo():
    """Connect to MongoDB."""
    global client
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        raise e

async def close_mongo_connection():
    """Close MongoDB connection."""
    global client
    if client:
        client.close()
        print("MongoDB connection closed")

def get_database():
    """Get database instance."""
    if not client:
        raise Exception("Database not initialized. Call connect_to_mongo() first.")
    return client[DATABASE_NAME] 