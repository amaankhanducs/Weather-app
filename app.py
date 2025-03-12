from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask and Config
app = Flask(__name__)
app.config.from_object(Config)

# Initialize the SQLAlchemy object
db = SQLAlchemy(app)

# Define models
class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(50), nullable=False)
    language = db.Column(db.String(5), nullable=False)
    temp = db.Column(db.Float, nullable=False)
    feels_like = db.Column(db.Float, nullable=False)
    temp_min = db.Column(db.Float, nullable=False)
    temp_max = db.Column(db.Float, nullable=False)
    pressure = db.Column(db.Integer, nullable=False)
    humidity = db.Column(db.Integer, nullable=False)
    wind_speed = db.Column(db.Float, nullable=False)
    wind_deg = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('city_name', 'language', name='unique_city_lang'),
    )
    
    def __repr__(self):
        return f'<Weather {self.city_name} ({self.language})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'city': self.city_name,
            'language': self.language,
            'temperature': {
                'temp': self.temp,
                'feels_like': self.feels_like,
                'temp_min': self.temp_min,
                'temp_max': self.temp_max,
                'pressure': self.pressure,
                'humidity': self.humidity
            },
            'wind': {
                'speed': self.wind_speed,
                'deg': self.wind_deg
            },
            'description': self.description,
            'timestamp': self.timestamp.isoformat()
        }



# Create the database if it doesn't exist
with app.app_context():
    db.create_all()
    logger.info("Database tables created or verified")
# Import routes after model definition
from routes import *

if __name__ == '__main__':
    logger.info("Starting Weather API application")
    app.run(host='0.0.0.0', port=8000, debug=Config.DEBUG)