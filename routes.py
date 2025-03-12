from flask import jsonify, request
from datetime import datetime, timedelta
import logging
from app import app, db, Weather
from weather_api import fetch_weather_data
from http import HTTPStatus
from schemas import WeatherRequest, CityDeleteRequest
from pydantic import ValidationError

# Configure logging
logger = logging.getLogger(__name__)

@app.route('/', methods=['GET'])
def home():
    """Homepage route that provides basic information about the API."""
    logger.info("Home route accessed")
    return jsonify({
        'message': 'Welcome to the Weather API',
        'usage': {
            'GET /': 'API information',
            'POST /': 'Get weather data with {"city_name": "city", "lang": "language_code"}',
            'DELETE /': 'Delete weather data with {"city_name": "city", "lang": "language_code"}',
            'GET /cities': 'Get list of all cities in the database',
            'GET /cities/<id>': 'Get weather data for a specific city by ID'
        }
    }), HTTPStatus.OK

@app.route('/', methods=['POST'])
def get_weather():
    """Get weather data for a specific city in the requested format."""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided in the request")
            return jsonify({'error': 'No JSON data provided'}), HTTPStatus.BAD_REQUEST
        
        # Validate request data with Pydantic
        try:
            weather_request = WeatherRequest(**data)
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST
        
        city_name = weather_request.city_name
        language = weather_request.lang
        
        logger.info(f"Processing weather data request for {city_name} in {language}")
        
        # Check if the weather data for the city and language is in the database
        weather_data = Weather.query.filter_by(city_name=city_name, language=language).first()
        
        needs_update = False
        if weather_data:
            # Check if the data is older than the configured cache timeout
            time_difference = datetime.utcnow() - weather_data.timestamp
            if time_difference > timedelta(minutes=app.config['CACHE_TIMEOUT_MINUTES']):
                logger.info(f"Data is older than {app.config['CACHE_TIMEOUT_MINUTES']} minutes, fetching new data for {city_name} in {language}")
                needs_update = True
        
        # If no data in the database or data is too old, fetch from OpenWeatherMap API
        if not weather_data or needs_update:
            api_response = fetch_weather_data(city_name, language)
            
            if not api_response:
                logger.error(f"Failed to fetch data from API for {city_name}")
                return jsonify({'error': 'City not found or API error'}), HTTPStatus.NOT_FOUND
            
            try:
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
                logger.info(f"Successfully saved weather data for {city_name}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Database error: {str(e)}")
                return jsonify({'error': 'Database error when saving weather data'}), HTTPStatus.INTERNAL_SERVER_ERROR
        
        # Return the data
        return jsonify(weather_data.to_dict()), HTTPStatus.OK
    
    except Exception as e:
        logger.error(f"Unexpected error in get_weather: {str(e)}")
        return jsonify({'error': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/', methods=['DELETE'])
def delete_weather():
    """Delete weather data for a specific city."""
    try:
        data = request.get_json()
        
        if not data:
            logger.warning("No JSON data provided in the request")
            return jsonify({'error': 'No JSON data provided'}), HTTPStatus.BAD_REQUEST
        
        # Validate request data with Pydantic
        try:
            delete_request = CityDeleteRequest(**data)
        except ValidationError as e:
            logger.warning(f"Validation error: {str(e)}")
            return jsonify({'error': str(e)}), HTTPStatus.BAD_REQUEST
        
        city_name = delete_request.city_name
        language = delete_request.lang
        
        logger.info(f"Processing delete request for {city_name} in {language}")
        
        # Find the weather data for the city and language
        weather_data = Weather.query.filter_by(city_name=city_name, language=language).first()
        
        if not weather_data:
            logger.warning(f"Weather data not found for {city_name} in {language}")
            return jsonify({'error': f'No data found for {city_name} in {language}'}), HTTPStatus.NOT_FOUND
        
        try:
            # Delete the weather data
            db.session.delete(weather_data)
            db.session.commit()
            logger.info(f"Successfully deleted weather data for {city_name} in {language}")
            
            return jsonify({
                'message': f'Weather data for {city_name} in {language} has been deleted successfully',
                'deleted_at': datetime.utcnow().isoformat()
            }), HTTPStatus.OK
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error when deleting: {str(e)}")
            return jsonify({'error': 'Database error when deleting weather data'}), HTTPStatus.INTERNAL_SERVER_ERROR
    
    except Exception as e:
        logger.error(f"Unexpected error in delete_weather: {str(e)}")
        return jsonify({'error': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/cities', methods=['GET'])
def get_cities():
    """Get a list of all cities in the database."""
    try:
        logger.info("Fetching list of all cities")
        cities = Weather.query.all()
        result = []
        
        for city in cities:
            time_difference = datetime.utcnow() - city.timestamp
            is_fresh = time_difference <= timedelta(minutes=app.config['CACHE_TIMEOUT_MINUTES'])
            
            result.append({
                'id': city.id,
                'city': city.city_name,
                'language': city.language,
                'last_updated': city.timestamp.isoformat(),
                'is_fresh': is_fresh
            })
        
        logger.info(f"Found {len(result)} cities in the database")
        return jsonify({
            'count': len(result),
            'cities': result
        }), HTTPStatus.OK
    
    except Exception as e:
        logger.error(f"Unexpected error in get_cities: {str(e)}")
        return jsonify({'error': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.route('/cities/<int:city_id>', methods=['GET'])
def get_city_by_id(city_id):
    """Get weather data for a specific city by ID."""
    try:
        logger.info(f"Fetching weather data for city with ID: {city_id}")
        
        # Find the weather data for the given ID
        weather_data = Weather.query.get(city_id)
        
        if not weather_data:
            logger.warning(f"Weather data not found for ID: {city_id}")
            return jsonify({'error': f'No data found for city with ID: {city_id}'}), HTTPStatus.NOT_FOUND
        
        # Check if the data is fresh
        time_difference = datetime.utcnow() - weather_data.timestamp
        is_fresh = time_difference <= timedelta(minutes=app.config['CACHE_TIMEOUT_MINUTES'])
        
        # Return the weather data with freshness information
        response_data = weather_data.to_dict()
        response_data['is_fresh'] = is_fresh
        response_data['last_updated'] = weather_data.timestamp.isoformat()
        
        logger.info(f"Successfully retrieved weather data for {weather_data.city_name}")
        return jsonify(response_data), HTTPStatus.OK
    
    except Exception as e:
        logger.error(f"Unexpected error in get_city_by_id: {str(e)}")
        return jsonify({'error': 'Internal server error'}), HTTPStatus.INTERNAL_SERVER_ERROR

@app.errorhandler(HTTPStatus.NOT_FOUND)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return jsonify({'error': 'Route not found. Please check the URL and try again.'}), HTTPStatus.NOT_FOUND

@app.errorhandler(HTTPStatus.METHOD_NOT_ALLOWED)
def method_not_allowed(error):
    """Handle 405 errors."""
    logger.warning(f"405 error: {request.method} {request.path}")
    return jsonify({'error': f'Method {request.method} not allowed for this endpoint'}), HTTPStatus.METHOD_NOT_ALLOWED

@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(error)}")
    return jsonify({'error': 'Internal server error. Please try again later.'}), HTTPStatus.INTERNAL_SERVER_ERROR