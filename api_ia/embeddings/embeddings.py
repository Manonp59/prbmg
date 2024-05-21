import pandas as pd 
import pyodbc 
import os
import re
from langchain_openai import AzureOpenAIEmbeddings
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine
import json
from api_ia.clustering_model.utils import create_sql_server_conn, create_sql_server_engine


##### Nettoyage des données #####

def clean_dataset(df)  -> pd.DataFrame:
    # Créer un dictionnaire des anciens noms de colonnes et des nouveaux noms nettoyés
    clean_names = {}
    for col in df.columns:
        # Remplacer les espaces par des _
        new_name = col.strip().lower().replace(' ', '_')
        # Retirer tous les caractères spéciaux
        new_name = re.sub('[^a-zA-Z0-9_]', '', new_name)
        clean_names[col] = new_name

    # Renommer les colonnes avec les nouveaux noms nettoyés
    df = df.rename(columns=clean_names)
    df = df.drop_duplicates(subset='incident_number')
    df = df.dropna()

    return df


##### Sélection des features #####

def features_selection(df:pd.DataFrame) -> pd.DataFrame:
    features = ['description','category_full','ci_name','location_full']
    id = 'incident_number'
    columns = []
    columns.append(id)
    for f in features :
        columns.append(f)
    df = df[columns]
    return df


##### Formation des embeddings (entrées du modèle) #####

def make_embeddings(df):
    docs = pd.Series(
            df["description"]
            + "\n\n"
            + "Category (Full):\n"
            + df["category_full"]
            + "\n\n"
            + "CI Name:\n"
            + df["ci_name"]
            + "\n\n"
            + "Location:\n"
            + df['location_full'])


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

    embeddings = embeddings_model.embed_documents(docs)

    # Convertir les embeddings en tableaux numpy
    embeddings_np = np.array(embeddings)

    # Convertir les tableaux numpy en listes de float
    embeddings_list = embeddings_np.tolist()

    embeddings_json = [json.dumps(embedding) for embedding in embeddings_list]

    result_docs = pd.DataFrame()
    result_docs["docs"] = docs
    result_docs["resulted_embeddings"] = embeddings_json
    result_docs.to_csv("api_ia/embeddings/result_docs.csv", index=False)

    df = pd.DataFrame({'incident_number':df['incident_number'],
                                "description": df["description"],
                                "category_full": df["category_full"],
                                "ci_name": df["ci_name"],
                                "location_full":df['location_full'],
                                "docs": result_docs["docs"],
                                "resulted_embeddings": result_docs["resulted_embeddings"]})


    return df 
