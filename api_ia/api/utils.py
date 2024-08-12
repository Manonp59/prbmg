import pandas as pd 
from dotenv import load_dotenv
import os 
from langchain_openai import AzureOpenAIEmbeddings
import pyodbc
import pickle
import mlflow
from pydantic import BaseModel
import string
from datetime import datetime
from typing import List 
from sentence_transformers import SentenceTransformer
import numpy as np 
import json
import ast 


class PredictionInput(BaseModel):
    incident_number: str
    creation_date: str
    description: str 
    category_full: str 
    ci_name: str 
    location_full: str 
    creation_date: str

class PredictionOuput(BaseModel):
    cluster_number: int 
    problem_title: str
    resulted_embeddings: List[List[float]]

load_dotenv()


azure_deployment = os.getenv('EMBEDDING_AZURE_DEPLOYMENT')
openai_api_version = os.getenv('EMBEDDING_OPENAI_API_VERSION')
api_key = os.getenv('EMBEDDING_API_KEY')
azure_endpoint = os.getenv('EMBEDDING_AZURE_ENDPOINT')

embeddings_model = AzureOpenAIEmbeddings(
    azure_deployment=azure_deployment,
    openai_api_version=openai_api_version,
    api_key = api_key,
    azure_endpoint = azure_endpoint
)

def connect_to_sql_server():
    load_dotenv()
    driver = os.getenv("DRIVER")
    server = os.getenv("AZURE_SERVER_NAME")
    database = os.getenv("AZURE_DATABASE_NAME")
    username = os.getenv("AZURE_DATABASE_USERNAME")
    password = os.getenv("AZURE_DATABASE_PASSWORD")

    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    return conn


def predict_cluster(model_path,incident:PredictionInput):

    loaded_model = mlflow.pyfunc.load_model(model_path)
    docs = incident.description + " " + incident.category_full + " " + incident.location_full + " " + incident.ci_name 
    punctuation_table = str.maketrans("", "", string.punctuation + "“”’")
    docs = docs.translate(punctuation_table)
    input_series = pd.Series({"docs":docs})
    embeddings = get_embeddings(input_series)
    prediction = loaded_model.predict(embeddings)
    problem_title = get_problem_title(prediction[0])
    output = PredictionOuput(cluster_number=prediction[0],problem_title=problem_title, resulted_embeddings=embeddings)

    return output 


def get_model_path(model_run):
    mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
    print(os.getenv('MLFLOW_TRACKING_URI'))
    experiment = mlflow.get_experiment_by_name("incidents_clustering")
    runs = mlflow.search_runs(experiment_ids=experiment.experiment_id)
    filtered_runs = runs[runs['tags.mlflow.runName'] == model_run]
    filtered_runs = filtered_runs.sort_values(by='metrics.silhouette score', ascending=False)
    run_id = filtered_runs.iloc[0]['run_id']
    run = mlflow.get_run(run_id)
    artifact_uri = run.info.artifact_uri
    
    # Assurez-vous que l'URI de l'artefact commence par 'azureml://'
    if not artifact_uri.startswith('azureml://'):
        raise ValueError(f"Artifact URI '{artifact_uri}' does not start with 'azureml://'")

    # Vous pouvez utiliser directement l'URI de l'artefact Azure sans le télécharger localement
    model_uri = artifact_uri + f"/{model_run}"

    return model_uri


def get_embeddings(input:pd.Series)-> pd.DataFrame:
    model_paraphrase = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = model_paraphrase.encode(input)
    embeddings_np = np.array(embeddings)
    embeddings_list = embeddings_np.tolist()
    
    return embeddings_list


def get_problem_title(cluster_number:int,table="kmeans_30_clusters_title") -> str:
    modelisation_query = f"""
    SELECT *
    FROM {table}
    """

    conn = connect_to_sql_server()
    df = pd.read_sql_query(modelisation_query,conn)
    row = df[df['cluster'] == cluster_number]
    # Vérifier si le numéro de cluster est présent dans le DataFrame
    if not row.empty:
        # Récupérer le nom du problème associé
        problem_title = row.iloc[0]['problem_title']
        return problem_title
    else:
        # Si le numéro de cluster n'est pas trouvé, retourner un message d'erreur
        return f"No problem title found for cluster {cluster_number}"

