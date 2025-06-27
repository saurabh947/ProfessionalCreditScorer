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
            "maxItems": max_results,
            "profileScraperMode": "Full ($8 per 1k)"
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
                print(f"✅ Actor run started successfully")
                
                # Extract run_id and dataset_id
                run_id = response_data.get('data', {}).get('id')
                dataset_id = response_data.get('data', {}).get('defaultDatasetId')
                
                if not run_id:
                    print("❌ No 'id' field found in response data")
                if not dataset_id:
                    print("❌ No 'defaultDatasetId' field found in response data")
                
                return response_data
            else:
                print(f"❌ Failed to start actor run: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting actor run: {e}")
            return None
    
    def _wait_for_run_completion(self, run_id: str) -> bool:
        """Wait for an actor run to complete (no timeout)"""
        while True:
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
                print(f"✅ Dataset items retrieved successfully")
                
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
            # Ensure city is a string
            if not isinstance(city, str):
                city = str(city) if city is not None else 'unknown'
            
            # Extract basic information
            professional = {
                'linkedinId': result.get('id'),
                'publicIdentifier': result.get('publicIdentifier'),
                'first_name': result.get('firstName', ''),
                'last_name': result.get('lastName', ''),
                'headline': result.get('headline', ''),
                'about': result.get('about', ''),
                'linkedinUrl': result.get('linkedinUrl', ''),
                'openToWork': result.get('openToWork', False),
                'hiring': result.get('hiring', False),
                'premium': result.get('premium', False),
                'influencer': result.get('influencer', False),
                'photo': result.get('photo', ''),
                'verified': result.get('verified', False),
                'registeredAt': result.get('registeredAt'),
                'connectionsCount': result.get('connectionsCount'),
                'followerCount': result.get('followerCount'),
                'topSkills': result.get('topSkills', ''),
                'city': city.lower() if city else 'unknown',
                'source': 'HarvestAPI LinkedIn'
            }
            
            # Extract location information
            location = result.get('location', {})
            if location:
                professional['location_linkedinText'] = location.get('linkedinText')
                professional['location_countryCode'] = location.get('countryCode')
                parsed_location = location.get('parsed', {})
                if parsed_location:
                    professional['location_parsed_text'] = parsed_location.get('text')
                    professional['location_parsed_countryCode'] = parsed_location.get('countryCode')
                    professional['location_parsed_regionCode'] = parsed_location.get('regionCode')
                    professional['location_parsed_country'] = parsed_location.get('country')
                    professional['location_parsed_countryFull'] = parsed_location.get('countryFull')
                    professional['location_parsed_state'] = parsed_location.get('state')
                    professional['location_parsed_city'] = parsed_location.get('city')
            
            # Extract current position
            current_position = result.get('currentPosition', [])
            if current_position:
                current_pos = current_position[0] if current_position else {}
                professional['currentPosition_companyName'] = current_pos.get('companyName')
                professional['currentPosition_company'] = current_pos.get('company')
            
            # Extract experience (most recent first)
            experience = result.get('experience', [])
            if experience:
                # Get the most recent experience for basic fields
                latest_exp = experience[0] if experience else {}
                professional['job_title'] = latest_exp.get('position', 'Professional')
                professional['company'] = latest_exp.get('companyName', 'Unknown')
                professional['employmentType'] = latest_exp.get('employmentType')
                professional['workplaceType'] = latest_exp.get('workplaceType')
                professional['experience_location'] = latest_exp.get('location')
                professional['experience_duration'] = latest_exp.get('duration')
                professional['experience_description'] = latest_exp.get('description')
                
                # Store all experience as a nested array
                professional['experience'] = experience
            
            # Extract education
            education = result.get('education', [])
            if education:
                professional['education'] = education
            
            # Extract certifications
            certifications = result.get('certifications', [])
            if certifications:
                professional['certifications'] = certifications
            
            # Extract received recommendations
            received_recommendations = result.get('receivedRecommendations', [])
            if received_recommendations:
                professional['receivedRecommendations'] = received_recommendations
            
            # Extract skills
            skills = result.get('skills', [])
            if skills:
                professional['skills'] = skills
            
            # Extract languages
            languages = result.get('languages', [])
            if languages:
                professional['languages'] = languages
            
            # Extract projects
            projects = result.get('projects', [])
            if projects:
                professional['projects'] = projects
            
            # Extract publications
            publications = result.get('publications', [])
            if publications:
                professional['publications'] = publications
            
            # Extract more profiles (connections)
            more_profiles = result.get('moreProfiles', [])
            if more_profiles:
                professional['moreProfiles'] = more_profiles
            
            return professional
            
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
    
    def get_last_run_dataset(self, actor_id: str, max_results: int = 2500) -> List[Dict]:
        """
        Get the dataset from the last successful run of an actor
        Uses the /v2/acts/{actorId}/runs/last/dataset/items endpoint
        """
        try:
            print(f"🔍 Getting last run dataset for actor: {actor_id}")
            
            # Get the last successful run's dataset
            url = f"{self.base_url}/acts/{actor_id}/runs/last/dataset/items"
            params = {
                'limit': max_results,
                'offset': 0,
                'status': 'SUCCEEDED'  # Only get data from successful runs
            }
            
            print(f"🔍 Fetching last run dataset from: {url}")
            print(f"📤 Parameters: {params}")
            
            response = requests.get(url, headers=self.headers, params=params)
            
            print(f"📥 Last run dataset response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Last run dataset response received successfully")
                
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
                
                print(f"✅ Found {len(items)} items in last run dataset")
                return items
            else:
                print(f"❌ Failed to get last run dataset: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting last run dataset: {e}")
            return []
    
    def get_last_run_info(self, actor_id: str) -> Optional[Dict]:
        """
        Get information about the last run of an actor
        Uses the /v2/acts/{actorId}/runs/last endpoint
        """
        try:
            print(f"🔍 Getting last run info for actor: {actor_id}")
            
            url = f"{self.base_url}/acts/{actor_id}/runs/last"
            params = {
                'status': 'SUCCEEDED'  # Only get successful runs
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            print(f"📥 Last run info response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Last run info retrieved successfully")
                
                # Extract data from the response wrapper
                data = response_data.get('data', {})
                return data
            else:
                print(f"❌ Failed to get last run info: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting last run info: {e}")
            return None
    
    def save_last_run_dataset(self, actor_id: str, city: str, max_results: int = 2500) -> List[Dict]:
        """
        Get the last run dataset and save the professionals to the database
        """
        try:
            # Validate city parameter
            if not city or not city.strip():
                print("❌ City parameter cannot be empty")
                return []
            
            city = city.strip()
            print(f"🔍 Getting and saving last run dataset for {city}...")
            
            # Get the dataset from the last run
            results = self.get_last_run_dataset(actor_id, max_results)
            
            if not results:
                print("⚠️  No results found in last run dataset")
                return []
            
            # Transform results to our format
            professionals = self._transform_results(results, city)
            
            print(f"✅ Found {len(professionals)} professionals from last run dataset")
            return professionals
            
        except Exception as e:
            print(f"❌ Error saving last run dataset: {e}")
            return [] 