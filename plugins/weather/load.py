import pandas as pd
import logging
logging.basicConfig(format = '%(levelname)s: %(message)s', level=logging.DEBUG)
from spotify.extraction import get_weather_data, fetch_weather_for_cities, to_dataframe
from spotify.transformation import transform_data
import boto3
import io
from botocore.exceptions import ClientError
from io import StringIO
from dotenv import load_dotenv
import os

load_dotenv()

# Load AWS env variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
# S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

#weather_data = fetch_weather_for_cities(cities)
#untransformed_df = to_dataframe(weather_data)
#df = transform_data(untransformed_df)

# initializing the s3 client
#s3 = boto3.client(
#      's3', 
#        aws_access_key_id=AWS_ACCESS_KEY_ID,
 #       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
  #      region_name=AWS_REGION
   # )

def _get_s3_client(s3_client_passed = None):
    """Helper to get S3 clinet, prioritizing passed client."""
    if s3_client_passed:
        return s3_client_passed
    logging.info("Creating new S3 client using credentials from environment variables")

    if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_REGION:
        logging.error("AWS credentilas or region not found in environment for S3 cleint creation.")
        raise ValueError("AWS credentials/region missing")
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

def upload_df_to_s3(df: pd.DataFrame, bucket: str, key: str, s3_client = None):
    """Upload a dataframe as CSV to S3"""
    if df.empty:
        logging.warning(f"DataFrame is empty. Skipping upload to s3://{bucket}/{key}")
        return

    s3 = _get_s3_client(s3_client)   
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index = False)

    try:
        s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
        logging.info(f"Uploaded to s3://{bucket}/{key}")
    except ClientError as e:
        logging.error(f"Failed to upload to s3://{bucket}/{key}: {e}")
        raise


# funciton to check if the file already exists in s3
def check_if_file_exists(bucket, key, s3_client=None):
    """Check if the file already exists in s3"""
    s3 = _get_s3_client(s3_client)
    try:
        s3.head_object(Bucket = bucket, Key = key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        raise

def download_csv_from_s3(bucket: str, key: str, s3_client=None) -> pd.DataFrame:
    """Download CSV file from S3 and return as dataframe"""
    s3 = _get_s3_client(s3_client)
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        logging.info(f"Downloaded from s3://{bucket}/{key}")
        return pd.read_csv(io.StringIO(content))
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            logging.warning(f"File s3://{bucket}/{key} not found. Returning empty DataFrame.")
            return pd.DataFrame()
        logging.error(f"Error downloading from s3://{bucket}/{key}: {e}")
        raise

def append_data_to_s3(bucket: str, key: str, new_data_df: pd.DataFrame, s3_client_passed=None):
    """Appends new data to an existing CSV in S3 or creates a new one."""
    s3 = _get_s3_client(s3_client_passed) # Get client once for all operations

    if new_data_df.empty:
        logging.warning("New data DataFrame is empty. Nothing to append or upload.")
        return

    if check_if_file_exists(bucket, key, s3):
        logging.info(f"File {key} exists in bucket {bucket}. Appending data.")
        existing_df = download_csv_from_s3(bucket, key, s3)
        if existing_df.empty:
            updated_df = new_data_df
        else:
            updated_df = pd.concat([existing_df, new_data_df], ignore_index=True)
    else:
        logging.info(f"File {key} does not exist in bucket {bucket}. Creating new file.")
        updated_df = new_data_df

    upload_df_to_s3(updated_df, bucket, key, s3)
    logging.info(f"Data successfully appended/uploaded to s3://{bucket}/{key}")
        

# append_data_to_s3(S3_BUCKET_NAME, "weather-data/daily_weather.csv", df, s3)
