import os 
import pyodbc 
import pandas as pd 
from sqlalchemy import create_engine
from dotenv import load_dotenv


def create_sql_server_conn():
    """
    Establishes a connection to an Azure SQL Server database using credentials from environment variables.

    This function loads the necessary environment variables, constructs a connection string, and uses 
    `pyodbc` to create and return a connection object for interacting with the SQL Server.

    Returns:
        pyodbc.Connection: A connection object for the SQL Server database.

    Raises:
        pyodbc.Error: If there is an issue with connecting to the SQL Server.
    """
    load_dotenv()
    driver = os.getenv("DRIVER")
    server = os.getenv("AZURE_SERVER_NAME")
    database = os.getenv("AZURE_DATABASE_NAME")
    username = os.getenv("AZURE_DATABASE_USERNAME")
    password = os.getenv("AZURE_DATABASE_PASSWORD")

    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    return conn


def create_sql_server_engine(): 
    """
    Creates an SQLAlchemy engine for connecting to an Azure SQL Server database.

    This function uses environment variables to retrieve database connection details and constructs
    an SQLAlchemy connection string. It then creates and returns an SQLAlchemy engine for interacting
    with the Azure SQL Server.

    Returns:
        sqlalchemy.engine.base.Engine: An SQLAlchemy engine object configured for the Azure SQL Server.

    Raises:
        ValueError: If any of the required environment variables are missing.
    """
    load_dotenv()
    server = os.getenv("AZURE_SERVER_NAME")
    database = os.getenv("AZURE_DATABASE_NAME")
    username = os.getenv("AZURE_DATABASE_USERNAME")
    password = os.getenv("AZURE_DATABASE_PASSWORD")
    
    azure_connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
    engine = create_engine(azure_connection_string)
    return engine

def query_db(query):
    """
    Executes a SQL query against an Azure SQL Server database and returns the result as a DataFrame.

    This function uses an SQLAlchemy engine to connect to the Azure SQL Server database, executes
    the specified SQL query, and retrieves the results into a pandas DataFrame.

    Args:
        query (str): The SQL query to be executed.

    Returns:
        pandas.DataFrame: The result of the query as a DataFrame.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: If there is an error executing the SQL query.
    """
    engine = create_sql_server_engine()
    with engine.connect() as connection:
        return pd.read_sql(query, connection)