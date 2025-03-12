import requests
from config import Config

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
    
    try:
        response = requests.get(Config.BASE_URL, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred: {e}")
        return None