import pandas as pd
import logging
logging.basicConfig(format = '%(levelname)s: %(message)s', level=logging.DEBUG)
import os
from dotenv import load_dotenv
import time
import requests
from datetime import datetime

load_dotenv()

api_key = os.getenv("API_KEY")

# Base URL for the OpenWeatherMap API
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# List of cities
cities = [
    "London", "New York", "Tokyo", "Paris", "Sydney", 
    "Berlin", "Los Angeles", "Dubai", "Toronto", "Madrid",
    "Moscow", "Rome", "Cape Town", "Seoul", "Singapore", 
    "Mexico City", "San Francisco", "Istanbul", "Los Angeles",
    "Bangkok", "Hong Kong", "Buenos Aires", "Cairo", "Delhi",
    "Kuala Lumpur", "Jakarta", "Lagos", "Kathmandu", "Karachi", 
    "Lima", "Rio de Janeiro", "Hong Kong", "Dubai", "Nairobi", 
    "Sydney", "Miami", "Chennai", "Dubai", "Cairo", "Manila", 
    "Paris", "São Paulo", "Shenzhen", "Madrid", "Beijing",
    "Amsterdam", "Mumbai", "Oslo", "Auckland", "Mexico City", 
    "Copenhagen", "Zurich", "Athens", "Kiev", "Vienna"
]

def get_weather_data(city):
    """Fetch wather data from OpenWeatherMap for a given city"""

    params = {
        'q': city,
        'appid':api_key,
        'units':'metric' 
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        return {'city': city,
        'sunrise': data['sys']['sunrise'],
        'sunset': data['sys']['sunset'],
        'country': data['sys']['country'],
        'temperature': data['main']['temp'],
        'humidity': data['main']['humidity'],
        'description': data['weather'][0]['description'],
        'wind_speed' : data['wind']['speed'],
        'pressure' : data['main']['pressure']
        }
    
    else:
        print(f"Error fetching data for {city}: {response.status_code}")

def fetch_weather_for_cities(cities):
    """Fetch weather data for the list of cities"""
    weather_data = []

    for city in cities:
        city_weather = get_weather_data(city)

        if city_weather:
            weather_data.append(city_weather)

        else:
            print(f"No weather data found for {city}")

        time.sleep(1)

    logging.info("Extracted the data of the citites")
    return weather_data

def to_dataframe(weather_data):
    """Converts the weather data to dataframe"""
    weather_df = pd.DataFrame(weather_data)
    print(weather_df)
    return weather_df



    




