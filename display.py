import pandas as pd
from tabulate import tabulate
from datetime import datetime

class DisplayManager:
    """Manages the display and formatting of professional data"""
    
    @staticmethod
    def display_professionals_table(professionals, city):
        """Display professionals in a formatted table"""
        if not professionals:
            print(f"\n❌ No professionals found in {city}")
            return
        
        # Prepare data for tabulation
        table_data = []
        for prof in professionals:
            table_data.append([
                prof.get('unique_id', 'N/A')[:8] + '...',  # Truncate UUID for display
                prof.get('first_name', 'N/A'),
                prof.get('last_name', 'N/A'),
                prof.get('job_title', 'N/A'),
                prof.get('company', 'N/A'),
                prof.get('city', 'N/A')
            ])
        
        # Create table
        headers = ['ID', 'First Name', 'Last Name', 'Job Title', 'Company', 'City']
        table = tabulate(table_data, headers=headers, tablefmt='grid', showindex=False)
        
        print(f"\n📊 Professionals in {city}:")
        print("=" * 80)
        print(table)
        print(f"\nTotal professionals found: {len(professionals)}")
    
    @staticmethod
    def display_professional_details(professional):
        """Display detailed information about a single professional"""
        print("\n" + "=" * 50)
        print("👤 PROFESSIONAL DETAILS")
        print("=" * 50)
        print(f"ID: {professional.get('unique_id', 'N/A')}")
        print(f"Name: {professional.get('first_name', 'N/A')} {professional.get('last_name', 'N/A')}")
        print(f"Job Title: {professional.get('job_title', 'N/A')}")
        print(f"Company: {professional.get('company', 'N/A')}")
        print(f"City: {professional.get('city', 'N/A')}")
        
        if 'created_at' in professional:
            created_at = professional['created_at']
            if isinstance(created_at, datetime):
                print(f"Added: {created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"Added: {created_at}")
        print("=" * 50)
    
    @staticmethod
    def display_search_summary(city, total_found, saved_count):
        """Display a summary of the search operation"""
        print("\n" + "=" * 60)
        print("🔍 SEARCH SUMMARY")
        print("=" * 60)
        print(f"City searched: {city}")
        print(f"Professionals found: {total_found}")
        print(f"Professionals saved to database: {saved_count}")
        print("=" * 60)
    
    @staticmethod
    def display_database_stats(db_manager):
        """Display database statistics"""
        try:
            all_professionals = db_manager.get_all_professionals()
            
            if not all_professionals:
                print("\n📊 Database is empty")
                return
            
            # Group by city
            cities = {}
            for prof in all_professionals:
                city = prof.get('city', 'Unknown')
                if city not in cities:
                    cities[city] = 0
                cities[city] += 1
            
            print("\n📊 DATABASE STATISTICS")
            print("=" * 40)
            print(f"Total professionals: {len(all_professionals)}")
            print("\nProfessionals by city:")
            
            for city, count in sorted(cities.items()):
                print(f"  {city}: {count}")
            
            print("=" * 40)
            
        except Exception as e:
            print(f"❌ Error displaying database stats: {e}")
    
    @staticmethod
    def display_menu():
        """Display the main menu"""
        print("\n" + "=" * 50)
        print("🏢 PROFESSIONAL FINDER")
        print("=" * 50)
        print("1. Search for professionals in a city")
        print("2. View all professionals in database")
        print("3. View professionals by city")
        print("4. View database statistics")
        print("5. Exit")
        print("=" * 50)
    
    @staticmethod
    def display_error(message):
        """Display error messages"""
        print(f"\n❌ ERROR: {message}")
    
    @staticmethod
    def display_success(message):
        """Display success messages"""
        print(f"\n✅ {message}")
    
    @staticmethod
    def display_warning(message):
        """Display warning messages"""
        print(f"\n⚠️  {message}") 