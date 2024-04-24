import pandas as pd 
import sys
import numpy as np 
import os 
import pyodbc
from openai import AzureOpenAI
from sqlalchemy import create_engine

driver = os.getenv("DRIVER")
server = os.getenv("AZURE_SERVER_NAME")
database = os.getenv("AZURE_DATABASE_NAME")
username = os.getenv("AZURE_DATABASE_USERNAME")
password = os.getenv("AZURE_DATABASE_PASSWORD")

conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)


naming_api_type = os.getenv('NAMING_OPENAI_API_TYPE') 
naming_openai_api_version = os.getenv('NAMING_OPENAI_API_VERSION')
naming_openai_api_base = os.getenv('NAMING_OPENAI_API_BASE')
naming_openai_api_key = os.getenv('NAMING_OPENAI_API_KEY') 

client = AzureOpenAI(api_key=naming_openai_api_key,azure_endpoint=naming_openai_api_base,api_version=naming_openai_api_version)

modelisation_query = f"""
SELECT *
FROM incidents_clusters
"""
    
df = pd.read_sql_query(modelisation_query,conn)

azure_connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(azure_connection_string)

data =[]

for c in (df.clusters.unique()):
    cluster = df.query(f"clusters == {c}")
    docs_str = "\n".join(cluster[cluster['clusters'] == c]['docs'])
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
        {"role": "system", "content": "You're an IT Service Suppport Manager. You're helping me name each IT incident into problem."},
        {"role": "user", "content": f"Using the following incident descriptions, write a problem title that summarizes all of them.\n\nIncidents:{docs_str}\n\nPROBLEM TITLE:"}
    ]
    )
    problem_title = completion.choices[0].message.content
    print(problem_title)
    df.loc[df.clusters == c, "problem_title"] = problem_title
    
    data.append({'cluster': c, 'problem_title': problem_title})

df.to_csv('api_ia/clustering_model/df_title.csv')
df.to_sql('incidents_title',con=engine,if_exists='append',index=False)
df_title = pd.DataFrame(data)
df_title.to_csv('api_ia/clustering_model/clusters_title.csv')
df_title.to_sql('clusters_title', con=engine,if_exists='append',index=False)


