#!/usr/bin/env python3
"""
Test script for LinkedIn field extraction
This script tests the extraction of all LinkedIn fields from the Apify response.
"""

import json
from apify_controller import ApifyController

def test_linkedin_field_extraction():
    """Test LinkedIn field extraction with sample data"""
    print("🔍 Testing LinkedIn Field Extraction")
    print("=" * 50)
    
    try:
        # Load sample data from fields.json
        with open('docs/fields.json', 'r') as f:
            sample_data = json.load(f)
        
        print(f"✅ Loaded {len(sample_data)} sample profiles from fields.json")
        
        # Test extraction with the first profile
        if sample_data:
            sample_profile = sample_data[0]
            print(f"\n📋 Testing extraction with profile: {sample_profile.get('firstName', '')} {sample_profile.get('lastName', '')}")
            
            # Create a mock Apify controller to test extraction
            controller = ApifyController()
            
            # Test the extraction method
            extracted_data = controller._extract_professional_data(sample_profile, "Austin")
            
            if extracted_data:
                print("✅ Field extraction successful!")
                print(f"📊 Extracted {len(extracted_data)} fields")
                
                # Show key fields
                key_fields = [
                    'linkedinId', 'first_name', 'last_name', 'headline', 
                    'company', 'job_title', 'connectionsCount', 'followerCount',
                    'openToWork', 'premium', 'verified'
                ]
                
                print("\n🔑 Key Fields:")
                for field in key_fields:
                    value = extracted_data.get(field, 'N/A')
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:50] + "..."
                    print(f"  {field}: {value}")
                
                # Show array fields
                array_fields = ['experience', 'education', 'skills', 'languages', 'projects']
                print("\n📋 Array Fields:")
                for field in array_fields:
                    array_data = extracted_data.get(field, [])
                    print(f"  {field}: {len(array_data)} items")
                    if array_data and len(array_data) > 0:
                        if field == 'experience':
                            print(f"    - Latest: {array_data[0].get('position', 'N/A')} at {array_data[0].get('companyName', 'N/A')}")
                        elif field == 'skills':
                            print(f"    - First skill: {array_data[0].get('name', 'N/A')}")
                        elif field == 'languages':
                            print(f"    - First language: {array_data[0].get('language', 'N/A')}")
                
                return True
            else:
                print("❌ Field extraction failed")
                return False
        else:
            print("❌ No sample data found")
            return False
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_linkedin_field_extraction()
    if success:
        print("\n✅ LinkedIn field extraction test completed successfully")
    else:
        print("\n❌ LinkedIn field extraction test failed") 