import pandas as pd 
import os 
from dotenv import load_dotenv
import pyodbc


load_dotenv() 

driver = os.getenv("DRIVER")
server = os.getenv("AZURE_SERVER_NAME")
database = os.getenv("AZURE_DATABASE_NAME")
username = os.getenv("AZURE_DATABASE_USERNAME")
password = os.getenv("AZURE_DATABASE_PASSWORD")


conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)


with conn.cursor() as cursor: 
    create_table_query = """
    CREATE TABLE ci_location (
        ci_name VARCHAR(100) PRIMARY KEY, 
        location_full VARCHAR(300) NOT NULL
    );
    """
    cursor.execute(create_table_query)


with conn.cursor() as cursor: 
    create_table_query = """
    CREATE TABLE incidents (
        incident_number VARCHAR(50) PRIMARY KEY, 
        description TEXT NOT NULL, 
        category_full VARCHAR(100) NOT NULL, 
        ci_name VARCHAR(100) NOT NULL, 
        location_full VARCHAR(300),
        owner_group VARCHAR(100) NOT NULL,
        urgency VARCHAR(10) NOT NULL, 
        priority INT NOT NULL,
        SLA VARCHAR(100),
    );
    """
    cursor.execute(create_table_query)


with conn.cursor() as cursor: 
    create_table_query = """
    CREATE TABLE predictions (
    prediction_id VARCHAR(250) PRIMARY KEY, 
    incident_number VARCHAR(250),
    creation_date VARCHAR(30),
    description TEXT,
    category_full VARCHAR(100),
    ci_name VARCHAR(100),
    location_full VARCHAR(300),
    resulted_embeddings VARCHAR(MZX),
    cluster_number INT,
    problem_title VARCHAR(300),
    model VARCHAR(50)
    )"""

    cursor.execute(create_table_query)
    
    
conn.close()