from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.client = None
        self.database = None


db = Database()


async def get_database():
    return db.database


async def connect_to_mongo():
    """Create database connection"""
    mongo_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DATABASE_NAME", "risk_app")
    
    db.client = AsyncIOMotorClient(mongo_url)
    db.database = db.client[db_name]
    
    # Test connection
    try:
        await db.client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()