import os
import time
from pymongo import MongoClient

MONGO_INITDB_ROOT_USERNAME = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_INITDB_ROOT_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
MONGO_USER_HOST = os.getenv("MONGO_USER_HOST")
MONGO_USER_DB = os.getenv("MONGO_USER_DB")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

DATABASE_URL = (
    f"mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}"
    f"@{MONGO_USER_HOST}:{MONGO_PORT}/{MONGO_USER_DB}?authSource=admin"
)

print(f"Connecting to MongoDB at: mongodb://{MONGO_INITDB_ROOT_USERNAME}:****@{MONGO_USER_HOST}:{MONGO_PORT}/{MONGO_USER_DB}")

def get_database(retries: int = 10, delay: int = 3):
    for attempt in range(retries):
        try:
            print(f"Connecting to MongoDB (attempt {attempt + 1})...")
            client = MongoClient(DATABASE_URL, serverSelectionTimeoutMS=2000)
            client.admin.command("ping")
            db = client[MONGO_USER_DB]

            db.user_profiles.create_index("user_id", unique=True)
            print("✅ MongoDB index created")

            return db
        except Exception as e:
            print(f"⚠️  Mongo not ready: {e}")
            time.sleep(delay)
    raise RuntimeError("❌ Could not connect to MongoDB after several attempts.")

database = get_database()
user_profiles = database.user_profiles
