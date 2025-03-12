import requests
import logging
from config import Config
from http import HTTPStatus
# Configure logging
logger = logging.getLogger(__name__)

def fetch_weather_data(city_name, lang='en'):
    """
    Fetch weather data from OpenWeatherMap API
    
    Args:
        city_name (str): Name of the city
        lang (str): Language code (default: 'en')
        
    Returns:
        dict: Weather data or None if error occurs
    """
    params = {
        'q': city_name,
        'appid': Config.API_KEY,
        'units': 'metric',  # Get temperature in Celsius
        'lang': lang  # Language for description
    }
    
    logger.info(f"Fetching weather data for {city_name} in {lang}")
    
    try:
        response = requests.get(Config.BASE_URL, params=params)
        
        if response.status_code == 200:
            logger.info(f"Successfully fetched weather data for {city_name}")
            return response.json()
        else:
            logger.error(f"Error fetching data for {city_name}: HTTP {response.status_code}")
            logger.debug(f"API response: {response.text}")
            return HTTPStatus.INTERNAL_SERVER_ERROR
    except requests.RequestException as e:
        logger.error(f"Request exception while fetching data for {city_name}: {str(e)}")
        return HTTPStatus.INTERNAL_SERVER_ERROR
    except Exception as e:
        logger.error(f"Unexpected exception while fetching data for {city_name}: {str(e)}")
        return HTTPStatus.INTERNAL_SERVER_ERROR