#!/usr/bin/env python3
"""
Test script for last run dataset functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apify_controller import ApifyController
from config import Config

def test_last_run_functionality():
    """Test the last run dataset functionality"""
    print("🧪 Testing Last Run Dataset Functionality")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Apify controller
    apify_token = os.getenv('APIFY_TOKEN')
    if not apify_token:
        print("❌ APIFY_TOKEN not found in environment variables")
        return False
    
    controller = ApifyController(apify_token)
    
    # Test actor ID
    actor_id = "harvestapi~linkedin-profile-search"
    
    print(f"🔍 Testing with actor ID: {actor_id}")
    
    # Test 1: Get last run info
    print("\n📋 Test 1: Getting last run info...")
    last_run_info = controller.get_last_run_info(actor_id)
    
    if last_run_info:
        print("✅ Last run info retrieved successfully")
        print(f"   Run ID: {last_run_info.get('id', 'Unknown')}")
        print(f"   Status: {last_run_info.get('status', 'Unknown')}")
        print(f"   Started: {last_run_info.get('startedAt', 'Unknown')}")
        print(f"   Finished: {last_run_info.get('finishedAt', 'Unknown')}")
    else:
        print("⚠️  No last run info found")
    
    # Test 2: Get last run dataset
    print("\n📊 Test 2: Getting last run dataset...")
    dataset_items = controller.get_last_run_dataset(actor_id, max_results=10)
    
    if dataset_items:
        print(f"✅ Last run dataset retrieved successfully")
        print(f"   Found {len(dataset_items)} items")
        
        # Show first item structure
        if dataset_items:
            first_item = dataset_items[0]
            print(f"   First item keys: {list(first_item.keys())}")
            print(f"   Sample data: {first_item.get('fullName', 'N/A')} - {first_item.get('headline', 'N/A')}")
    else:
        print("⚠️  No dataset items found")
    
    # Test 3: Test data transformation without city input
    print("\n💾 Test 3: Testing data transformation...")
    
    # Get some sample data first
    sample_data = controller.get_last_run_dataset(actor_id, max_results=5)
    
    if sample_data:
        print(f"✅ Sample data retrieved for transformation test")
        print(f"   Found {len(sample_data)} sample items")
        
        # Test city extraction from first item
        if sample_data:
            first_item = sample_data[0]
            print(f"   First item location data: {first_item.get('location', 'N/A')}")
            
            # Test if we can extract city from the data
            location = first_item.get('location', {})
            if location:
                parsed_location = location.get('parsed', {})
                if parsed_location and parsed_location.get('city'):
                    print(f"   Extracted city: {parsed_location.get('city')}")
                elif location.get('linkedinText'):
                    print(f"   Extracted location: {location.get('linkedinText')}")
                else:
                    print(f"   No city found in location data")
    else:
        print("⚠️  No sample data found for transformation test")
    
    print("\n✅ Last run functionality tests completed!")
    return True

if __name__ == "__main__":
    test_last_run_functionality() 