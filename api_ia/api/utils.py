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

# API configuration for embedding model
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
    """
    Establishes a connection to an Azure SQL Server database using environment variables.

    This function:
    1. Loads environment variables from a `.env` file.
    2. Retrieves database connection parameters.
    3. Creates and returns a connection object to the SQL Server using `pyodbc`.

    Returns:
        pyodbc.Connection: A connection object to the Azure SQL Server database.

    Raises:
        pyodbc.Error: If the connection fails.
    """
    load_dotenv()
    driver = os.getenv("DRIVER")
    server = os.getenv("AZURE_SERVER_NAME")
    database = os.getenv("AZURE_DATABASE_NAME")
    username = os.getenv("AZURE_DATABASE_USERNAME")
    password = os.getenv("AZURE_DATABASE_PASSWORD")

    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    return conn


def predict_cluster(model_path,incident:PredictionInput):
    """
    Predicts the cluster and problem title for a given incident using a pre-trained model.

    This function:
    1. Loads a machine learning model from the specified path using `mlflow`.
    2. Combines the incident details into a single text string.
    3. Cleans the text by removing punctuation.
    4. Converts the cleaned text into embeddings.
    5. Uses the model to predict the cluster based on the embeddings.
    6. Retrieves the problem title corresponding to the predicted cluster.
    7. Returns a `PredictionOuput` object containing the cluster number, problem title, and embeddings.

    Args:
        model_path (str): The file path to the pre-trained ML model.
        incident (PredictionInput): An object containing details about the incident.

    Returns:
        PredictionOuput: An object containing the predicted cluster number, problem title, and embeddings.

    Raises:
        Exception: If there's an error during model loading, text processing, or prediction.
    """
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
    """
    Retrieves the URI of the model artifact from MLflow based on the specified model run name.

    This function:
    1. Sets the MLflow tracking URI from environment variables.
    2. Retrieves the experiment by its name.
    3. Searches for runs associated with the specified model run name.
    4. Sorts the runs by silhouette score in descending order.
    5. Gets the artifact URI of the best run.
    6. Constructs and returns the URI for the model artifact.

    Args:
        model_run (str): The name of the model run for which to retrieve the model path.

    Returns:
        str: The URI of the model artifact.

    Raises:
        ValueError: If the artifact URI does not start with 'azureml://'.
        KeyError: If no runs match the specified model run name or if the expected columns are not found in the DataFrame.
    """
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
    """
    Generates embeddings for a given input using a pre-trained SentenceTransformer model.

    This function:
    1. Loads a pre-trained SentenceTransformer model for generating embeddings.
    2. Encodes the input text into embeddings.
    3. Converts the embeddings from a NumPy array to a list.

    Args:
        input (pd.Series): A Pandas Series containing text data to be embedded. The Series should have a single column of text.

    Returns:
        pd.DataFrame: A DataFrame containing the generated embeddings as lists. Each row corresponds to the embeddings of a text input.

    Raises:
        ValueError: If the input is not a Pandas Series or does not contain text data.
    """
    model_paraphrase = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    embeddings = model_paraphrase.encode(input)
    embeddings_np = np.array(embeddings)
    embeddings_list = embeddings_np.tolist()
    
    return embeddings_list


def get_problem_title(cluster_number:int,table="kmeans_40_clusters_title") -> str:
    """
    Retrieves the problem title associated with a given cluster number from a SQL table.

    This function:
    1. Connects to a SQL Server database.
    2. Executes a query to fetch data from the specified table.
    3. Filters the data for the given cluster number.
    4. Returns the problem title associated with the cluster number, if found.

    Args:
        cluster_number (int): The cluster number for which to retrieve the problem title.
        table (str): The name of the SQL table containing cluster information. Defaults to "kmeans_30_clusters_title".

    Returns:
        str: The problem title associated with the cluster number, or an error message if no title is found for the given cluster number.

    Raises:
        ValueError: If there is an issue with the SQL query or connection.
    """
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

