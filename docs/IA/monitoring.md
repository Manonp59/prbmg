# Monitoring with MLflow

MLflow on Azure is used to track the training process, log model parameters, and monitor performance metrics.

To use MLflow on Azure, we need to create a Workspace Azure Machine Learning with the script <code>create_ws.sh</code> :

```bash
# Load environment variables from .env file
set -a
source .env
set +a

az login

az account set --subscription $SUBSCRIPTION_ID

az ml workspace create \
    --name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

az configure --defaults workspace=$WORKSPACE_NAME group=$RESOURCE_GROUP location=$LOCATION 

az ml workspace show --query mlflow_tracking_uri
```

## Configuration

- **Tracking URI**: Ensure that MLflow is configured with the correct tracking URI (MLFLOW_TRACKING_URI).
- **Experiments**: The clustering results are logged under the incidents_clustering experiment.
- **Metrics**: Key metrics like the silhouette score are logged to evaluate the model's performance.

We can visualize the results and monitor the model training process by access to the Azure Machine Learning Workspace.

## Monitoring dashboard 

To visualize these metrics, a **Streamlit dashboard** is available locally. It retrieves the model parameters and associated metrics from MLFlow on Azure. Then, it analyzes the distribution of incidents across clusters and compares the distribution in the training dataset with that in the predictions table using a bar chart. Finally, it displays the incidents on a scatter plot using PCA, with colors representing the clusters. One scatter plot is created for the training dataset and another for the predictions table.
