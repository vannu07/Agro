"""
Database Module for MongoDB Integration

Handles MongoDB connections and user activity logging.
"""

from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from datetime import datetime
from typing import Dict, Any, Optional
import os
import json

class MongoDatabase:
    """MongoDB database handler"""
    
    def __init__(self, mongo_uri: str = None):
        """
        Initialize MongoDB connection
        
        Args:
            mongo_uri: MongoDB connection string (optional, uses env var if not provided)
        """
        self.mongo_uri = mongo_uri or os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        self.client = None
        self.db = None
        self.connected = False
        self._initialize()
    
    def _initialize(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=2000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client.get_default_database() or self.client['krishi_mitr']
            self.connected = True
            print("[MongoDB] Connected successfully")
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            print(f"[MongoDB] Connection failed: {e}")
            print("[MongoDB] Using in-memory fallback mode")
            self.connected = False
            self._fallback_memory = {}
    
    def sync_user(self, user_info: Dict[str, Any]):
        """
        Sync user information to database
        
        Args:
            user_info: User information from Auth0
        """
        if not self.connected:
            print("[MongoDB] Fallback: User data not persisted")
            return
        
        try:
            users_collection = self.db['users']
            user_id = user_info.get('sub')
            
            if user_id:
                users_collection.update_one(
                    {'_id': user_id},
                    {
                        '$set': {
                            'email': user_info.get('email'),
                            'name': user_info.get('name'),
                            'picture': user_info.get('picture'),
                            'last_updated': datetime.utcnow()
                        },
                        '$setOnInsert': {
                            'created_at': datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                print(f"[MongoDB] User {user_id} synced successfully")
        except Exception as e:
            print(f"[MongoDB] Error syncing user: {e}")
    
    def log_activity(self, activity_type: str, input_data: Dict[str, Any] = None, 
                     result: Dict[str, Any] = None, metadata: Dict[str, Any] = None,
                     user_id: str = None):
        """
        Log user activity to database
        
        Args:
            activity_type: Type of activity (crop_recommendation, disease_detection, etc.)
            input_data: Input parameters used
            result: Result of the activity
            metadata: Additional metadata
            user_id: User ID (optional)
        """
        if not self.connected:
            print(f"[MongoDB] Fallback: Activity '{activity_type}' not logged to database")
            return
        
        try:
            activity_log = {
                'activity_type': activity_type,
                'timestamp': datetime.utcnow(),
                'input_data': input_data or {},
                'result': result or {},
                'metadata': metadata or {},
                'user_id': user_id
            }
            
            logs_collection = self.db['activity_logs']
            logs_collection.insert_one(activity_log)
            print(f"[MongoDB] Activity '{activity_type}' logged successfully")
        except Exception as e:
            print(f"[MongoDB] Error logging activity: {e}")
    
    def get_user_activities(self, user_id: str, limit: int = 10) -> list:
        """
        Get user's recent activities
        
        Args:
            user_id: User ID
            limit: Number of activities to retrieve (default: 10)
        
        Returns:
            List of activities
        """
        if not self.connected:
            return []
        
        try:
            logs_collection = self.db['activity_logs']
            activities = list(logs_collection.find(
                {'user_id': user_id}
            ).sort('timestamp', -1).limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for activity in activities:
                activity['_id'] = str(activity['_id'])
                activity['timestamp'] = activity['timestamp'].isoformat()
            
            return activities
        except Exception as e:
            print(f"[MongoDB] Error retrieving activities: {e}")
            return []
    
    def save_crop_recommendation(self, crop_name: str, input_params: Dict, 
                                  yield_prediction: float, user_id: str = None):
        """Save crop recommendation to database"""
        if not self.connected:
            return
        
        try:
            recommendations = self.db['crop_recommendations']
            recommendation = {
                'crop_name': crop_name,
                'input_params': input_params,
                'yield_prediction': yield_prediction,
                'user_id': user_id,
                'timestamp': datetime.utcnow()
            }
            recommendations.insert_one(recommendation)
        except Exception as e:
            print(f"[MongoDB] Error saving crop recommendation: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary from all logged activities"""
        if not self.connected:
            return {'status': 'offline'}
        
        try:
            logs_collection = self.db['activity_logs']
            
            # Count activities by type
            activities = list(logs_collection.aggregate([
                {
                    '$group': {
                        '_id': '$activity_type',
                        'count': {'$sum': 1}
                    }
                }
            ]))
            
            return {
                'status': 'ok',
                'total_activities': logs_collection.count_documents({}),
                'activities_by_type': activities
            }
        except Exception as e:
            print(f"[MongoDB] Error getting analytics: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("[MongoDB] Connection closed")


# Global MongoDB instance
_mongo_instance = None

def get_db() -> MongoDatabase:
    """Get or create MongoDB instance"""
    global _mongo_instance
    if _mongo_instance is None:
        _mongo_instance = MongoDatabase()
    return _mongo_instance

# Export mongo instance for global use
mongo = MongoDatabase()

# Export the get_db function for backward compatibility
__all__ = ['get_db', 'mongo', 'MongoDatabase']
