import os
import secrets

class Config:
    # Application settings
    # Fix DEBUG setting to ensure it correctly reads string values
    # DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///weather.db'
    
    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    
    # API settings
    API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY') or '186316716709c31e9f17840d653a9eba'
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    
    # Cache settings
    CACHE_TIMEOUT_MINUTES = int(os.environ.get('CACHE_TIMEOUT_MINUTES', 30))