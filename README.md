# Professional Finder

A Python application that finds professionals in US cities using Google Gemini 2.5 Flash AI and Apify web scraping, storing the results in a local MongoDB database.

## Features

- 🔍 Search for professionals in any US city using Apify LinkedIn Profile Search
- 📊 Store and manage professional data in MongoDB
- 🎯 Duplicate detection and removal
- **Professional Search**: Search for professionals in US cities using Apify's LinkedIn Profile Search
- **Apify Integration**: Use Apify's LinkedIn Profile Search actor for comprehensive data
- **Last Run Dataset**: Retrieve and save data from the most recent successful Apify run
- **Database Storage**: Store results in MongoDB with deduplication
- **Rich Data**: Capture comprehensive LinkedIn profile information
- **Interactive Interface**: User-friendly command-line interface
- **Gemini AI Integration**: Available for other AI features (not used for professional search)

## Prerequisites

Before running this application, you need:

1. **Python 3.7+** installed on your system
2. **MongoDB** running locally (or a MongoDB connection string)
3. **Google Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. **Apify API Token** from [Apify Console](https://console.apify.com/account/integrations) (optional but recommended)

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `env_example.txt` to `.env`
   - Add your API keys:
     ```
     GEMINI_API_KEY=your_actual_gemini_api_key_here
     APIFY_API_TOKEN=your_actual_apify_api_token_here
     GEMINI_MODEL=gemini-2.0-flash-exp
     USE_APIFY=true
     ```

4. **Start MongoDB:**
   - If running locally: `mongod`
   - Or use a cloud MongoDB instance and update the `MONGODB_URI` in your `.env` file

## Usage

### Interactive Mode

Run the application and choose from the menu:

1. **Search for professionals in a city** - Use Apify to find professionals
2. **View all professionals in database** - Display all stored professionals
3. **View professionals by city** - Filter professionals by specific city
4. **View database statistics** - Show database metrics and counts
5. **Get last run's dataset** - Retrieve data from the most recent successful Apify run (no city input required)
6. **Exit** - Close the application

### Command Line Mode
Search for professionals in a specific city:
```bash
python main.py "San Francisco"
```

## Search Methods

The application uses Apify's LinkedIn Profile Search for finding professionals:

- **Apify LinkedIn Profile Search**: Searches LinkedIn profiles for professional information
  - Provides comprehensive profile data from real LinkedIn profiles
  - Requires Apify API token
  - Returns rich professional data including experience, education, skills, and more

## Database Management

The application provides comprehensive database management features:

### Viewing Data
- **View All Professionals**: Display all professionals in the database, grouped by city
- **View by City**: Filter and display professionals from a specific city
- **Database Statistics**: View summary statistics including total records, cities, and data sources

### Data Management
- **Database Statistics**: View summary statistics including total records, cities, and data sources

### Data Integrity
- **Duplicate Detection**: Automatically prevents duplicate entries based on name, company, and city
- **Unique IDs**: Each professional record gets a unique UUID identifier
- **Source Tracking**: All records include the data source (LinkedIn Scraper, Gemini AI, etc.)
- **Timestamps**: Records include creation timestamps for tracking

## Example Output

```
🏢 Professional Finder Application
==================================================

🔍 Searching with HarvestAPI LinkedIn Profile Search...
✅ Actor run started with ID: abc123def456
✅ Actor run completed successfully
✅ Found 8 professionals via Apify

📊 Professionals in San Francisco:
================================================================================
| ID        | First Name | Last Name  | Job Title           | Company        | City           | Source           |
|===========|============|============|=====================|================|================|==================|
| a1b2c3d4. | John       | Smith      | Software Engineer   | Tech Corp      | San Francisco  | HarvestAPI LinkedIn |
| e5f6g7h8. | Sarah      | Johnson    | Product Manager     | Startup Inc    | San Francisco  | HarvestAPI LinkedIn |
| i9j0k1l2. | Mike       | Davis      | Data Scientist      | AI Solutions   | San Francisco  | Gemini AI        |
================================================================================

Total professionals found: 10

================================================================================
🔍 SEARCH SUMMARY
================================================================================
City searched: San Francisco
Professionals found: 10
Professionals saved to database: 10
================================================================================

🔍 Search method used: HarvestAPI LinkedIn Profile Search
```

## Project Structure

```
AthenaAI/
├── main.py                   # Main application entry point
├── config.py                 # Configuration and environment variables
├── database.py               # MongoDB database operations
├── gemini_client.py          # Google Gemini AI client
├── apify_controller.py       # Apify API integration
├── display.py                # Display and formatting utilities
├── requirements.txt          # Python dependencies
├── env_example.txt           # Example environment variables
├── test_app.py               # Test suite
├── test_apify_dataset.py     # Apify dataset retrieval test
├── test_linkedin_fields.py   # LinkedIn field extraction test
├── docs/
│   └── fields.json           # Sample LinkedIn profile data
└── README.md                 # This file
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required for AI search)
- `APIFY_API_TOKEN`: Your Apify API token (required for web scraping)
- `GEMINI_MODEL`: Gemini model to use (default: `gemini-2.0-flash-exp`)
- `USE_APIFY`: Set to `true` to use Apify, `false` for Gemini only (default: `true`)
- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017/`)
- `MAX_RESULTS`: Maximum number of professionals to find (default: 10)

**Note**: The application uses a database named `database_training_data` to store professional information.

### Database Schema

Each professional record contains:
- `unique_id`: Unique identifier (UUID)
- `linkedinId`: LinkedIn profile ID (from Apify response)
- `publicIdentifier`: LinkedIn public identifier
- `first_name`: Professional's first name
- `last_name`: Professional's last name
- `headline`: Professional headline/title
- `about`: Professional summary/about section
- `linkedinUrl`: LinkedIn profile URL
- `openToWork`: Whether they're open to work
- `hiring`: Whether they're hiring
- `premium`: Whether they have premium LinkedIn
- `influencer`: Whether they're an influencer
- `photo`: Profile photo URL
- `verified`: Whether profile is verified
- `registeredAt`: When they registered on LinkedIn
- `connectionsCount`: Number of connections
- `followerCount`: Number of followers
- `topSkills`: Top skills summary
- `job_title`: Current job title (from most recent experience)
- `company`: Current company (from most recent experience)
- `employmentType`: Employment type (Full-time, Part-time, etc.)
- `workplaceType`: Workplace type (On-site, Remote, Hybrid)
- `city`: City where they work
- `source`: Data source (LinkedIn Scraper, Google Search, Gemini AI)
- `created_at`: Timestamp when record was created

**Rich Profile Data:**
- `location_*`: Detailed location information (parsed from LinkedIn)
- `currentPosition_*`: Current position details
- `experience`: Complete work experience history (array)
- `education`: Education history (array)
- `certifications`: Professional certifications (array)
- `receivedRecommendations`: Recommendations received (array)
- `skills`: Skills and endorsements (array)
- `languages`: Languages spoken (array)
- `projects`: Projects worked on (array)
- `publications`: Publications (array)
- `moreProfiles`: Related profiles/connections (array)

## API Integration

### Apify API
The application integrates with [Apify's API](https://docs.apify.com/api/v2/act-runs-post) to run web scraping actors:
- **LinkedIn Scraper**: Extracts real professional profiles
- **Google Search Scraper**: Parses search results for professional information

### Google Gemini AI
Uses Google's Gemini 2.5 Flash model for AI-powered professional discovery.

## Debugging

### Apify Integration Issues

If you encounter issues with Apify integration, you can use the dedicated test script:

```bash
python3 test_apify_dataset.py
```

This script will:
- Test the Apify API connection
- Verify actor availability
- Run a test search with detailed logging
- Show the dataset retrieval process

### Common Issues

1. **"Failed to get dataset ID from Apify response"**
   - The actor might not be configured to return a dataset
   - Check if the actor ID is correct
   - Verify your API token has access to the actor

2. **"No results found in dataset"**
   - The actor might not have found any results for the search query
   - Try a different city or search terms
   - Check the actor's documentation for input requirements

3. **"Actor run failed"**
   - The actor might be temporarily unavailable
   - Check your API token permissions
   - Verify the actor is still active and accessible

### Detailed Logging

The application now includes comprehensive logging for Apify operations:
- API request/response details
- Dataset ID extraction and validation
- Dataset item retrieval process
- Response format handling

## Error Handling

The application includes comprehensive error handling for:
- Missing API keys
- Database connection issues
- Invalid city names
- API rate limits
- Data validation errors
- Web scraping failures
- Network connectivity issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

If you encounter any issues:
1. Check that MongoDB is running
2. Verify your API keys are valid
3. Ensure all dependencies are installed
4. Check the console output for error messages
5. Review the search method status in the application menu

## Future Enhancements

- Add professional contact information
- Implement search filters (industry, experience level)
- Add data export functionality
- Create a web interface
- Add professional networking features
- Support for additional Apify actors
- Real-time data validation
- Professional verification system 