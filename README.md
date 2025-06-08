This repo contains two pipelines. One is Youtube Data Pipeline with Apache Airflow and the other is Automated Weather Data ETL Pipeline with Airflow and AWS S3

YouTube Data Pipeline with Apache Airflow
This project implements an ETL (Extract, Transform, Load) data pipeline using Apache Airflow to collect statistics for a predefined list of YouTube channels. The pipeline extracts data using the YouTube Data API v3, transforms it using Pandas, and loads the processed data into a PostgreSQL database.

The entire Airflow environment, including the PostgreSQL database for Airflow's metadata and the target database for YouTube stats, is containerized using Docker Compose for easy setup and portability.

Features
Extraction: Fetches channel statistics (like subscriber count, view count, video count) and snippet details (like channel name, description, publish date) for a list of YouTube channels.
Transformation: Cleans and reshapes the raw API data into a structured format suitable for analysis using Pandas.
Loading: Loads the transformed data into a specified table in a PostgreSQL database.
Orchestration: Uses Apache Airflow for scheduling (e.g., daily runs) and monitoring the pipeline.
Containerized: Leverages Docker and Docker Compose for a consistent and isolated development and execution environment.

Prerequisites
Docker
Docker Compose
Git (for cloning the repository)
A YouTube Data API v3 Key. You can obtain one from the Google Cloud Console.
Setup and Configuration
Clone the Repository:

git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
Configure Environment Variables:

Copy the example environment file:
cp .env.example .env
Edit the newly created .env file and add your YouTube Data API Key:
YT_API_KEY=YOUR_YOUTUBE_API_KEY_HERE
_PIP_ADDITIONAL_REQUIREMENTS=apache-airflow-providers-postgres>=5.0.0 psycopg2-binary google-api-python-client python-dotenv pandas sqlalchemy
AIRFLOW_UID=50000 # Or your desired user ID for file permissions
Note: The _PIP_ADDITIONAL_REQUIREMENTS line ensures necessary Python packages for the pipeline (like pandas, google-api-python-client, python-dotenv, sqlalchemy) and the Airflow Postgres provider are installed in the Airflow containers.
Build and Start Airflow Services: From the root directory of the project (where docker-compose.yml is located):

docker-compose up -d
This will build the images (if a Dockerfile is used) and start the Airflow webserver, scheduler, worker, PostgreSQL, and Redis containers. The -d flag runs them in detached mode. Wait a few minutes for all services to initialize.

Configure Airflow Connection:

Open the Airflow UI in your browser (usually http://localhost:8080). The default login is airflow / airflow.
Navigate to Admin -> Connections.
Click the + button to add a new connection.
Prepare Target Database and Table (First Time Only): The pipeline appends data. The target database and table need to exist.

Connect to the postgres Docker container:
docker exec -it <your_project_name>_postgres_1 psql -U airflow -d airflow
# Replace <your_project_name>_postgres_1 with the actual container name (use `docker ps`)
# The default user/db in the postgres container (from official Airflow docker-compose) is airflow/airflow.
# If you are connecting to a different user/db for youtube_stats, adjust accordingly.
Inside psql, create the youtube_stats database if it doesn't exist (if your postgres_default connection is not using the airflow database):
-- If connecting as 'airflow' user to 'airflow' db, you might want to create a new user and DB for youtube_stats for separation
-- For simplicity, if using the 'postgres' superuser for 'postgres_default' connection:
-- First, connect as default 'postgres' superuser if not already:
-- docker exec -it <your_project_name>_postgres_1 psql -U postgres
CREATE DATABASE youtube_stats;
\c youtube_stats -- Connect to the new database
Create the target table (adjust columns and types based on your data_transformation.py output):
CREATE TABLE IF NOT EXISTS youtube_channel_stats (
    channel_name VARCHAR(255),
    channel_description TEXT,
    custom_url VARCHAR(255),
    publish_date TIMESTAMP,
    default_language VARCHAR(20),
    localized_title VARCHAR(255),
    local_description TEXT,
    country VARCHAR(10),
    content_detail_related_playlist_likes VARCHAR(255),
    view_count BIGINT,
    suscriber_count BIGINT,
    hidden_subscriber BOOLEAN,
    video_count INTEGER,
    contentdetails_relatedplaylists_uploads VARCHAR(255),
    channel_id VARCHAR(255) PRIMARY KEY,
    channel_label VARCHAR(255), -- Added based on your settings.py
    date DATE -- Added based on your settings.py
);
Type \q to exit psql.
Running the Pipeline
In the Airflow UI (http://localhost:8080), find the DAG named youtube_data_pipeline (or youtube_data_pipeline_taskflow).
Unpause the DAG by toggling the switch to "On".
The DAG is scheduled to run daily by default. You can also trigger it manually by clicking the "play" button next to the DAG name.
Customization
Channel List: Modify the channels dictionary in plugins/youtube/settings.py to change or add YouTube channels to track.
Schedule Interval: Change the schedule parameter in the @dag decorator in dags/youtube_pipeline_dag.py.
Transformations: Update the logic in plugins/youtube/data_transformation.py.

---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Automated Weather Data ETL Pipeline with Airflow and AWS S3

This project implements a robust, automated End-to-End (ETL) data pipeline designed to:
1.  **Extract** daily weather information for a curated list of global cities using the OpenWeatherMap API.
2.  **Transform** the collected raw data into a structured and usable format.
3.  **Load** the processed data into an AWS S3 bucket, creating a historical weather dataset.

The entire workflow is orchestrated and scheduled using Apache Airflow, ensuring efficient and reliable data processingg


## Features

*   **Automated Data Ingestion:** Regularly fetches current weather metrics (temperature, humidity, wind conditions, sunrise/sunset, pressure, etc.).
*   **Structured Data Processing:** Converts JSON API responses into Pandas DataFrames and enriches data with collection timestamps (UTC date).
*   **Scalable Cloud Storage:** Persists transformed data in AWS S3, appending new data daily to a CSV file.
*   **Workflow Orchestration with Apache Airflow:** A Directed Acyclic Graph (DAG) defines, schedules (daily), and monitors the ETL process.
*   **Modular Codebase:** Python logic is organized into distinct plugin modules for extraction, transformation, and loading.
*   **Secure Configuration:** Uses `.env.example` for outlining necessary configurations, with actual secrets managed locally (gitignored) or via Airflow Connections.

## Workflow Overview

The ETL process consists of three main tasks orchestrated by Airflow:

1.  **Extract (`extract_weather_data` task):**
    *   Fetches current weather data for a predefined list of global cities from the OpenWeatherMap API.
    *   Compiles the raw JSON data.
2.  **Transform (`transform_weather_data` task):**
    *   Converts the raw data into a Pandas DataFrame.
    *   Adds a `date` column with the current UTC date.
3.  **Load (`load_weather_data_to_s3` task):**
    *   Connects to AWS S3 using an Airflow S3Hook.
    *   Checks for an existing `daily_weather.csv` file in the target S3 bucket.
    *   Appends the newly transformed data to the existing file or creates a new file if one doesn't exist.
    *   Uploads the final CSV to S3.

## Technology Stack

*   **Orchestration:** Apache Airflow
*   **Programming Language:** Python 3
*   **Data Handling:** Pandas
*   **API Interaction:** Python `requests` library
*   **AWS Interaction:** Boto3 (via Airflow's `S3Hook`)
*   **Data Source:** OpenWeatherMap API
*   **Data Storage:** AWS S3
*   **Environment Management:** `python-dotenv` (for local loading of `.env` by plugin scripts)
*   **Version Control:** Git & GitHub

## Project Structure
