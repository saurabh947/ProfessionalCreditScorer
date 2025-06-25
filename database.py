from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import uuid
from datetime import datetime
from config import Config

class DatabaseManager:
    """Manages database operations for professional data"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB database"""
        try:
            self.client = MongoClient(Config.MONGODB_URI)
            # Test the connection
            self.client.admin.command('ping')
            print("✅ Successfully connected to MongoDB")
            
            self.db = self.client[Config.DATABASE_NAME]
            self.collection = self.db[Config.COLLECTION_NAME]
            
            # Create indexes for better performance
            self.collection.create_index("unique_id", unique=True)
            self.collection.create_index("city")
            self.collection.create_index("company")
            
        except ConnectionFailure as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def save_professional(self, professional_data):
        """Save a professional to the database"""
        try:
            # Generate unique ID if not provided
            if 'unique_id' not in professional_data:
                professional_data['unique_id'] = str(uuid.uuid4())
            
            # Add timestamp
            professional_data['created_at'] = datetime.utcnow()
            
            # Check if professional already exists (based on name and company)
            existing = self.collection.find_one({
                'first_name': professional_data['first_name'],
                'last_name': professional_data['last_name'],
                'company': professional_data['company'],
                'city': professional_data['city']
            })
            
            if existing:
                print(f"⚠️  Professional {professional_data['first_name']} {professional_data['last_name']} already exists")
                return existing['unique_id']
            
            # Insert new professional
            result = self.collection.insert_one(professional_data)
            print(f"✅ Saved professional: {professional_data['first_name']} {professional_data['last_name']}")
            return professional_data['unique_id']
            
        except Exception as e:
            print(f"❌ Error saving professional: {e}")
            return None
    
    def get_professionals_by_city(self, city):
        """Get all professionals from a specific city"""
        try:
            professionals = list(self.collection.find({'city': city.lower()}))
            return professionals
        except Exception as e:
            print(f"❌ Error retrieving professionals: {e}")
            return []
    
    def get_all_professionals(self):
        """Get all professionals from the database"""
        try:
            professionals = list(self.collection.find({}, {'_id': 0}))
            return professionals
        except Exception as e:
            print(f"❌ Error retrieving all professionals: {e}")
            return []
    
    def delete_professional(self, unique_id):
        """Delete a professional by unique ID"""
        try:
            result = self.collection.delete_one({'unique_id': unique_id})
            if result.deleted_count > 0:
                print(f"✅ Deleted professional with ID: {unique_id}")
                return True
            else:
                print(f"⚠️  No professional found with ID: {unique_id}")
                return False
        except Exception as e:
            print(f"❌ Error deleting professional: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Database connection closed") 