# Load environment variables from .env file
set -a
source .env
set +a

#az login

az account set --subscription $SUBSCRIPTION_ID

az ml workspace create \
    --name $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

az configure --defaults workspace=$WORKSPACE_NAME group=$RESOURCE_GROUP location=$LOCATION 

az ml workspace show --query mlflow_tracking_uri
