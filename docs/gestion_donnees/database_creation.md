# Azure SQL Server and Database Creation Script

## Introduction

This document provides a step-by-step guide to creating an Azure SQL Server and database using a Bash script. The script automates the creation of the resource group, SQL server, firewall rules, and the database within Microsoft Azure.

## Script Overview

### Script Name: `create_azure_sql_db.sh`

This script performs the following operations:
1. Imports environment variables from a `.env` file.

```bash
set -a
source .env
set +a
```

2. Logs into the Azure CLI.

```bash
az login
```

3. Creates a resource group in the specified Azure region.

```bash
az group create --name $resourceGroupName --location $location
```

4. Creates a SQL server with an admin user.
```bash
az sql server create --name $serverName --resource-group $resourceGroupName --location $location --admin-user $adminLogin --admin-password $adminPassword
```

5. Configures the firewall to allow all IP addresses to connect.
```bash
az sql server firewall-rule create --resource-group $resourceGroupName --server $serverName --name AllowAll --start-ip-address 0.0.0.0 --end-ip-address 255.255.255.255
```

6. Creates a SQL database with a specified service tier.
```bash
az sql db create --resource-group $resourceGroupName --server $serverName --name $databaseName --service-objective S0
```

## Prerequisites

Before running the script, ensure that:

- You have the Azure CLI installed and configured on your system.
- The .env file is present in the same directory as the script, containing the necessary environment variables (e.g., AZURE_DATABASE_PASSWORD).

## Command 

Ensure that you have permissions to run the script: 
```bash
chmod +x create_database.sh
```

To execute the script : 
```bash 
create_database.sh
```

## RGPD 
Our database doesn't include personal informations. 