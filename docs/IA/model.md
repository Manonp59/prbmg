# Model Training 

This documentation outlines the steps involved in training a clustering model on IT incidents.

## Prerequisites

Before starting the training, ensure that the following are properly configured:

- **Python 3.7+**
- **Python Libraries**: Install the necessary libraries by running `pip install -r requirements-api_ia.txt`.
- **MLflow**: Set up MLflow for tracking experiments and models.
- **Azure OpenAI**: Ensure that your Azure OpenAI credentials are set up in your environment variables.
- **SQL Server**: Ensure that the SQL Server is running and accessible.

## Environment Setup

Ensure that the following environment variables are set:

- `MLFLOW_TRACKING_URI`: The URI where MLflow will log the experiment data.
- `NAMING_OPENAI_API_TYPE`, `NAMING_OPENAI_API_VERSION`, `NAMING_OPENAI_API_BASE`, `NAMING_OPENAI_API_KEY`: Credentials for Azure OpenAI.
- `API_DATABASE_SECRET_KEY`: API key to access the incidents data.
- `SQL_SERVER_URI`: Connection URI for your SQL Server instance.

## Training Pipeline Overview

The training pipeline consists of the following steps:

### 1. Fetching Incident Data

The `get_incidents()` function retrieves incident data from a remote API and loads it into a Pandas DataFrame.

- **Endpoint**: The data is fetched from `http://prbmg-api-database.francecentral.azurecontainer.io:8000/incidents/` using the API key provided.

### 2. Data Cleaning

The `clean_dataset()` function standardizes column names, removes duplicates, and handles missing values in the dataset.

- **Operations**:
  - Standardize column names by replacing spaces with underscores and converting to lowercase.
  - Remove duplicate rows based on the `incident_number` column.
  - Drop rows with missing values.

### 3. Feature Selection

The `features_selection()` function selects specific columns from the DataFrame that are relevant for feature analysis.

- **Selected Features**: 
  - `incident_number`
  - `description`
  - `category_full`
  - `ci_name`
  - `location_full`

### 4. Embedding Generation

The `make_embeddings()` function generates embeddings for the textual data in the DataFrame using a pre-trained SentenceTransformer model.

- **Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Process**:
  - Text from relevant columns is concatenated.
  - Embeddings are generated in batches and stored in the DataFrame.

### 5. Clustering Model Training

The `modelisation()` function trains a KMeans clustering model on the generated embeddings.

- **MLflow Tracking**:
  - MLflow logs the model, hyperparameters, and metrics such as the silhouette score.
  - The results, including the cluster labels, are stored in a SQL database.

- **KMeans Parameters**:
  - `n_clusters`: Number of clusters (configured via `cfg.model.n_clusters`).
  - `init`: Initialization method (`k-means++`).
  - `n_init`: Number of initializations (`80`).
  - `algorithm`: Algorithm used for clustering (`lloyd`).

### 6. Naming Clusters

The `make_naming()` function uses Azure OpenAI to generate descriptive titles for each cluster based on the incident descriptions.

- **Process**:
  - Incidents are grouped by their cluster labels.
  - For each cluster, the incident descriptions are concatenated and sent to Azure OpenAI’s GPT-4 to generate a summary title.
  - The generated titles are stored in the DataFrame.

### 7. Saving Results

The DataFrame containing the cluster labels and problem titles is saved to the SQL database, along with the original and processed data.

## Running the Training

To initiate the training pipeline, run the `training.py` script with a specified run name:

```bash
python main.py
```
This will execute the entire pipeline, logging the process in MLflow, and storing results in your SQL database.
