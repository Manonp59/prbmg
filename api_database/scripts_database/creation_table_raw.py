import pandas as pd 
import os 
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv() 

driver = os.getenv("DRIVER")
server = os.getenv("AZURE_SERVER_NAME")
database = os.getenv("AZURE_DATABASE_NAME_RAW")
username = os.getenv("AZURE_DATABASE_USERNAME")
password = os.getenv("AZURE_DATABASE_PASSWORD")

engine = create_engine(f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}')


df = pd.read_csv('/home/utilisateur/DevIA/prbmg/api_database/data/brutes/incident_analysis_apr23.csv',delimiter=";")


df.to_sql('incidents_raw', con=engine, if_exists='replace', index=False)


