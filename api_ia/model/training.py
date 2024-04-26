from api_ia.embeddings.embeddings import clean_dataset, features_selection, make_embeddings
from api_ia.clustering_model.clustering import modelisation
from api_ia.clustering_model.naming import make_naming
from api_ia.clustering_model.utils import create_sql_server_conn, create_sql_server_engine
from dotenv import load_dotenv
import pandas as pd 
import os 
import pyodbc


def training(run_name,start_date="2017-01-01",end_date="2018-01-01"):

    engine = create_sql_server_engine()
    table_name = 'incidents_location'
    # Requête SQL pour récupérer toute la table
    query = f"SELECT * FROM {table_name}"
    # Exécution de la requête et récupération des données dans un DataFrame Pandas
    df = pd.read_sql(query, engine)
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