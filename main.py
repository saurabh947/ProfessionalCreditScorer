#!/usr/bin/env python3
"""
Professional Finder Application
A Python application that finds professionals in US cities using Google Gemini AI and Apify
and stores the results in a local MongoDB database.
"""

import sys
import os
from typing import List, Dict

from database import DatabaseManager
from gemini_client import GeminiClient
from apify_controller import ApifyController
from display import DisplayManager
from config import Config

class ProfessionalFinder:
    """Main application class for finding and managing professional data"""
    
    def __init__(self):
        self.db_manager = None
        self.gemini_client = None
        self.apify_controller = None
        self.display_manager = DisplayManager()
        
        try:
            # Initialize database connection
            self.db_manager = DatabaseManager()
            
            # Initialize search clients based on configuration
            if Config.USE_APIFY and Config.APIFY_API_TOKEN:
                try:
                    self.apify_controller = ApifyController()
                    # Test API connection
                    if self.apify_controller.test_api_connection():
                        print("✅ Apify controller initialized successfully")
                        # Test actor availability
                        actor_id = "harvestapi~linkedin-profile-search"
                        if self.apify_controller.test_actor_availability(actor_id):
                            print("✅ Actor is available and accessible")
                        else:
                            print("⚠️  Actor is not available or accessible")
                            self.apify_controller = None
                    else:
                        print("⚠️  Apify controller initialized but API connection failed")
                        self.apify_controller = None
                except Exception as e:
                    print(f"⚠️  Failed to initialize Apify controller: {e}")
                    self.apify_controller = None
            
            if Config.GEMINI_API_KEY:
                try:
                    self.gemini_client = GeminiClient()
                    print("✅ Gemini client initialized successfully")
                except Exception as e:
                    print(f"⚠️  Failed to initialize Gemini client: {e}")
                    self.gemini_client = None
            
            if not self.apify_controller and not self.gemini_client:
                raise Exception("No search methods available. Please check your API keys.")
            
            print("🚀 Professional Finder Application initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize application: {e}")
            sys.exit(1)
    
    def search_professionals_in_city(self, city):
        """Search for professionals in a given city"""
        try:
            # Validate city input
            if not city or not city.strip():
                self.display_manager.display_error("City name cannot be empty")
                return
            
            city = city.strip().title()
            
            professionals = []
            search_methods_used = []
            
            # Try Apify if available
            if self.apify_controller and Config.USE_APIFY:
                try:
                    print(f"🔍 Searching with HarvestAPI LinkedIn Profile Search...")
                    apify_professionals = self.apify_controller.search_professionals_with_linkedin_scraper(
                        city, 
                        max_results=Config.MAX_RESULTS
                    )
                    professionals.extend(apify_professionals)
                    search_methods_used.append("HarvestAPI LinkedIn Profile Search")
                        
                except Exception as e:
                    print(f"⚠️  Apify search failed: {e}")
            
            if not professionals:
                self.display_manager.display_warning(f"No professionals found in {city}")
                return
            
            # Remove duplicates based on name and company
            unique_professionals = self._remove_duplicates(professionals)
            
            # Save professionals to database
            saved_count = 0
            for professional in unique_professionals:
                professional['city'] = city.lower()  # Normalize city name
                unique_id = self.db_manager.save_professional(professional)
                if unique_id:
                    saved_count += 1
            
            # Display results
            self.display_manager.display_professionals_table(unique_professionals, city)
            self.display_manager.display_search_summary(city, len(unique_professionals), saved_count)
            
            # Show search methods used
            if search_methods_used:
                print(f"\n🔍 Search methods used: {', '.join(search_methods_used)}")
            
        except Exception as e:
            self.display_manager.display_error(f"Error searching for professionals: {e}")
    
    def _remove_duplicates(self, professionals):
        """Remove duplicate professionals based on name and company"""
        seen = set()
        unique_professionals = []
        
        for prof in professionals:
            # Create a key based on name and company with safe string conversion
            first_name = str(prof.get('first_name', '')).lower()
            last_name = str(prof.get('last_name', '')).lower()
            company = str(prof.get('company', '')).lower()
            
            key = f"{first_name}_{last_name}_{company}"
            
            if key not in seen:
                seen.add(key)
                unique_professionals.append(prof)
        
        return unique_professionals
    
    def view_all_professionals(self):
        """View all professionals in the database"""
        try:
            professionals = self.db_manager.get_all_professionals()
            
            if not professionals:
                self.display_manager.display_warning("No professionals found in database")
                return
            
            # Group by city for better display
            cities = {}
            for prof in professionals:
                city = prof.get('city', 'Unknown').title()
                if city not in cities:
                    cities[city] = []
                cities[city].append(prof)
            
            for city, city_professionals in cities.items():
                self.display_manager.display_professionals_table(city_professionals, city)
            
        except Exception as e:
            self.display_manager.display_error(f"Error retrieving professionals: {e}")
    
    def view_professionals_by_city(self, city):
        """View professionals from a specific city"""
        try:
            if not city or not city.strip():
                self.display_manager.display_error("City name cannot be empty")
                return
            
            city = city.strip().lower()
            professionals = self.db_manager.get_professionals_by_city(city)
            
            if not professionals:
                self.display_manager.display_warning(f"No professionals found in {city.title()}")
                return
            
            self.display_manager.display_professionals_table(professionals, city.title())
            
        except Exception as e:
            self.display_manager.display_error(f"Error retrieving professionals: {e}")
    
    def get_last_run_dataset(self):
        """Get and save the last run's dataset"""
        try:
            if not self.apify_controller:
                self.display_manager.display_error("Apify controller not available")
                return
            
            print(f"🔍 Getting last run dataset...")
            
            # Get last run info first
            actor_id = "harvestapi~linkedin-profile-search"
            last_run_info = self.apify_controller.get_last_run_info(actor_id)
            
            if not last_run_info:
                self.display_manager.display_warning("No successful last run found")
                return
            
            print(f"✅ Found last run: {last_run_info.get('id', 'Unknown')}")
            print(f"✅ Last run started: {last_run_info.get('startedAt', 'Unknown')}")
            print(f"✅ Last run finished: {last_run_info.get('finishedAt', 'Unknown')}")
            
            # Get the dataset from the last run
            results = self.apify_controller.get_last_run_dataset(actor_id, max_results=Config.MAX_RESULTS)
            
            if not results:
                self.display_manager.display_warning("No results found in last run dataset")
                return
            
            # Transform results to our format (without city parameter)
            professionals = self._transform_results_from_last_run(results)
            
            if not professionals:
                self.display_manager.display_warning("No professionals found in last run dataset")
                return
            
            # Remove duplicates based on linkedinId
            unique_professionals = self._remove_duplicates(professionals)
            
            # Save professionals to database
            saved_count = 0
            for professional in unique_professionals:
                unique_id = self.db_manager.save_professional(professional)
                if unique_id:
                    saved_count += 1
            
            # Display results
            self.display_manager.display_professionals_table(unique_professionals, "Last Run Dataset")
            self.display_manager.display_search_summary("Last Run Dataset", len(unique_professionals), saved_count)
            
            print(f"\n🔍 Source: Last successful Apify run dataset")
            
        except Exception as e:
            self.display_manager.display_error(f"Error getting last run dataset: {e}")
    
    def _transform_results_from_last_run(self, results: List[Dict]) -> List[Dict]:
        """Transform results from last run without requiring city input"""
        professionals = []
        
        for i, result in enumerate(results):
            try:
                print(f"🔍 Processing result {i+1}/{len(results)}")
                
                # Extract city from the result data if available
                city = self._extract_city_from_result(result)
                print(f"📍 Extracted city: '{city}' (type: {type(city)})")
                
                # Handle different result formats from different actors
                professional = self.apify_controller._extract_professional_data(result, city)
                if professional:
                    professionals.append(professional)
                    print(f"✅ Successfully processed professional: {professional.get('first_name', 'N/A')} {professional.get('last_name', 'N/A')}")
                else:
                    print(f"⚠️  Failed to extract professional data from result {i+1}")
            except Exception as e:
                print(f"⚠️  Error transforming result {i+1}: {e}")
                continue
        
        return professionals
    
    def _extract_city_from_result(self, result: Dict) -> str:
        """Extract city information from a result item"""
        try:
            # Try to get city from location data if available
            location = result.get('location', {})
            if location:
                # Try parsed location first
                parsed_location = location.get('parsed', {})
                if parsed_location and parsed_location.get('city'):
                    city = parsed_location.get('city')
                    if city and isinstance(city, str):
                        return city
                
                # Try linkedin text
                linkedin_text = location.get('linkedinText')
                if linkedin_text and isinstance(linkedin_text, str):
                    return linkedin_text
            
            # Try to get city from current position
            current_position = result.get('currentPosition', [])
            if current_position and len(current_position) > 0:
                pos_location = current_position[0].get('location')
                if pos_location and isinstance(pos_location, str):
                    return pos_location
            
            # Try to get city from experience
            experience = result.get('experience', [])
            if experience and len(experience) > 0:
                exp_location = experience[0].get('location')
                if exp_location and isinstance(exp_location, str):
                    return exp_location
            
            # Default fallback
            return 'unknown'
            
        except Exception as e:
            print(f"⚠️  Error extracting city from result: {e}")
            return 'unknown'
    
    def run_interactive_mode(self):
        """Run the application in interactive mode"""
        while True:
            try:
                self.display_manager.display_menu()
                choice = input("\nEnter your choice (1-6): ").strip()
                
                if choice == '1':
                    city = input("Enter city name: ").strip()
                    self.search_professionals_in_city(city)
                
                elif choice == '2':
                    self.view_all_professionals()
                
                elif choice == '3':
                    city = input("Enter city name: ").strip()
                    self.view_professionals_by_city(city)
                
                elif choice == '4':
                    self.display_manager.display_database_stats(self.db_manager)
                
                elif choice == '5':
                    self.get_last_run_dataset()
                
                elif choice == '6':
                    print("\n👋 Thank you for using Professional Finder!")
                    break
                
                else:
                    self.display_manager.display_error("Invalid choice. Please enter 1-6.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Application interrupted. Goodbye!")
                break
            except Exception as e:
                self.display_manager.display_error(f"Unexpected error: {e}")
    
    def run_command_line_mode(self, city):
        """Run the application in command line mode"""
        try:
            self.search_professionals_in_city(city)
        except Exception as e:
            self.display_manager.display_error(f"Error in command line mode: {e}")
    
    def cleanup(self):
        """Clean up resources"""
        if self.db_manager:
            self.db_manager.close()

def main():
    """Main entry point of the application"""
    print("🏢 Professional Finder Application")
    print("=" * 50)
    
    # Check if running in command line mode
    if len(sys.argv) > 1:
        city = sys.argv[1]
        app = ProfessionalFinder()
        try:
            app.run_command_line_mode(city)
        finally:
            app.cleanup()
    else:
        # Interactive mode
        app = ProfessionalFinder()
        try:
            app.run_interactive_mode()
        finally:
            app.cleanup()

if __name__ == "__main__":
    main() 