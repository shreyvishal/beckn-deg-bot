import os
from pymongo import MongoClient
from pymongo.database import Database
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "beckn_deg_bot")

class DatabaseManager:
    _instance = None
    _client = None
    _database = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Initialize database connection"""
        if self._client is None:
            self._client = MongoClient(MONGODB_URL)
            self._database = self._client[DATABASE_NAME]
            print(f"Connected to MongoDB: {DATABASE_NAME}")
    
    def get_database(self) -> Database:
        """Get database instance"""
        if self._database is None:
            self.connect()
        return self._database
    
    def close_connection(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            print("MongoDB connection closed")

# Global database manager instance
db_manager = DatabaseManager()

def get_database() -> Database:
    """Get database instance for dependency injection"""
    return db_manager.get_database()

# Collection names
USERS_COLLECTION = "users"
SESSIONS_COLLECTION = "sessions" 