import pandas as pd 
from sklearn.cluster import KMeans
import pickle
import mlflow
from sklearn.metrics import silhouette_score
import sys
import ast
import numpy as np 
import os 
import pyodbc
from sqlalchemy import create_engine
sys.path.append("/home/utilisateur/DevIA/prbmg")
from config import cfg
import json
from api_ia.clustering_model.utils import create_sql_server_conn, create_sql_server_engine


def modelisation(df,run_name):
    df["resulted_embeddings"] = df["resulted_embeddings"].apply(lambda x: ast.literal_eval(x))
    embeddings_np = np.array(df["resulted_embeddings"].tolist())
    print(embeddings_np)

    n_clusters = cfg.model.n_clusters

    experiment_name = "incidents_clustering"
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id

    run_name = f"kmeans_{n_clusters}"

    engine = create_sql_server_engine()

    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run : 
        mlflow.set_tracking_uri("http://127.0.0.1:5000")
        model = KMeans(n_clusters=n_clusters,init='k-means++')
        model.fit(embeddings_np)
        mlflow.sklearn.log_model(model, run_name)
        mlflow.log_params(({"n_clusters":n_clusters}))
        mlflow.set_tag("model","kmeans")
        labels = model.labels_
        print(labels)
        silouhette_avg = silhouette_score(embeddings_np, labels)
        mlflow.log_metric("silhouette score",silouhette_avg)
        df['clusters'] = labels
        df['resulted_embeddings'] = [json.dumps(embedding) for embedding in df['resulted_embeddings']]
        df.to_csv(f'api_ia/clustering_model/df_kmeans_{n_clusters}.csv')
        df.to_excel(f'api_ia/clustering_model/df_kmeans_{n_clusters}.xlsx')
        df.to_sql('incidents_clusters',con=engine,if_exists='append',index=False)
        with open(f'api_ia/clustering_model/model_kmeans_{n_clusters}.pickle', 'wb') as f:
            pickle.dump(model, f)
        run_id = run.info.run_id
    
    return run_id,df

