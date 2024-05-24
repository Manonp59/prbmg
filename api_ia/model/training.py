from api_ia.embeddings.embeddings import clean_dataset, features_selection, make_embeddings
from api_ia.clustering_model.clustering import modelisation
from api_ia.clustering_model.naming import make_naming
from api_ia.clustering_model.utils import create_sql_server_conn, create_sql_server_engine
from dotenv import load_dotenv
import pandas as pd 
import os 
import pyodbc
import requests

load_dotenv()

database_api_key = os.getenv('API_DATABASE_SECRET_KEY')

def get_incidents():
    url = "http://127.0.0.1:8000/incidents/"
    headers = {"X-API-Key":"ipNOJ2OiSAvkUAsjE554SVnwYyBKcXFT"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Assurez-vous que la requête est réussie
    incidents = response.json()
    incidents = pd.DataFrame(incidents)
    return incidents


def training(run_name):

    engine = create_sql_server_engine()

    # Exécution de la requête et récupération des données dans un DataFrame Pandas
    df = get_incidents()
    print(df.columns)
    df_clean = clean_dataset(df)
    df_clean.to_sql(run_name +'_cleandataset', engine, index=False, if_exists='replace')
    print('df_clean ok')
    features = ['description','category_full','ci_name','location_full']
    id = 'incident_number'
    df_feat = features_selection(df_clean)
    df_feat.to_sql(run_name +'_trainingdataset', engine, index=False, if_exists='replace')
    print("df_feat ok")
    df_embeddings = make_embeddings(df_feat)
    df_embeddings.to_sql(run_name +'_trainingdataset_embed', engine, index=False, if_exists='replace')
    print("df_embed ok")
    run_id,df_clusters = modelisation(df_embeddings,run_name)
    df_clusters.to_sql(run_name +'_trainingdataset_clusters', engine, index=False, if_exists='replace')
    df_named, cluster_title = make_naming(df_clusters)
    df_named.to_sql(run_name +'_trainingdataset_titles', engine, index=False, if_exists='replace')
    cluster_title.to_sql(run_name +'_clusters_title', engine, index=False, if_exists='replace')

    return run_id
