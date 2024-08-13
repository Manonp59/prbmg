import pandas as pd 
import re 
import os 
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pyodbc

load_dotenv() 

driver = os.getenv("DRIVER")
server = os.getenv("AZURE_SERVER_NAME")
database = os.getenv("AZURE_DATABASE_NAME")
database_raw = os.getenv("AZURE_DATABASE_NAME_RAW")
username = os.getenv("AZURE_DATABASE_USERNAME")
password = os.getenv("AZURE_DATABASE_PASSWORD")

azure_connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(azure_connection_string)

azure_connection_string_raw = f"mssql+pyodbc://{username}:{password}@{server}/{database_raw}?driver=ODBC+Driver+17+for+SQL+Server"
engine_raw = create_engine(azure_connection_string_raw)

def filter_dataframe(df) -> pd.DataFrame:
    """
    This function takes a DataFrame as input and returns a new DataFrame containing the rows that match the criteria
    "Origin of Request" = "Monitoring" and "Requesting Person" = "REST API - ZABBIX".

    Args:
        df (pd.DataFrame): The input DataFrame to filter.

    Returns:
        pd.DataFrame: A new DataFrame containing the rows regarding the chosen mask.
    """
    mask_origin_request = df["Origin of Request"] == "Monitoring"
    mask_requesting_person = df["Requesting Person"] == "REST API - ZABBIX"

    
    df_zabbix = df[mask_origin_request & mask_requesting_person]

    return df_zabbix


def features_selection(df:pd.DataFrame, features:list, id:str) -> pd.DataFrame:
    columns = []
    columns.append(id)
    for f in features :
        columns.append(f)
    print(columns)
    df = df[columns]
    return df
    

def clean_column_names(df:pd.DataFrame)  -> pd.DataFrame:
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

    return df


table_name = 'incidents_raw'
df = pd.read_sql_table(table_name, con=engine_raw)


df = filter_dataframe(df)


features = ['Description','Category (Full)','CI: Name', 'Owner Group','Urgency', 'Priority', 'SLA']
id = 'Incident Number'
df = features_selection(df,features, id)
df = clean_column_names(df)

df = df.drop_duplicates(subset='incident_number')
df = df.dropna()
df.to_sql('incidents',con=engine, if_exists='append',index=False)


ci_name = pd.read_csv('/home/utilisateur/DevIA/prbmg/api_database/data/brutes/CMDB.CSV',delimiter='\t')
print(ci_name.columns)
features = ["Location (Full)"]
id = 'Name'

ci_name = features_selection(ci_name, features, id)

ci_name = ci_name.rename(columns={'Name':'CI: Name'})
ci_name = ci_name.drop_duplicates(subset='CI: Name')
ci_name = clean_column_names(ci_name)

ci_name.to_sql('ci_location',con=engine, if_exists='append',index=False)



conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)


with conn.cursor() as cursor:
    add_column_query = """
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS
                   WHERE TABLE_NAME = 'incidents' AND COLUMN_NAME = 'location_full')
    BEGIN
        ALTER TABLE incidents ADD location_full VARCHAR(300);
    END
    """
    cursor.execute(add_column_query)
    conn.commit()

with conn.cursor() as cursor:
    update_query = """
    UPDATE incidents
    SET location_full = l.location_full
    FROM ci_location l
    WHERE incidents.ci_name = l.ci_name;
    """
    cursor.execute(update_query)
    conn.commit()

