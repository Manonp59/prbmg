import pandas as pd 
from dotenv import load_dotenv
import os 
from langchain_openai import AzureOpenAIEmbeddings
import numpy as np 
import pyodbc
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import  HTTPException, status, Depends
from jose import JWTError, jwt
import pickle
import mlflow
from pydantic import BaseModel


class PredictionInput(BaseModel):
    input_str: str

class PredictionOuput(BaseModel):
    cluster_number: int 
    problem_title: str

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


async def has_access(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token = credentials.credentials
    SECRET_KEY = os.getenv("API_IA_SECRET_KEY")
    ALGORITHM = "HS256"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
    except JWTError:
        raise credentials_exception
    if username == "admin":
        return True
    else:
        raise credentials_exception
    

def predict_cluster(model_path, incident:PredictionInput):

    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)

    input_series = pd.Series({"docs":incident.input_str})
    embeddings = get_embeddings(input_series)
    prediction = loaded_model.predict(embeddings)
    problem_title = get_problem_title(prediction[0])
    output = PredictionOuput(cluster_number=prediction[0],problem_title=problem_title)

    return output 


def get_model_path(model_run):
    experiment = mlflow.get_experiment_by_name("incidents_clustering")
    runs = mlflow.search_runs(experiment_ids=experiment.experiment_id)
    filtered_runs = runs[runs['tags.mlflow.runName'] == model_run]
    run_id = filtered_runs.iloc[0]['run_id']
    run = mlflow.get_run(run_id)
    artifact_uri = run.info.artifact_uri
    local_artifact_path = artifact_uri.replace("file://", "")
    model_path = os.path.join(local_artifact_path, model_run, "model.pkl")
    return model_path


def generate_token(to_encode):
    SECRET_KEY = os.environ.get("API_IA_SECRET_KEY")
    ALGORITHM = "HS256"
    to_encode_dict = {"sub": to_encode}
    encoded_jwt = jwt.encode(to_encode_dict, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_embeddings(input:pd.Series)-> pd.DataFrame:
    embeddings = embeddings_model.embed_documents(input)
    return embeddings


def get_problem_title(cluster_number:int,table="kmean30_clusters_title") -> str:
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


if __name__ == "__main__":
    print(generate_token("admin"))