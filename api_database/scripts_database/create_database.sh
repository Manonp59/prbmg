#!/bin/bash

# Variables
resourceGroupName="RG_PLATTEAU"
location="francecentral"
serverName="prbmg"
adminLogin="manon"
adminPassword=$(grep -oP '(?<=AZURE_DATABASE_PASSWORD=").*?(?=")' .env)
databaseName="prbmg-bdd"

# Connexion à Azure
az login

# Création d'un groupe de ressources
az group create --name $resourceGroupName --location $location

# Création d'un serveur SQL
az sql server create --name $serverName --resource-group $resourceGroupName --location $location --admin-user $adminLogin --admin-password $adminPassword

# Configuration du pare-feu
az sql server firewall-rule create --resource-group $resourceGroupName --server $serverName --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255

# Création d'une base de données
az sql db create --resource-group $resourceGroupName --server $serverName --name $databaseName --service-objective S0

echo "Le serveur SQL et la base de données ont été créés avec succès."
