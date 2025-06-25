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
        
        if Config.GEMINI_API_KEY:
            print("✅ Gemini API key found")
        else:
            print("⚠️  Gemini API key not found - set GEMINI_API_KEY environment variable")
        
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
        
        # Sample professional data
        sample_professionals = [
            {
                'unique_id': '12345678-1234-1234-1234-123456789abc',
                'first_name': 'John',
                'last_name': 'Smith',
                'job_title': 'Software Engineer',
                'company': 'Tech Corp',
                'city': 'San Francisco'
            },
            {
                'unique_id': '87654321-4321-4321-4321-cba987654321',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'job_title': 'Product Manager',
                'company': 'Startup Inc',
                'city': 'San Francisco'
            }
        ]
        
        DisplayManager.display_professionals_table(sample_professionals, 'San Francisco')
        print("✅ Sample data display test passed")
        return True
        
    except Exception as e:
        print(f"❌ Sample data test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏢 Professional Finder - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_display_manager,
        test_sample_data
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
        print("1. Set up your GEMINI_API_KEY in .env file")
        print("2. Start MongoDB (mongod)")
        print("3. Run: python main.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 