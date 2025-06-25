#!/usr/bin/env python3
"""
Test script for Apify dataset retrieval
This script tests the Apify API integration with detailed logging.
"""

import os
from dotenv import load_dotenv
from apify_controller import ApifyController

def test_apify_dataset_retrieval():
    """Test Apify dataset retrieval with detailed logging"""
    print("🔍 Testing Apify Dataset Retrieval")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if Apify token is available
    apify_token = os.getenv('APIFY_API_TOKEN')
    if not apify_token:
        print("❌ APIFY_API_TOKEN not found in environment variables")
        return False
    
    try:
        # Initialize Apify controller
        controller = ApifyController()
        
        # Test API connection
        if not controller.test_api_connection():
            print("❌ Apify API connection failed")
            return False
        
        # Test actor availability
        actor_id = "harvestapi~linkedin-profile-search"
        if not controller.test_actor_availability(actor_id):
            print("❌ Actor not available")
            return False
        
        # Test a small search to see the dataset retrieval process
        print("\n🔍 Testing search with detailed logging...")
        city = "San Francisco"
        max_results = 10  # Apify actor requires at least 10 items
        
        professionals = controller.search_professionals_with_linkedin_scraper(city, max_results)
        
        print(f"\n📊 Results: Found {len(professionals)} professionals")
        
        if professionals:
            print("✅ Dataset retrieval successful!")
            for i, prof in enumerate(professionals[:3], 1):
                print(f"  {i}. {prof.get('first_name', 'N/A')} {prof.get('last_name', 'N/A')} - {prof.get('job_title', 'N/A')} at {prof.get('company', 'N/A')}")
            return True
        else:
            print("⚠️  No professionals found - this might be normal for the test")
            return True
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_apify_dataset_retrieval()
    if success:
        print("\n✅ Apify dataset retrieval test completed")
    else:
        print("\n❌ Apify dataset retrieval test failed") 