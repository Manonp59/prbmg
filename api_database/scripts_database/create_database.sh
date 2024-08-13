#!/bin/bash

# import .env variables
set -a
source .env
set +a

# Variables

resourceGroupName="RG_PLATTEAU"
location="francecentral"
serverName="prbmg-server"
adminLogin="manon"
adminPassword=$AZURE_DATABASE_PASSWORD
databaseName="prbmg-bdd"

# Connection to Azure
az login

# Resource group creation
az group create --name $resourceGroupName --location $location

# SQL server creation
az sql server create --name $serverName --resource-group $resourceGroupName --location $location --admin-user $adminLogin --admin-password $adminPassword

# Firewall configuration
az sql server firewall-rule create --resource-group $resourceGroupName --server $serverName --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255

# Database creation
az sql db create --resource-group $resourceGroupName --server $serverName --name $databaseName --service-objective S0

echo "SQL server and database has been created successfully."
