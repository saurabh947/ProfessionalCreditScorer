#!/usr/bin/env python3
"""
Professional Finder Application
A Python application that finds professionals in US cities using Google Gemini AI and Apify
and stores the results in a local MongoDB database.
"""

import sys
import os
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
            
            # Try Apify first if available
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
            
            # Fallback to Gemini if Apify failed or not configured
            if (not professionals or len(professionals) < Config.MAX_RESULTS) and self.gemini_client:
                try:
                    remaining = Config.MAX_RESULTS - len(professionals)
                    print(f"🔍 Searching with Gemini AI for {remaining} professionals...")
                    gemini_professionals = self.gemini_client.search_professionals(
                        city, 
                        max_results=remaining
                    )
                    professionals.extend(gemini_professionals)
                    search_methods_used.append("Gemini AI")
                    
                except Exception as e:
                    print(f"⚠️  Gemini search failed: {e}")
            
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
            # Create a key based on name and company
            key = f"{prof.get('first_name', '').lower()}_{prof.get('last_name', '').lower()}_{prof.get('company', '').lower()}"
            
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
    
    def show_search_methods(self):
        """Show available search methods and their status"""
        print("\n🔍 AVAILABLE SEARCH METHODS")
        print("=" * 40)
        
        if self.apify_controller:
            print("✅ Apify Integration: Available")
            actors = self.apify_controller.get_available_actors()
            for actor in actors:
                print(f"  - {actor['name']}: {actor['description']}")
        else:
            print("❌ Apify Integration: Not available (missing API token)")
        
        if self.gemini_client:
            print("✅ Gemini AI Integration: Available")
            print(f"  - Model: {Config.GEMINI_MODEL}")
        else:
            print("❌ Gemini AI Integration: Not available (missing API key)")
        
        print(f"📊 Current search method: {'Apify' if Config.USE_APIFY else 'Gemini AI'}")
        print("=" * 40)
    
    def clear_database(self):
        """Clear all records from the database"""
        try:
            # Get current statistics for confirmation
            stats = self.db_manager.get_statistics()
            total_records = stats.get('total_professionals', 0)
            
            if total_records == 0:
                self.display_manager.display_warning("Database is already empty")
                return
            
            # Show confirmation with record count
            print(f"\n⚠️  WARNING: This will permanently delete {total_records} records from the database!")
            print("This action cannot be undone.")
            
            confirmation = input("Type 'DELETE' to confirm, or press Enter to cancel: ").strip()
            
            if confirmation == 'DELETE':
                success = self.db_manager.clear_database()
                if success:
                    self.display_manager.display_success(f"Successfully cleared {total_records} records from database")
                else:
                    self.display_manager.display_error("Failed to clear database")
            else:
                print("🗑️  Database clear operation cancelled")
                
        except Exception as e:
            self.display_manager.display_error(f"Error clearing database: {e}")
    
    def run_interactive_mode(self):
        """Run the application in interactive mode"""
        while True:
            try:
                self.display_manager.display_menu()
                choice = input("\nEnter your choice (1-7): ").strip()
                
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
                    self.show_search_methods()
                
                elif choice == '6':
                    self.clear_database()
                
                elif choice == '7':
                    print("\n👋 Thank you for using Professional Finder!")
                    break
                
                else:
                    self.display_manager.display_error("Invalid choice. Please enter 1-7.")
                
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