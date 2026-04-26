import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from datetime import datetime

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("DATABASE_NAME", "agro_db")

    def connect(self):
        # Connection disabled for Review Mode
        print("OK: Running in Review Mode (Local Data)")
        return True

    def get_db(self):
        return None  # No database access needed for review

    def log_activity(self, activity_type, input_data, result, metadata=None):
        # Logging disabled for Review Mode
        return True

    def sync_user(self, user_info):
        # Sync disabled for Review Mode
        return True

# Singleton instance
mongo = MongoDB()

def get_db():
    return mongo.get_db()
