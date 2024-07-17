# Load environment variables from .env file
set -o allexport
source .env
set +o allexport

# Azure login and set subscription
az login
az account set --subscription $SUBSCRIPTION_ID
az extension add -n ml
# Create MLflow workspace
az ml workspace create \
    -n $WORKSPACE_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

az configure --defaults workspace=$WORKSPACE_NAME group=$RESOURCE_GROUP location=$LOCATION 

az ml workspace show -n $WORKSPACE_NAME --resource-group $RESOURCE_GROUP 