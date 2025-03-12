from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re

class CityRequest(BaseModel):
    city_name: str = Field(..., min_length=2, max_length=50)
    lang: Optional[str] = Field('en')  # No length restriction for lang field

    @validator('city_name')
    def validate_city_name(cls, v):
        if not re.match(r'^[a-zA-Z\s\-]+$', v):
            raise ValueError('City name must only contain letters, spaces, and hyphens')
        return v
    
    @validator('lang')
    def validate_language(cls, v):
        # Allow any length, but only alphabetic characters are allowed
        if not re.match(r'^[a-zA-Z]+$', v):
            raise ValueError('Language code must only contain alphabetic characters')
        return v

class WeatherRequest(CityRequest):
    pass

class CityDeleteRequest(CityRequest):
    pass

class WeatherResponse(BaseModel):
    city: str
    temperature: dict
    wind: dict
    description: str

class ErrorResponse(BaseModel):
    error: str
    status_code: int

class CityListResponse(BaseModel):
    count: int
    cities: List[dict]
