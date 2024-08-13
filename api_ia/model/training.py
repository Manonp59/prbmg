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
    """
    Fetches incident data from a remote API and returns it as a DataFrame.

    This function sends a GET request to a specified API endpoint to retrieve incident data. The data is returned
    in JSON format and is then converted into a pandas DataFrame for further processing.

    Returns:
        pd.DataFrame: A DataFrame containing the incident data fetched from the API.

    Raises:
        HTTPError: If the HTTP request returned an unsuccessful status code.
    """
    url = "http://prbmg-api-database.francecentral.azurecontainer.io:8000/incidents/"
    headers = {"X-API-Key":"ipNOJ2OiSAvkUAsjE554SVnwYyBKcXFT"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Assurez-vous que la requête est réussie
    incidents = response.json()
    incidents = pd.DataFrame(incidents)

    return incidents


def training(run_name):
    """
    Orchestrates the pipeline for processing incident data and training a clustering model.

    Parameters:
        run_name (str): Unique identifier for the training run.

    Returns:
        str: MLflow run ID for the current training session.

    Process:
        1. Fetch and clean incident data.
        2. Select features and create embeddings.
        3. Train a clustering model and save results.
        4. Generate and store cluster titles.
    """
    engine = create_sql_server_engine()

    # Exécution de la requête et récupération des données dans un DataFrame Pandas
    df = get_incidents()
    df_clean = clean_dataset(df)
    df_clean.to_sql(run_name +'_cleandataset', engine, index=False, if_exists='replace')
    df_feat = features_selection(df_clean)
    df_feat.to_sql(run_name +'_trainingdataset', engine, index=False, if_exists='replace')
    df_embeddings = make_embeddings(df_feat)
    df_embeddings.to_sql(run_name +'_trainingdataset_embed', engine, index=False, if_exists='replace')
    run_id,df_clusters = modelisation(df_embeddings,run_name)
    df_clusters.to_sql(run_name +'_trainingdataset_clusters', engine, index=False, if_exists='replace')
    df_named, cluster_title = make_naming(df_clusters)
    df_named.to_sql(run_name +'_trainingdataset_titles', engine, index=False, if_exists='replace')
    cluster_title.to_sql(run_name +'_clusters_title', engine, index=False, if_exists='replace')

    return run_id
