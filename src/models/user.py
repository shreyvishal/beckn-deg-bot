from datetime import datetime, timezone
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId
from pymongo.database import Database
from config.database import get_database, USERS_COLLECTION
from utils.auth import get_password_hash, verify_password


class UserCreate(BaseModel):
    meter_id: str = Field(min_length=3, description="Meter ID must be at least 3 characters")
    email: EmailStr
    password: str = Field(min_length=6, description="Password must be at least 6 characters")
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    meter_id: str
    password: str


class UserResponse(BaseModel):
    id: str
    meter_id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }


class UserInDB(BaseModel):
    id: Optional[str] = None
    meter_id: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


class UserService:
    def __init__(self, database: Database = None):
        self.db = database or get_database()
        self.collection = self.db[USERS_COLLECTION]
        
        # Create unique indexes on meter_id and email
        self.collection.create_index("meter_id", unique=True)
        self.collection.create_index("email", unique=True)
    
    def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """Create a new user"""
        # Check if user already exists by meter_id or email
        if self.get_user_by_meter_id(user_data.meter_id) or self.get_user_by_email(user_data.email):
            return None
        
        # Hash password and create user document
        hashed_password = get_password_hash(user_data.password)
        now = datetime.now(timezone.utc)
        
        user_doc = {
            "meter_id": user_data.meter_id,
            "email": user_data.email,
            "hashed_password": hashed_password,
            "full_name": user_data.full_name,
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        
        try:
            result = self.collection.insert_one(user_doc)
            user_doc["_id"] = result.inserted_id
            return self._doc_to_user_response(user_doc)
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email"""
        user_doc = self.collection.find_one({"email": email})
        if user_doc:
            return self._doc_to_user_in_db(user_doc)
        return None
    
    def get_user_by_meter_id(self, meter_id: str) -> Optional[UserInDB]:
        """Get user by meter_id"""
        user_doc = self.collection.find_one({"meter_id": meter_id})
        if user_doc:
            return self._doc_to_user_in_db(user_doc)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserResponse]:
        """Get user by ID"""
        try:
            user_doc = self.collection.find_one({"_id": ObjectId(user_id)})
            if user_doc:
                return self._doc_to_user_response(user_doc)
        except Exception as e:
            print(f"Error getting user by ID: {e}")
        return None
    
    def authenticate_user(self, meter_id: str, password: str) -> Optional[UserResponse]:
        """Authenticate user with meter_id and password"""
        user = self.get_user_by_meter_id(meter_id)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Convert to response model
        user_doc = self.collection.find_one({"meter_id": meter_id})
        return self._doc_to_user_response(user_doc)
    
    def update_user_activity(self, user_id: str) -> bool:
        """Update user's last activity timestamp"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"updated_at": datetime.now(timezone.utc)}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user activity: {e}")
            return False
    
    def _doc_to_user_response(self, doc: Dict[str, Any]) -> UserResponse:
        """Convert MongoDB document to UserResponse"""
        return UserResponse(
            id=str(doc["_id"]),
            meter_id=doc["meter_id"],
            email=doc["email"],
            full_name=doc.get("full_name"),
            is_active=doc.get("is_active", True),
            created_at=doc["created_at"]
        )
    
    def _doc_to_user_in_db(self, doc: Dict[str, Any]) -> UserInDB:
        """Convert MongoDB document to UserInDB"""
        return UserInDB(
            id=str(doc["_id"]),
            meter_id=doc["meter_id"],
            email=doc["email"],
            hashed_password=doc["hashed_password"],
            full_name=doc.get("full_name"),
            is_active=doc.get("is_active", True),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )


# Global user service instance
user_service = UserService() 