import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the application"""
    
    # Google Gemini API configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')  # Default to Gemini 2.5 Flash
    
    # Apify API configuration
    APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN')
    
    # MongoDB configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = 'professional_finder'
    COLLECTION_NAME = 'professionals'
    
    # Application settings
    MAX_RESULTS = int(os.getenv('MAX_RESULTS', 2500))
    US_CITIES_ONLY = True
    USE_APIFY = os.getenv('USE_APIFY', 'true').lower() == 'true'  # Default to using Apify 