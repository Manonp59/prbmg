import pandas as pd 
from sklearn.cluster import KMeans
import mlflow
from sklearn.metrics import silhouette_score
import sys
import ast
import numpy as np 
import os 
from sqlalchemy import create_engine
sys.path.append("/home/utilisateur/DevIA/prbmg")
from config import cfg
import json
from api_ia.clustering_model.utils import create_sql_server_conn, create_sql_server_engine
from dotenv import load_dotenv

load_dotenv()


def modelisation(df,run_name):
    mlflow.set_tracking_uri(os.environ.get("ML_FLOW_TRACKING_URI"))
    df["resulted_embeddings"] = df["resulted_embeddings"].apply(lambda x: ast.literal_eval(x))
    embeddings_np = np.array(df["resulted_embeddings"].tolist())

    n_clusters = cfg.model.n_clusters

    experiment_name = "incidents_clustering"
    experiment = mlflow.get_experiment_by_name(experiment_name)
    if experiment is None:
        experiment_id = mlflow.create_experiment(experiment_name)
    else:
        experiment_id = experiment.experiment_id

    engine = create_sql_server_engine()

    with mlflow.start_run(experiment_id=experiment_id, run_name=run_name) as run : 
        mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
        init='k-means++'
        n_init=80
        algorithm='lloyd'
        model = KMeans(n_clusters=n_clusters,init=init,n_init=n_init,algorithm=algorithm)
        model.fit(embeddings_np)
        mlflow.sklearn.log_model(model, run_name)
        mlflow.log_params(({"n_clusters":n_clusters,"init":init,"n_init":n_init,"algorithm":algorithm}))
        mlflow.set_tag("model","kmeans")
        labels = model.labels_
        print(labels)
        silouhette_avg = silhouette_score(embeddings_np, labels)
        mlflow.log_metric("silhouette score",silouhette_avg)
        df['clusters'] = labels
        df['resulted_embeddings'] = [json.dumps(embedding) for embedding in df['resulted_embeddings']]
        df.to_sql('incidents_clusters',con=engine,if_exists='append',index=False)
        run_id = run.info.run_id
    
    return run_id,df



