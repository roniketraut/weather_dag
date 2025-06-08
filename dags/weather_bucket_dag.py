import pandas as pd
import logging
logging.basicConfig(format = '%(levelname)s: %(message)s', level=logging.DEBUG)
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.append('/opt/airflow/plugins')  
import os
from weather.extraction import fetch_weather_for_cities, to_dataframe, get_weather_data
from weather.transformation import transform_data
from weather.load import append_data_to_s3
from airflow.decorators import dag, task
from dotenv import load_dotenv
import boto3

dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'plugins', 'weather', '.env')

load_dotenv(dotenv_path=dotenv_path)

# Load AWS env variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


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

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# initializing the s3 client
s3 = boto3.client(
        's3', 
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

@dag(
    dag_id = 'weather_bucket_dag', 
    start_date = datetime(2025, 5, 12),
    end_date = datetime(2025, 5, 21),
    catchup = False,
    schedule='@daily'
)

def etl_weahter():
    @task
    def extract_data(cities: list) -> pd.DataFrame:
        """Extracts weather data for the given cities and returns a DataFrame."""
        raw_weather_data = fetch_weather_for_cities(cities)
        if not raw_weather_data:
            logging.warning("No weather data was executed. Returning an empty DataFrame")
            return pd.DataFrame()
        weather_df = to_dataframe(raw_weather_data)
        logging.info(f"Extraction complete. DataFrame shape: {weather_df.shape}")
        return weather_df
    
    @task
    def data_transformation(weather_df: pd.DataFrame) -> pd.DataFrame:
        """Transformes the extracted weather DataFrame"""
        if weather_df.empty:
            logging.warning("Recieved empty DataFrame for transformation. Skipping")
            return df
        logging.info(f"Starting transformation for DataFrame with shape: {weather_df.shape}")
        transformed_data = transform_data(weather_df)
        (f"Transformation complete. DataFrame shape: {transformed_data.shape}")
        return transformed_data
    
    @task
    def load_data(transformed_data):
        append_data_to_s3(S3_BUCKET_NAME, "weather-data/daily_weather.csv", transformed_data, s3)    
        
    
    weather_df = extract_data(cities)
    transformed_data = data_transformation(weather_df=weather_df)
    load_data(transformed_data=transformed_data)

# instantiating the dag
etl_weahter()

