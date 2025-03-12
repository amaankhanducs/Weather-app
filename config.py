import os

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    API_KEY = '186316716709c31e9f17840d653a9eba'  # Your OpenWeatherMap API key
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///weather.db'