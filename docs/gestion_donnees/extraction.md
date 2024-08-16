# Incident and CI Location Data Processing

## Introduction

This document outlines the steps involved in extracting, cleaning, and importing incident data and CI location data into a database. The process involves reading data from different sources, applying various cleaning functions, and finally, integrating the cleaned data into a database.

## Command 
To execute the python script : 
```bash 
python -m api_database.scripts_database.data_extraction_cleaning
```

## Dependencies and external connections 

### Dependencies 
The following Python libraries are required to run the data processing script:
```python 
import pandas as pd 
import re 
import os 
from dotenv import load_dotenv
from sqlalchemy import create_engine
import pyodbc
```
### External connections 
The script connects to Azure SQL databases using connection strings created from environment variables.
```python 
load_dotenv() 

# Database configuration
driver = os.getenv("DRIVER")
server = os.getenv("AZURE_SERVER_NAME")
database = os.getenv("AZURE_DATABASE_NAME")
database_raw = os.getenv("AZURE_DATABASE_NAME_RAW")
username = os.getenv("AZURE_DATABASE_USERNAME")
password = os.getenv("AZURE_DATABASE_PASSWORD")
```

```python 
# Connection to Azure databases
azure_connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
engine = create_engine(azure_connection_string)

azure_connection_string_raw = f"mssql+pyodbc://{username}:{password}@{server}/{database_raw}?driver=ODBC+Driver+17+for+SQL+Server"
engine_raw = create_engine(azure_connection_string_raw)
```

## Workflow Overview

The overall process consists of three main stages:

1. **Extraction**: Data is extracted from the raw incidents database and a CSV file containing CI locations.
2. **Cleaning**: The extracted data is filtered, cleaned, and prepared for analysis.
3. **Import and Aggregation**: The cleaned data is saved to a new database and integrated with additional data.

## Extraction

### Raw Incidents Data
The incidents data is read from a table in the raw incidents database.

```python
table_name = 'incidents_raw'
df = pd.read_sql_table(table_name, con=engine_raw)
```

### CI Location Data 
CI location data is extracted from a CSV file using Pandas. 

```python 
ci_name = pd.read_csv('/home/utilisateur/DevIA/prbmg/api_database/data/brutes/CMDB.CSV', delimiter='\t')
```

The filter_dataframe() function is applied to filter and refine the incidents data.
Specific features are selected from the dataset to keep only the relevant columns using the features_selection() function.

## Cleaning 

The filter_dataframe() function is applied to filter and refine the incidents data.

Specific features are selected from the dataset to keep only the relevant columns using the features_selection() function.

Column names in the dataset are standardized and cleaned.

Duplicates based on the incident_number column are removed, and rows with any missing values are dropped to ensure data quality.

For CI locations, specific features are selected and the data is cleaned similarly to the incidents data.

The CI name column is renamed, duplicates are removed, and column names are cleaned.

## Import and aggregation 
The cleaned incidents data is imported into a new table named incidents in the database.
```python 
df.to_sql('incidents', con=engine, if_exists='append', index=False)
```

The cleaned CI location data is imported into a table named ci_location in the same database.
```python 
ci_name.to_sql('ci_location', con=engine, if_exists='append', index=False)
```

A new column location_full is added to the incidents table if it does not already exist.

The incidents table is updated with the location_full data by performing a join with the ci_location table on the ci_name column.
```sql
UPDATE incidents
SET location_full = l.location_full
FROM ci_location l
WHERE incidents.ci_name = l.ci_name;
```   


## Functions used

::: api_database.scripts_database.data_extraction_cleaning