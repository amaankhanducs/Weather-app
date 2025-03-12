# Weather API

A Flask-based RESTful API for retrieving, storing, and managing weather data.

## Features

- Fetch and store weather data from OpenWeatherMap API
- Support for multiple languages
- Data caching to minimize external API calls
- Pydantic validation for request data
- Comprehensive error handling with HTTP status codes
- Proper logging setup
- Supports GET, POST, and DELETE operations

## Requirements

- Python 3.6+
- Flask and dependencies (see requirements.txt)
- OpenWeatherMap API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/weather-api.git
cd weather-api
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables (optional):
```bash
export OPENWEATHERMAP_API_KEY='your_api_key_here'
export DEBUG='True'  # Set to 'False' in production
export DATABASE_URL='your_database_url'  # Optional, defaults to SQLite
```

## Usage

### Starting the application

Run the application:
```bash
python app.py
```

The API will be available at http://localhost:8000/

### API Endpoints

#### GET /
Returns basic information about the API and its endpoints.

#### POST /
Get weather data for a specific city.

Request body:
```json
{
  "city_name": "London",
  "lang": "en"
}
```

Parameters:
- `city_name`: Name of the city (required)
- `lang`: Language code (optional, defaults to "en")

Response example:
```json
{
  "id": 1,
  "city": "London",
  "language": "en",
  "temperature": {
    "temp": 15.2,
    "feels_like": 14.5,
    "temp_min": 13.8,
    "temp_max": 16.4,
    "pressure": 1013,
    "humidity": 76
  },
  "wind": {
    "speed": 3.6,
    "deg": 250
  },
  "description": "scattered clouds",
  "timestamp": "2025-03-12T13:45:30.123456"
}
```

#### DELETE /
Delete weather data for a specific city.

Request body:
```json
{
  "city_name": "London",
  "lang": "en"
}
```

Parameters:
- `city_name`: Name of the city (required)
- `lang`: Language code (optional, defaults to "en")

Response example:
```json
{
  "message": "Weather data for London in en has been deleted successfully",
  "deleted_at": "2025-03-12T14:05:30.123456"
}
```

#### GET /cities
List all cities stored in the database.

Response example:
```json
{
  "count": 2,
  "cities": [
    {
      "id": 1,
      "city": "London",
      "language": "en",
      "last_updated": "2025-03-12T13:45:30.123456",
      "is_fresh": true
    },
    {
      "id": 2,
      "city": "Paris",
      "language": "fr",
      "last_updated": "2025-03-12T12:30:15.654321",
      "is_fresh": false
    }
  ]
}
```

## Configuration

Configuration options can be found in `config.py`. The following settings can be customized:

- `DEBUG`: Enable/disable debug mode (default: False)
- `TESTING`: Enable/disable testing mode (default: False)
- `SQLALCHEMY_DATABASE_URI`: Database connection string (default: SQLite)
- `SECRET_KEY`: Secret key for the Flask application
- `API_KEY`: OpenWeatherMap API key
- `CACHE_TIMEOUT_MINUTES`: Cache duration for weather data (default: 30 minutes)

## Project Structure

```
weather-api/
├── app.py              # Main application file
├── config.py           # Configuration settings
├── routes.py           # API endpoints
├── schemas.py          # Pydantic validation models
├── weather_api.py      # OpenWeatherMap API integration
├── requirements.txt    # Dependencies
└── README.md           # Documentation
```

## Error Handling

The API uses standard HTTP status codes:
- 200 OK: Request successful
- 400 Bad Request: Invalid request data
- 404 Not Found: Resource not found
- 405 Method Not Allowed: HTTP method not supported
- 500 Internal Server Error: Unexpected error

Error responses are returned as JSON:
```json
{
  "error": "Description of the error"
}
```

## Logging

The application uses Python's built-in logging module to log events at different levels:
- INFO: Standard operation information
- WARNING: Warning events
- ERROR: Error events that might still allow the application to continue running
- CRITICAL: Critical events that may cause the application to terminate

Logs are output to the console by default.



## Contributors

Your Name Mohd Amaan Khan