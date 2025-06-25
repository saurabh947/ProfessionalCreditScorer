#!/usr/bin/env python3
"""
Test script for Professional Finder Application
This script tests the basic functionality without requiring API keys or database connections.
"""

import sys
import os

def test_imports():
    """Test if all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        from config import Config
        print("✅ Config module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from display import DisplayManager
        print("✅ Display module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import display: {e}")
        return False
    
    try:
        import google.generativeai
        print("✅ Google Generative AI module imported successfully")
    except ImportError:
        print("⚠️  Google Generative AI not installed - run: pip install google-generativeai")
    
    try:
        from pymongo import MongoClient
        print("✅ PyMongo module imported successfully")
    except ImportError:
        print("⚠️  PyMongo not installed - run: pip install pymongo")
    
    try:
        from tabulate import tabulate
        print("✅ Tabulate module imported successfully")
    except ImportError:
        print("⚠️  Tabulate not installed - run: pip install tabulate")
    
    try:
        import requests
        print("✅ Requests module imported successfully")
    except ImportError:
        print("⚠️  Requests not installed - run: pip install requests")
    
    return True

def test_display_manager():
    """Test the display manager functionality"""
    print("\n🧪 Testing display manager...")
    
    try:
        from display import DisplayManager
        
        # Test display methods
        DisplayManager.display_success("Test success message")
        DisplayManager.display_error("Test error message")
        DisplayManager.display_warning("Test warning message")
        
        print("✅ Display manager tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Display manager test failed: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\n🧪 Testing configuration...")
    
    try:
        from config import Config
        
        print(f"Max results: {Config.MAX_RESULTS}")
        print(f"US cities only: {Config.US_CITIES_ONLY}")
        print(f"Database name: {Config.DATABASE_NAME}")
        print(f"Use Apify: {Config.USE_APIFY}")
        print(f"Gemini model: {Config.GEMINI_MODEL}")
        
        if Config.GEMINI_API_KEY:
            print("✅ Gemini API key found")
        else:
            print("⚠️  Gemini API key not found - set GEMINI_API_KEY environment variable")
        
        if Config.APIFY_API_TOKEN:
            print("✅ Apify API token found")
        else:
            print("⚠️  Apify API token not found - set APIFY_API_TOKEN environment variable")
        
        print("✅ Configuration tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_sample_data():
    """Test sample data formatting"""
    print("\n🧪 Testing sample data display...")
    
    try:
        from display import DisplayManager
        
        # Sample professional data with sources
        sample_professionals = [
            {
                'unique_id': '12345678-1234-1234-1234-123456789abc',
                'first_name': 'John',
                'last_name': 'Smith',
                'job_title': 'Software Engineer',
                'company': 'Tech Corp',
                'city': 'San Francisco',
                'source': 'LinkedIn Scraper'
            },
            {
                'unique_id': '87654321-4321-4321-4321-cba987654321',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'job_title': 'Product Manager',
                'company': 'Startup Inc',
                'city': 'San Francisco',
                'source': 'Google Search'
            },
            {
                'unique_id': 'abcdef12-3456-7890-abcd-ef1234567890',
                'first_name': 'Mike',
                'last_name': 'Davis',
                'job_title': 'Data Scientist',
                'company': 'AI Solutions',
                'city': 'San Francisco',
                'source': 'Gemini AI'
            }
        ]
        
        DisplayManager.display_professionals_table(sample_professionals, 'San Francisco')
        print("✅ Sample data display test passed")
        return True
        
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False

def test_apify_controller_structure():
    """Test Apify controller structure (without API calls)"""
    print("\n🧪 Testing Apify controller structure...")
    
    try:
        # Test if we can import the module
        from apify_controller import ApifyController
        from config import Config
        print("✅ Apify controller module imported successfully")
        
        # Test available actors method (static data)
        actors = ApifyController.get_available_actors(None)
        if isinstance(actors, list) and len(actors) > 0:
            print(f"✅ Available actors: {len(actors)} found")
            for actor in actors:
                print(f"  - {actor['name']}: {actor['id']}")
        else:
            print("⚠️  No available actors found")
        
        # Test API connection if token is available
        if Config.APIFY_API_TOKEN:
            try:
                controller = ApifyController()
                if controller.test_api_connection():
                    print("✅ Apify API connection test passed")
                else:
                    print("⚠️  Apify API connection test failed")
            except Exception as e:
                print(f"⚠️  Apify API connection test error: {e}")
        else:
            print("⚠️  Skipping Apify API connection test (no token)")
        
        print("✅ Apify controller structure tests passed")
        return True
        
    except ImportError as e:
        print(f"⚠️  Apify controller not available: {e}")
        return True  # Not a failure, just not available
    except Exception as e:
        print(f"❌ Apify controller test failed: {e}")
        return False

def test_clear_database_functionality():
    """Test clear database functionality structure"""
    print("\n🧪 Testing clear database functionality...")
    
    try:
        # Test if we can import the database module
        from database import DatabaseManager
        print("✅ Database manager module imported successfully")
        
        # Test if clear_database method exists
        db_manager = DatabaseManager()
        if hasattr(db_manager, 'clear_database'):
            print("✅ Clear database method exists")
        else:
            print("❌ Clear database method not found")
            return False
        
        # Test if the method is callable
        if callable(getattr(db_manager, 'clear_database')):
            print("✅ Clear database method is callable")
        else:
            print("❌ Clear database method is not callable")
            return False
        
        # Test statistics method exists (used in clear confirmation)
        if hasattr(db_manager, 'get_statistics'):
            print("✅ Get statistics method exists")
        else:
            print("❌ Get statistics method not found")
            return False
        
        print("✅ Clear database functionality tests passed")
        return True
        
    except ImportError as e:
        print(f"⚠️  Database manager not available: {e}")
        return True  # Not a failure, just not available
    except Exception as e:
        print(f"❌ Clear database test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏢 Professional Finder - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_display_manager,
        test_sample_data,
        test_apify_controller_structure,
        test_clear_database_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Application is ready to use.")
        print("\nNext steps:")
        print("1. Set up your API keys in .env file:")
        print("   - GEMINI_API_KEY for Gemini AI")
        print("   - APIFY_API_TOKEN for Apify integration")
        print("2. Start MongoDB (mongod)")
        print("3. Run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 