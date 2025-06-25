import requests
import json
import time
from typing import List, Dict, Optional
from config import Config

class ApifyController:
    """Controller for Apify API integration"""
    
    def __init__(self):
        if not Config.APIFY_API_TOKEN:
            raise ValueError("APIFY_API_TOKEN not found in environment variables")
        
        self.api_token = Config.APIFY_API_TOKEN
        self.base_url = "https://api.apify.com/v2"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def search_professionals_with_linkedin_scraper(self, city: str, max_results: int = 10) -> List[Dict]:
        """
        Search for professionals using HarvestAPI's LinkedIn Profile Search Actor
        Actor ID: harvestapi~linkedin-profile-search
        """
        actor_id = "harvestapi~linkedin-profile-search"
        
        # Ensure max_results is at least 10 (Apify actor requirement)
        max_results = max(10, max_results)
        
        # Prepare input for LinkedIn profile search (correct format)
        input_data = {
            "locations": [city],
            "maxItems": max_results
        }
        
        return self._run_actor_and_get_results(actor_id, input_data, max_results)
    
    def _run_actor_and_get_results(self, actor_id: str, input_data: Dict, max_results: int) -> List[Dict]:
        """Run an Apify actor and get the results"""
        try:
            print(f"🔍 Running Apify actor {actor_id} for {max_results} professionals in {input_data.get('location', 'the city')}...")
            
            # Start the actor run
            run_response = self._start_actor_run(actor_id, input_data)
            if not run_response:
                return []
            
            run_id = run_response.get('id')
            dataset_id = run_response.get('defaultDatasetId')
            
            print(f"🔍 Extracted run_id: {run_id}")
            print(f"🔍 Extracted dataset_id: {dataset_id}")
            
            if not run_id:
                print("❌ Failed to get run ID from Apify response")
                return []
            
            if not dataset_id:
                print("❌ Failed to get dataset ID from Apify response")
                print("❌ This might indicate the actor doesn't return a dataset")
                return []
            
            print(f"✅ Actor run started with ID: {run_id}")
            print(f"✅ Dataset ID for results: {dataset_id}")
            
            # Wait for the run to complete
            if not self._wait_for_run_completion(run_id):
                print("❌ Actor run did not complete successfully")
                return []
            
            # Get results from dataset
            results = self._get_dataset_items(dataset_id, max_results)
            
            if not results:
                print("⚠️  No results found in dataset")
                return []
            
            # Transform results to our format
            professionals = self._transform_results(results, input_data.get('location', ''))
            
            print(f"✅ Found {len(professionals)} professionals via Apify")
            return professionals
            
        except Exception as e:
            print(f"❌ Error running Apify actor: {e}")
            return []
    
    def _start_actor_run(self, actor_id: str, input_data: Dict) -> Optional[Dict]:
        """Start an Apify actor run"""
        try:
            url = f"{self.base_url}/acts/{actor_id}/runs"
            print(f"🔍 Making API call to: {url}")
            print(f"📤 Input data: {json.dumps(input_data, indent=2)}")
            
            response = requests.post(url, headers=self.headers, json=input_data)
            
            print(f"📥 Response status: {response.status_code}")
            
            if response.status_code == 201:
                response_data = response.json()
                print(f"✅ Actor run response: {json.dumps(response_data, indent=2)}")
                
                # Extract data from the response wrapper
                data = response_data.get('data', {})
                run_id = data.get('id')
                dataset_id = data.get('defaultDatasetId')
                
                if not run_id:
                    print("❌ No 'id' field found in response data")
                if not dataset_id:
                    print("❌ No 'defaultDatasetId' field found in response data")
                
                return data  # Return the data object, not the full response
            else:
                print(f"❌ Failed to start actor run: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting actor run: {e}")
            return None
    
    def _wait_for_run_completion(self, run_id: str, timeout: int = 300) -> bool:
        """Wait for an actor run to complete"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                url = f"{self.base_url}/actor-runs/{run_id}"
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    run_data = response.json()
                    print(f"📥 Run status response: {json.dumps(run_data, indent=2)}")
                    status = run_data.get('data', {}).get('status')
                    
                    if status == 'SUCCEEDED':
                        print("✅ Actor run completed successfully")
                        return True
                    elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                        print(f"❌ Actor run failed with status: {status}")
                        return False
                    else:
                        print(f"⏳ Actor run status: {status}")
                        time.sleep(10)  # Wait 10 seconds before checking again
                else:
                    print(f"❌ Failed to get run status: {response.status_code}")
                    print(f"❌ Response text: {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking run status: {e}")
                return False
        
        print("❌ Actor run timed out")
        return False
    
    def _get_dataset_items(self, dataset_id: str, max_results: int) -> List[Dict]:
        """Get items from an Apify dataset"""
        try:
            url = f"{self.base_url}/datasets/{dataset_id}/items"
            params = {
                'limit': max_results,
                'offset': 0
            }
            
            print(f"🔍 Fetching dataset items from: {url}")
            print(f"📤 Parameters: {params}")
            
            response = requests.get(url, headers=self.headers, params=params)
            
            print(f"📥 Dataset response status: {response.status_code}")
            print(f"📥 Dataset response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Dataset response: {json.dumps(response_data, indent=2)}")
                
                # Handle different response formats
                if isinstance(response_data, list):
                    # Direct array of items
                    items = response_data
                elif isinstance(response_data, dict):
                    # Response with data wrapper
                    items = response_data.get('data', [])
                    if not items:
                        items = response_data.get('items', [])
                else:
                    print(f"⚠️  Unexpected response format: {type(response_data)}")
                    items = []
                
                print(f"✅ Found {len(items)} items in dataset")
                return items
            else:
                print(f"❌ Failed to get dataset items: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting dataset items: {e}")
            return []
    
    def _transform_results(self, results: List[Dict], city: str) -> List[Dict]:
        """Transform Apify results to our professional format"""
        professionals = []
        
        for result in results:
            try:
                # Handle different result formats from different actors
                professional = self._extract_professional_data(result, city)
                if professional:
                    professionals.append(professional)
            except Exception as e:
                print(f"⚠️  Error transforming result: {e}")
                continue
        
        return professionals
    
    def _extract_professional_data(self, result: Dict, city: str) -> Optional[Dict]:
        """Extract professional data from a result item"""
        try:
            # Try HarvestAPI LinkedIn format first
            if 'fullName' in result:
                name_parts = result['fullName'].split(' ', 1)
                return {
                    'first_name': name_parts[0] if name_parts else '',
                    'last_name': name_parts[1] if len(name_parts) > 1 else '',
                    'company': result.get('company', 'Unknown'),
                    'job_title': result.get('jobTitle', 'Professional'),
                    'city': city.lower(),
                    'source': 'HarvestAPI LinkedIn'
                }
            
            # Try alternative name formats
            elif 'name' in result:
                name_parts = result['name'].split(' ', 1)
                return {
                    'first_name': name_parts[0] if name_parts else '',
                    'last_name': name_parts[1] if len(name_parts) > 1 else '',
                    'company': result.get('company', 'Unknown'),
                    'job_title': result.get('title', 'Professional'),
                    'city': city.lower(),
                    'source': 'HarvestAPI LinkedIn'
                }
            
            # Try first_name/last_name format
            elif 'first_name' in result or 'firstName' in result:
                first_name = result.get('first_name') or result.get('firstName', '')
                last_name = result.get('last_name') or result.get('lastName', '')
                return {
                    'first_name': first_name,
                    'last_name': last_name,
                    'company': result.get('company', 'Unknown'),
                    'job_title': result.get('job_title') or result.get('title', 'Professional'),
                    'city': city.lower(),
                    'source': 'HarvestAPI LinkedIn'
                }
            
            return None
            
        except Exception as e:
            print(f"⚠️  Error extracting professional data: {e}")
            return None
    
    def test_actor_availability(self, actor_id: str) -> bool:
        """Test if an actor is available and accessible"""
        try:
            url = f"{self.base_url}/acts/{actor_id}"
            print(f"🔍 Testing actor availability: {url}")
            
            response = requests.get(url, headers=self.headers)
            
            print(f"📥 Actor test response status: {response.status_code}")
            
            if response.status_code == 200:
                actor_data = response.json()
                print(f"✅ Actor found: {actor_data.get('name', 'Unknown')}")
                print(f"✅ Actor version: {actor_data.get('versionNumber', 'Unknown')}")
                return True
            else:
                print(f"❌ Actor not found or not accessible: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing actor availability: {e}")
            return False
    
    def test_api_connection(self) -> bool:
        """Test Apify API connection by getting user info"""
        try:
            url = f"{self.base_url}/users/me"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Apify API connection successful - User: {user_data.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Apify API connection failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing Apify API connection: {e}")
            return False
    
    def test_dataset_access(self, dataset_id: str) -> bool:
        """Test if we can access a specific dataset"""
        try:
            url = f"{self.base_url}/datasets/{dataset_id}"
            print(f"🔍 Testing dataset access: {url}")
            
            response = requests.get(url, headers=self.headers)
            
            print(f"📥 Dataset test response status: {response.status_code}")
            
            if response.status_code == 200:
                dataset_data = response.json()
                print(f"✅ Dataset found: {dataset_data.get('name', 'Unknown')}")
                print(f"✅ Dataset item count: {dataset_data.get('itemCount', 'Unknown')}")
                return True
            else:
                print(f"❌ Dataset not found or not accessible: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing dataset access: {e}")
            return False
    
    def get_available_actors(self) -> List[Dict]:
        """Get list of available actors for professional search"""
        return [
            {
                'id': 'harvestapi~linkedin-profile-search',
                'name': 'HarvestAPI LinkedIn Profile Search',
                'description': 'Searches LinkedIn profiles for professional information'
            }
        ] 