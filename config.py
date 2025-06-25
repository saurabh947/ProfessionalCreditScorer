import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Google Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = 'professional_finder'
    COLLECTION_NAME = 'professionals'
    
    # Application settings
    MAX_RESULTS = 10
    US_CITIES_ONLY = True 