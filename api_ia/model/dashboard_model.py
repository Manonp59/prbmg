from api_ia.clustering_model.utils import create_sql_server_engine, query_db
import streamlit as st 
import pandas as pd 
import plotly.express as px
import mlflow 
import os 
import numpy as np 
from dotenv import load_dotenv
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

load_dotenv()
st.set_page_config(layout="wide")
mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))
st.title('Clustering Model Monitoring ')


def get_best_run(experiment_name):
    experiment = mlflow.get_experiment_by_name(experiment_name)
    runs = mlflow.search_runs(experiment_ids=experiment.experiment_id)
    best_run = runs.loc[runs['metrics.silhouette score'].idxmax()]
    return best_run

experiment_name = "incidents_clustering"  # Remplacez par le nom de votre expérience
best_run = get_best_run(experiment_name)
st.write('Model Metrics and Params')
st.markdown(f"""
<div class="container">
    <div class="metric-container">
        <div class="metric-name">Number of clusters</div>
        <div class="metric-value">{best_run['params.n_clusters']}</div>
    </div>
    <div class="metric-container">
        <div class="metric-name">Algorithm</div>
        <div class="metric-value">{best_run['params.algorithm']}</div>
    </div>  
    <div class="metric-container">
        <div class="metric-name">n_init</div>
        <div class="metric-value">{best_run['params.n_init']}</div>
    </div>
    <div class="metric-container">
        <div class="metric-name">Init</div>
        <div class="metric-value">{best_run['params.init']}</div>
    </div>
    <div class="metric-container">
        <div class="metric-name">Silhouette score</div>
        <div class="metric-value">{best_run['metrics.silhouette score'].round(2)}</div>
    </div>     
            
            """, unsafe_allow_html=True)
# Add the CSS styles for metric containers
st.markdown("""
<style>
.container {
    display: flex;
    align-content: space-between 
}
.metric-container {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    margin-right: 10px;
    width: 300px;
    height: 150px;
    text-align: center;
    display: inline-block;
    vertical-align: top;
}
.metric-name {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 24px;
    font-weight: bold;
    color: #007bff;
}
</style>
""", unsafe_allow_html=True)

query = "SELECT * FROM kmeans30_trainingdataset_titles"

data = query_db(query)

fig = px.pie(data, names='problem_title', title='Clusters repartition on training dataset')

# Affichage du graphique dans Streamlit
st.plotly_chart(fig)


data['resulted_embeddings'] = data['resulted_embeddings'].apply(lambda x: np.array(eval(x)))
scaler = StandardScaler()
scaled_embeddings = scaler.fit_transform(list(data['resulted_embeddings']))
pca = PCA(n_components=2)
principal_components = pca.fit_transform(scaled_embeddings)
df = pd.DataFrame(principal_components, columns=['PC1', 'PC2'])
df['Cluster'] = data['problem_title']

fig = px.scatter(df, x='PC1', y='PC2', color='Cluster', hover_data=['PC1', 'PC2', 'Cluster'])
fig.update_layout(title='PCA Scatter Plot of Incidents with Clusters', 
                  xaxis_title='Principal Component 1', yaxis_title='Principal Component 2')

# Streamlit app
st.title('Incidents Clustering Visualization with PCA and Plotly')
st.plotly_chart(fig)

query = "SELECT * FROM predictions"

data = query_db(query)

fig = px.pie(data, names='problem_title', title='Clusters repartition on predictions')

# Affichage du graphique dans Streamlit
st.plotly_chart(fig)


scaler = StandardScaler()
scaled_embeddings = scaler.fit_transform(data['resulted_embeddings'])
pca = PCA(n_components=2)
principal_components = pca.fit_transform(scaled_embeddings)
df = pd.DataFrame(principal_components, columns=['PC1', 'PC2'])
df['Cluster'] = data['problem_title']

fig = px.scatter(df, x='PC1', y='PC2', color='Cluster', hover_data=['PC1', 'PC2', 'Cluster'])
fig.update_layout(title='PCA Scatter Plot of Incidents with Clusters', 
                  xaxis_title='Principal Component 1', yaxis_title='Principal Component 2')

# Streamlit app
st.title('Incidents Clustering Visualization with PCA and Plotly')
st.plotly_chart(fig)