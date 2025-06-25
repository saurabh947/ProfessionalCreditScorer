import google.generativeai as genai
import json
import re
from config import Config

class GeminiClient:
    """Client for interacting with Google Gemini AI"""
    
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def search_professionals(self, city, max_results=10):
        """Search for professionals in a given city using Gemini AI"""
        
        prompt = f"""
        You are a professional research assistant. I need you to find {max_results} real professionals who work and reside in {city}, USA.
        
        For each professional, provide the following information in a structured format:
        - First Name
        - Last Name  
        - Current Company/Organization
        - Job Title
        - City (should be {city})
        
        Please provide the results in the following JSON format:
        {{
            "professionals": [
                {{
                    "first_name": "John",
                    "last_name": "Doe",
                    "company": "Tech Corp",
                    "job_title": "Software Engineer",
                    "city": "{city}"
                }}
            ]
        }}
        
        Important guidelines:
        1. Only include real professionals who actually work in {city}
        2. Focus on diverse industries and roles
        3. Ensure all information is accurate and current
        4. If you cannot find enough real professionals, indicate this clearly
        5. Do not make up or fabricate information
        6. Only include US-based professionals
        
        Return only the JSON response, no additional text.
        """
        
        try:
            print(f"🔍 Searching for professionals in {city}...")
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            content = response.text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)
                
                professionals = data.get('professionals', [])
                
                # Validate and clean the data
                cleaned_professionals = []
                for prof in professionals:
                    if self._validate_professional(prof, city):
                        cleaned_professionals.append(prof)
                
                print(f"✅ Found {len(cleaned_professionals)} valid professionals in {city}")
                return cleaned_professionals[:max_results]
            
            else:
                print("❌ Could not parse JSON response from Gemini")
                return []
                
        except Exception as e:
            print(f"❌ Error searching for professionals: {e}")
            return []
    
    def _validate_professional(self, professional, expected_city):
        """Validate professional data"""
        required_fields = ['first_name', 'last_name', 'company', 'job_title', 'city']
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in professional or not professional[field]:
                return False
        
        # Check if city matches expected city
        if professional['city'].lower() != expected_city.lower():
            return False
        
        # Basic validation for names
        if len(professional['first_name']) < 2 or len(professional['last_name']) < 2:
            return False
        
        return True
    
    def get_professional_summary(self, city, professionals):
        """Generate a summary of professionals found in a city"""
        if not professionals:
            return f"No professionals found in {city}"
        
        summary = f"Found {len(professionals)} professionals in {city}:\n\n"
        
        for i, prof in enumerate(professionals, 1):
            summary += f"{i}. {prof['first_name']} {prof['last_name']} - {prof['job_title']} at {prof['company']}\n"
        
        return summary 