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
import sys
sys.path.append('/home/utilisateur/DevIA/prbmg')


load_dotenv()

# Add PYTHONPATH from .env to sys.path
sys.path.append(os.getenv('PYTHONPATH'))

load_dotenv()
st.set_page_config(layout="wide")

mlflow.set_tracking_uri(os.getenv('MLFLOW_TRACKING_URI'))

# Add the CSS styles for metric containers
st.markdown("""
<style>
.container {
    display: flex;
    align-content: space-between;
    justify-content: center;
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
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


st.markdown("<h1>Clustering Model Monitoring</h1>",unsafe_allow_html=True)

def get_best_run(experiment_name):
    experiment = mlflow.get_experiment_by_name(experiment_name)
    runs = mlflow.search_runs(experiment_ids=experiment.experiment_id)
    best_run = runs.loc[runs['metrics.silhouette score'].idxmax()]
    return best_run

experiment_name = "incidents_clustering"  # Remplacez par le nom de votre expérience
best_run = get_best_run(experiment_name)
st.markdown('<h2>Model Metrics and Params</h2>',unsafe_allow_html=True)
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




# Query for predictions dataset
query_predictions = "SELECT * FROM predictions"
data_predictions = query_db(query_predictions)

# Query for training dataset
query_training = "SELECT * FROM kmeans_30_trainingdataset_titles"
data_training = query_db(query_training)

# Combine data for comparison
def prepare_comparison_data(data, label):
    count_data = data['problem_title'].value_counts().reset_index()
    count_data.columns = ['Cluster', 'Count']
    count_data['Dataset'] = label
    total_count = count_data['Count'].sum()
    count_data['Percentage'] = (count_data['Count'] / total_count) * 100
    return count_data[['Cluster', 'Percentage', 'Dataset']]

data_predictions_comparison = prepare_comparison_data(data_predictions, 'Predictions')
data_training_comparison = prepare_comparison_data(data_training, 'Training')

# Concatenate both datasets for grouped bar chart
comparison_data = pd.concat([data_predictions_comparison, data_training_comparison])

# Create a grouped bar chart
fig = px.bar(
    comparison_data,
    x='Percentage',
    y='Cluster',
    color='Dataset',
    barmode='group',
    title='Cluster Proportions in Training Dataset vs. Predictions',
    labels={'Percentage': 'Percentage of Incidents'},
    text='Percentage',
    orientation='h'
)

fig.update_layout(xaxis_title='Percentage of incidents', yaxis_title='Clusters',height=1000)

# Display the bar chart
st.plotly_chart(fig)


st.markdown('<h2>Incidents Clustering Visualization : Training dataset</h2>',unsafe_allow_html=True)

# Affichage du graphique dans Streamlit

data_training['resulted_embeddings'] = data_training['resulted_embeddings'].apply(lambda x: np.array(eval(x)))
scaler = StandardScaler()
scaled_embeddings = scaler.fit_transform(list(data_training['resulted_embeddings']))
pca = PCA(n_components=2)
principal_components = pca.fit_transform(scaled_embeddings)
df = pd.DataFrame(principal_components, columns=['PC1', 'PC2'])
df['Cluster'] = data_training['problem_title']

fig = px.scatter(df, x='PC1', y='PC2', color='Cluster', hover_data=['PC1', 'PC2', 'Cluster'])
fig.update_layout(title='Clusters for training dataset', 
                  xaxis_title='Principal Component 1', yaxis_title='Principal Component 2')



st.plotly_chart(fig)


# Convert the embeddings from string to numpy array
data_predictions['resulted_embeddings'] = data_predictions['resulted_embeddings'].apply(lambda x: np.array(eval(x)))

# Flatten the embeddings if they are multi-dimensional
# For example, if each embedding is of shape (n, m), you can flatten it to shape (n * m)
data_predictions['resulted_embeddings'] = data_predictions['resulted_embeddings'].apply(lambda x: x.flatten())

# Stack all embeddings into a single 2D numpy array
embeddings = np.stack(data_predictions['resulted_embeddings'].values)
scaler = StandardScaler()
scaled_embeddings = scaler.fit_transform(list(data_predictions['resulted_embeddings']))
pca = PCA(n_components=2)
principal_components = pca.fit_transform(scaled_embeddings)
df = pd.DataFrame(principal_components, columns=['PC1', 'PC2'])
df['Cluster'] = data_predictions['problem_title']

fig = px.scatter(df, x='PC1', y='PC2', color='Cluster', hover_data=['PC1', 'PC2', 'Cluster'])
fig.update_layout(title='Clusters for predictions', 
                  xaxis_title='Principal Component 1', yaxis_title='Principal Component 2')


st.plotly_chart(fig)