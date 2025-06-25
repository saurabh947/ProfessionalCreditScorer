# Professional Finder

A Python application that finds professionals in US cities using Google Gemini AI and stores the results in a local MongoDB database.

## Features

- 🔍 Search for professionals in any US city using Google Gemini AI
- 💾 Store professional data in a local MongoDB database
- 📊 Display results in beautiful tabular format
- 🆔 Assign unique IDs to each professional
- 🔄 Interactive menu system
- 📈 Database statistics and reporting
- 🚀 Command-line and interactive modes

## Prerequisites

Before running this application, you need:

1. **Python 3.7+** installed on your system
2. **MongoDB** running locally (or a MongoDB connection string)
3. **Google Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

1. **Clone or download the project files**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Copy `env_example.txt` to `.env`
   - Add your Google Gemini API key:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

4. **Start MongoDB:**
   - If running locally: `mongod`
   - Or use a cloud MongoDB instance and update the `MONGODB_URI` in your `.env` file

## Usage

### Interactive Mode
Run the application without arguments to start interactive mode:
```bash
python main.py
```

This will show a menu with options:
1. Search for professionals in a city
2. View all professionals in database
3. View professionals by city
4. View database statistics
5. Exit

### Command Line Mode
Search for professionals in a specific city:
```bash
python main.py "San Francisco"
```

## Example Output

```
🏢 Professional Finder Application
==================================================

📊 Professionals in San Francisco:
================================================================================
| ID        | First Name | Last Name  | Job Title           | Company        | City           |
|===========|============|============|=====================|================|================|
| a1b2c3d4. | John       | Smith      | Software Engineer   | Tech Corp      | San Francisco  |
| e5f6g7h8. | Sarah      | Johnson    | Product Manager     | Startup Inc    | San Francisco  |
| i9j0k1l2. | Mike       | Davis      | Data Scientist      | AI Solutions   | San Francisco  |
================================================================================

Total professionals found: 3

================================================================================
🔍 SEARCH SUMMARY
================================================================================
City searched: San Francisco
Professionals found: 3
Professionals saved to database: 3
================================================================================
```

## Project Structure

```
AthenaAI/
├── main.py              # Main application entry point
├── config.py            # Configuration and environment variables
├── database.py          # MongoDB database operations
├── gemini_client.py     # Google Gemini AI client
├── display.py           # Display and formatting utilities
├── requirements.txt     # Python dependencies
├── env_example.txt      # Example environment variables
└── README.md           # This file
```

## Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `MONGODB_URI`: MongoDB connection string (default: `mongodb://localhost:27017/`)
- `MAX_RESULTS`: Maximum number of professionals to find (default: 10)

### Database Schema

Each professional record contains:
- `unique_id`: Unique identifier (UUID)
- `first_name`: Professional's first name
- `last_name`: Professional's last name
- `job_title`: Current job title
- `company`: Current company/organization
- `city`: City where they work
- `created_at`: Timestamp when record was created

## API Usage

The application uses Google Gemini AI to search for professionals. The AI is prompted to:
- Find real professionals working in the specified city
- Provide accurate information about their roles and companies
- Return results in a structured JSON format
- Focus on diverse industries and roles

## Error Handling

The application includes comprehensive error handling for:
- Missing API keys
- Database connection issues
- Invalid city names
- API rate limits
- Data validation errors

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
2. Verify your Gemini API key is valid
3. Ensure all dependencies are installed
4. Check the console output for error messages

## Future Enhancements

- Add professional contact information
- Implement search filters (industry, experience level)
- Add data export functionality
- Create a web interface
- Add professional networking features 