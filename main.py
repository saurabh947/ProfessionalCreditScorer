#!/usr/bin/env python3
"""
Professional Finder Application
A Python application that finds professionals in US cities using Google Gemini AI
and stores the results in a local MongoDB database.
"""

import sys
import os
from database import DatabaseManager
from gemini_client import GeminiClient
from display import DisplayManager
from config import Config

class ProfessionalFinder:
    """Main application class for finding and managing professional data"""
    
    def __init__(self):
        self.db_manager = None
        self.gemini_client = None
        self.display_manager = DisplayManager()
        
        try:
            # Initialize database connection
            self.db_manager = DatabaseManager()
            
            # Initialize Gemini client
            self.gemini_client = GeminiClient()
            
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
            
            # Search for professionals using Gemini AI
            professionals = self.gemini_client.search_professionals(
                city, 
                max_results=Config.MAX_RESULTS
            )
            
            if not professionals:
                self.display_manager.display_warning(f"No professionals found in {city}")
                return
            
            # Save professionals to database
            saved_count = 0
            for professional in professionals:
                professional['city'] = city.lower()  # Normalize city name
                unique_id = self.db_manager.save_professional(professional)
                if unique_id:
                    saved_count += 1
            
            # Display results
            self.display_manager.display_professionals_table(professionals, city)
            self.display_manager.display_search_summary(city, len(professionals), saved_count)
            
        except Exception as e:
            self.display_manager.display_error(f"Error searching for professionals: {e}")
    
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
    
    def run_interactive_mode(self):
        """Run the application in interactive mode"""
        while True:
            try:
                self.display_manager.display_menu()
                choice = input("\nEnter your choice (1-5): ").strip()
                
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
                    print("\n👋 Thank you for using Professional Finder!")
                    break
                
                else:
                    self.display_manager.display_error("Invalid choice. Please enter 1-5.")
                
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