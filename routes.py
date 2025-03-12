from flask import jsonify, request
from datetime import datetime, timedelta
from app import app, db, Weather
from weather_api import fetch_weather_data

@app.route('/', methods=['GET'])
def home():
    """Homepage route that provides basic information about the API."""
    return jsonify({
        'message': 'Welcome to the Weather API',
        'usage': 'Send a POST request to / with {"city_name": "city", "lang": "language_code"}'
    })

@app.route('/', methods=['POST'])
def get_weather():
    """Get weather data for a specific city in the requested format."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    city_name = data.get('city_name')
    language = data.get('lang', 'en')
    
    if not city_name:
        return jsonify({'error': 'city_name parameter is required'}), 400
    
    # Check if the weather data for the city and language is in the database
    weather_data = Weather.query.filter_by(city_name=city_name, language=language).first()
    
    needs_update = False
    if weather_data:
        # Check if the data is older than 30 minutes
        time_difference = datetime.utcnow() - weather_data.timestamp
        if time_difference > timedelta(minutes=30):
            print(f"Data is older than 30 minutes, fetching new data for {city_name} in {language}")
            needs_update = True
    
    # If no data in the database or data is too old, fetch from OpenWeatherMap API
    if not weather_data or needs_update:
        api_response = fetch_weather_data(city_name, language)
        
        if api_response:
            if weather_data:
                # Update the existing weather data
                weather_data.temp = api_response['main']['temp']
                weather_data.feels_like = api_response['main']['feels_like']
                weather_data.temp_min = api_response['main']['temp_min']
                weather_data.temp_max = api_response['main']['temp_max']
                weather_data.pressure = api_response['main']['pressure']
                weather_data.humidity = api_response['main']['humidity']
                weather_data.wind_speed = api_response['wind']['speed']
                weather_data.wind_deg = api_response['wind']['deg']
                weather_data.description = api_response['weather'][0]['description']
                weather_data.timestamp = datetime.utcnow()
            else:
                # Add new weather data to the database
                weather_data = Weather(
                    city_name=city_name,
                    language=language,
                    temp=api_response['main']['temp'],
                    feels_like=api_response['main']['feels_like'],
                    temp_min=api_response['main']['temp_min'],
                    temp_max=api_response['main']['temp_max'],
                    pressure=api_response['main']['pressure'],
                    humidity=api_response['main']['humidity'],
                    wind_speed=api_response['wind']['speed'],
                    wind_deg=api_response['wind']['deg'],
                    description=api_response['weather'][0]['description'],
                    timestamp=datetime.utcnow()
                )
                db.session.add(weather_data)
            
            db.session.commit()
            
            if weather_data:
                return jsonify(weather_data.to_dict())
            else:
                return jsonify({'error': 'Failed to process weather data'}), 500
        else:
            return jsonify({'error': 'City not found or API error'}), 404
    
    # Return the data if it's not too old
    return jsonify(weather_data.to_dict())

@app.route('/cities', methods=['GET'])
def get_cities():
    """Get a list of all cities in the database."""
    cities = Weather.query.all()
    result = []
    
    for city in cities:
        time_difference = datetime.utcnow() - city.timestamp
        is_fresh = time_difference <= timedelta(minutes=30)
        
        result.append({
            'city': city.city_name,
            'language': city.language,
            'last_updated': city.timestamp.isoformat(),
            'is_fresh': is_fresh
        })
    
    return jsonify({
        'count': len(result),
        'cities': result
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Route not found. Please check the URL and try again.'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error. Please try again later.'}), 500