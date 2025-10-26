from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from fastapi import Depends
import os

MONGO_INITDB_ROOT_USERNAME= os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD= os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGODB_USER_HOST = os.getenv("MONGODB_USER_HOST")
MONGO_USER_DB = os.getenv("MONGO_USER_DB")
MONGO_PORT= os.getenv("MONGO_PORT", "27018")

DATABASE_URL = f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@mongo_user_db:27017/{MONGO_USER_DB}?authSource=admin"

print(f"Connecting to MongoDB at: mongodb://{MONGO_INITDB_ROOT_USERNAME}:****@mongo_user_db:27017/{MONGO_USER_DB}")

try:
    client = MongoClient(DATABASE_URL, serverSelectionTimeoutMS=5000)
    # Test connection
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB")
    
    database = client[MONGO_USER_DB]
    user_profiles = database.user_profiles
    user_profiles.create_index("user_id", unique=True)
    
except Exception as e:
    print(f"❌ Failed to connect to MongoDB: {e}")
    raise e