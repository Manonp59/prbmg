import pandas as pd 
import re
from langchain_openai import AzureOpenAIEmbeddings
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine
import json
from api_ia.clustering_model.utils import create_sql_server_conn, create_sql_server_engine
from sentence_transformers import SentenceTransformer



def clean_dataset(df)  -> pd.DataFrame:
    """
    Cleans a DataFrame by standardizing column names and removing duplicates and missing values.

    This function performs the following operations on the DataFrame:
    1. Standardizes column names by replacing spaces with underscores, converting to lowercase, 
       and removing special characters.
    2. Removes duplicate rows based on the 'incident_number' column.
    3. Drops rows with any missing values.

    Args:
        df (pd.DataFrame): The DataFrame to be cleaned.

    Returns:
        pd.DataFrame: The cleaned DataFrame with standardized column names, no duplicates, and no missing values.

    Raises:
        KeyError: If the 'incident_number' column is not present in the DataFrame.
    """
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


def features_selection(df:pd.DataFrame) -> pd.DataFrame:
    """
    Selects specific columns from the DataFrame for feature analysis.

    This function retains only the columns specified in the `features` list along with the identifier column (`id`).
    It returns a DataFrame with only these selected columns.

    Args:
        df (pd.DataFrame): The DataFrame from which columns will be selected.

    Returns:
        pd.DataFrame: A DataFrame containing only the specified columns: 'incident_number', 'description', 
                      'category_full', 'ci_name', and 'location_full'.

    Notes:
        - Ensure that the DataFrame contains the columns specified in the `features` list and the identifier column.
    """
    features = ['description','category_full','ci_name','location_full']
    id = 'incident_number'
    columns = []
    columns.append(id)
    for f in features :
        columns.append(f)
    df = df[columns]
    return df


##### Formation des embeddings (entrées du modèle) #####

# def make_embeddings(df):
#     docs = pd.Series(
#             df["description"]
#             + "\n\n"
#             + "Category (Full):\n"
#             + df["category_full"]
#             + "\n\n"
#             + "CI Name:\n"
#             + df["ci_name"]
#             + "\n\n"
#             + "Location:\n"
#             + df['location_full'])


#     azure_deployment = os.getenv('EMBEDDING_AZURE_DEPLOYMENT')
#     openai_api_version = os.getenv('EMBEDDING_OPENAI_API_VERSION')
#     api_key = os.getenv('EMBEDDING_API_KEY')
#     azure_endpoint = os.getenv('EMBEDDING_AZURE_ENDPOINT')

#     embeddings_model = AzureOpenAIEmbeddings(
#         azure_deployment=azure_deployment,
#         openai_api_version=openai_api_version,
#         api_key = api_key,
#         azure_endpoint = azure_endpoint
#     )

#     batch_size = 250
#     embeddings = []

#     for i in range(0, len(docs), batch_size):
#         print(i)
#         start_batch = i
#         end_batch = i + batch_size
#         batch = docs[start_batch:end_batch]
#         batch_embeddings = embeddings_model.embed_documents(batch)
#         embeddings.extend(batch_embeddings)
#         if i + batch_size < len(docs):
#             time.sleep(5)
    

#     # Convertir les embeddings en tableaux numpy
#     embeddings_np = np.array(embeddings)

#     # Convertir les tableaux numpy en listes de float
#     embeddings_list = embeddings_np.tolist()

#     embeddings_json = [json.dumps(embedding) for embedding in embeddings_list]

#     result_docs = pd.DataFrame()
#     result_docs["docs"] = docs
#     result_docs["resulted_embeddings"] = embeddings_json
#     result_docs.to_csv("api_ia/embeddings/result_docs.csv", index=False)

#     df = pd.DataFrame({'incident_number':df['incident_number'],
#                                 "description": df["description"],
#                                 "category_full": df["category_full"],
#                                 "ci_name": df["ci_name"],
#                                 "location_full":df['location_full'],
#                                 "docs": result_docs["docs"],
#                                 "resulted_embeddings": result_docs["resulted_embeddings"]})


#     return df 

def make_embeddings(df) -> pd.DataFrame:
    """
    Generates embeddings for textual data in the DataFrame.

    This function creates embeddings for each row in the DataFrame based on the concatenated textual columns:
    'description', 'category_full', 'ci_name', and 'location_full'. The embeddings are computed using a pre-trained
    SentenceTransformer model. Results are returned in a DataFrame including the original columns and the computed
    embeddings.

    Args:
        df (pd.DataFrame): The input DataFrame with columns 'incident_number', 'description', 'category_full',
                           'ci_name', and 'location_full'.

    Returns:
        pd.DataFrame: A DataFrame containing the original columns along with new columns:
                      - 'docs': Concatenated text used for embedding generation.
                      - 'resulted_embeddings': JSON-encoded embeddings for each row.
    """
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
    
    model_paraphrase = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

    batch_size = 250
    embeddings = []
    
    for i in range (0,len(docs), batch_size):
        start_batch = i 
        end_batch = i + batch_size
        batch = docs[start_batch:end_batch]

        batch_df = pd.Series([str (doc) for doc in batch], index=range(len(batch)))
        batch_embeddings = model_paraphrase.encode(batch_df)
        embeddings.extend(batch_embeddings)
        
    embeddings_np = np.array(embeddings)
    embeddings_list = embeddings_np.tolist()
    embeddings_json = [json.dumps(embedding) for embedding in embeddings_list]
    result_docs = pd.DataFrame()
    result_docs["docs"] = docs
    result_docs["resulted_embeddings"] = embeddings_json
    

    df = pd.DataFrame({'incident_number':df['incident_number'],
                                "description": df["description"],
                                "category_full": df["category_full"],
                                "ci_name": df["ci_name"],
                                "location_full":df['location_full'],
                                "docs": result_docs["docs"],
                                "resulted_embeddings": result_docs["resulted_embeddings"]})


    return df 
