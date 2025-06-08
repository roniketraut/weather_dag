import pandas as pd
import logging
logging.basicConfig(format = '%(levelname)s: %(message)s', level=logging.DEBUG)
from dotenv import load_dotenv


def transform_data(df):
    df['date'] = pd.to_datetime('today').normalize()
    logging.debug(f"{df} has {df.shape[0]} columns and {df.shape[1]} rows")
    return df
