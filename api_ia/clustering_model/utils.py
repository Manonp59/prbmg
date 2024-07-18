import os 
import pyodbc 
import pandas as pd 
from sqlalchemy import create_engine
from dotenv import load_dotenv


def create_sql_server_conn():
    load_dotenv()
    driver = os.getenv("DRIVER")
    server = os.getenv("AZURE_SERVER_NAME")
    database = os.getenv("AZURE_DATABASE_NAME")
    username = os.getenv("AZURE_DATABASE_USERNAME")
    password = os.getenv("AZURE_DATABASE_PASSWORD")

    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    return conn


def create_sql_server_engine(): 
    load_dotenv()
    server = os.getenv("AZURE_SERVER_NAME")
    database = os.getenv("AZURE_DATABASE_NAME")
    username = os.getenv("AZURE_DATABASE_USERNAME")
    password = os.getenv("AZURE_DATABASE_PASSWORD")
    
    azure_connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    engine = create_engine(azure_connection_string)
    return engine

def query_db(query):
    engine = create_sql_server_engine()
    with engine.connect() as connection:
        return pd.read_sql(query, connection)