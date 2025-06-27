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
            self.collection.create_index("linkedinId")  # Add index for LinkedIn ID
            self.collection.create_index("city")
            self.collection.create_index("company")
            self.collection.create_index("source")  # Add index for source field
            
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
            
            # Ensure source field is present
            if 'source' not in professional_data:
                professional_data['source'] = 'Unknown'
            
            # Ensure all string fields are properly converted to strings
            string_fields = ['first_name', 'last_name', 'company', 'city', 'headline', 'job_title']
            for field in string_fields:
                if field in professional_data:
                    if professional_data[field] is None:
                        professional_data[field] = ''
                    else:
                        professional_data[field] = str(professional_data[field])
            
            # Check if professional already exists (based on linkedinId if available, otherwise name and company)
            if 'linkedinId' in professional_data and professional_data['linkedinId']:
                existing = self.collection.find_one({'linkedinId': professional_data['linkedinId']})
            else:
                existing = self.collection.find_one({
                    'first_name': professional_data.get('first_name', ''),
                    'last_name': professional_data.get('last_name', ''),
                    'company': professional_data.get('company', ''),
                    'city': professional_data.get('city', '')
                })
            
            if existing:
                print(f"⚠️  Professional {professional_data.get('first_name', '')} {professional_data.get('last_name', '')} already exists")
                return existing['unique_id']
            
            # Insert new professional
            result = self.collection.insert_one(professional_data)
            return professional_data['unique_id']
            
        except Exception as e:
            print(f"❌ Error saving professional: {e}")
            return None
    
    def get_professionals_by_city(self, city):
        """Get all professionals from a specific city"""
        try:
            # Validate city parameter
            if not city or not isinstance(city, str):
                print("⚠️  Invalid city parameter provided")
                return []
            
            professionals = list(self.collection.find({'city': city.lower()}))
            return professionals
        except Exception as e:
            print(f"❌ Error retrieving professionals: {e}")
            return []
    
    def get_professionals_by_source(self, source):
        """Get all professionals from a specific source"""
        try:
            professionals = list(self.collection.find({'source': source}))
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
    
    def get_statistics(self):
        """Get database statistics"""
        try:
            total_professionals = self.collection.count_documents({})
            
            # Get unique cities
            cities = self.collection.distinct('city')
            
            # Get unique sources
            sources = self.collection.distinct('source')
            
            # Get counts by source
            source_counts = {}
            for source in sources:
                count = self.collection.count_documents({'source': source})
                source_counts[source] = count
            
            return {
                'total_professionals': total_professionals,
                'unique_cities': len(cities),
                'unique_sources': len(sources),
                'source_counts': source_counts,
                'cities': cities
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Database connection closed") 