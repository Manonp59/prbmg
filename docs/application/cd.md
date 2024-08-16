# Continuous Deployment Pipeline Documentation

This document describes the **Continuous Deployment (CD)** pipeline defined in the **GitHub Actions** workflow for deploying the application to Azure Container Instances.

## Overview

The CD pipeline is triggered on every push to the `main` branch. It performs the following steps: 

- Checks out the repository code.
- Sets up Docker Buildx for building multi-platform Docker images.
- Builds and pushes Docker images using Docker Compose.
- Logs in to Azure.
- Deploys various services to Azure Container Instances:
    - API IA
    - API Database
    - Web App

## Pipeline Steps

### 1. Checkout Repository

```yaml
- name: Checkout repository
  uses: actions/checkout@v2
```

### 2. Set Up Docker Buildx

```yaml

- name: Set up Docker Buildx
  uses: docker/setup-buildx-action@v1
```

Sets up Docker Buildx, which is necessary for building multi-platform Docker images.

### 3. Build and Push Docker Images Using Docker Compose

```yaml

- name: Build and Push Docker Images using Docker Compose
  env:
    DOCKERHUB_USERNAME: ${{ secrets.DOCKERHUB_USERNAME }}
    APPLICATIONINSIGHTS_CONNECTION_STRING: ${{ secrets.APPLICATIONINSIGHTS_CONNECTION_STRING }}
  run: |
    echo "${{ secrets.DOCKERHUB_PASSWORD }}" | docker login -u ${{ secrets.DOCKERHUB_USERNAME }} --password-stdin
    docker compose build
    docker compose push
```
Logs in to Docker Hub, builds Docker images using Docker Compose, and pushes them to Docker Hub.

### 4. Azure Login

```yaml

- name: Azure Login
  uses: azure/login@v1
  with:
    creds: ${{ secrets.AZURE_CREDENTIALS }}
```
Logs in to Azure using credentials stored in GitHub Secrets.

### 5. Deploy API IA to Azure Container Instances

```yaml
- name: Deploy API IA to Azure Container Instances
  uses: azure/aci-deploy@v1
  with:
    resource-group: ${{ secrets.RESOURCE_GROUP }}
    dns-name-label: prbmg-api-ia
    image: docker.io/manon29/api_ia:latest
    registry-login-server: docker.io
    registry-username: ${{ secrets.DOCKERHUB_USERNAME }}
    registry-password: ${{ secrets.DOCKERHUB_PASSWORD }}
    name: prbmg-api-ia
    location: francecentral
    ports: '8001'
    secure-environment-variables: |
      API_IA_SECRET_KEY=${{ secrets.API_IA_SECRET_KEY }}
      EMBEDDING_API_KEY=${{ secrets.EMBEDDING_API_KEY }}
      EMBEDDING_AZURE_DEPLOYMENT=${{ secrets.EMBEDDING_AZURE_DEPLOYMENT }}
      EMBEDDING_AZURE_ENDPOINT=${{ secrets.EMBEDDING_AZURE_ENDPOINT }}
      EMBEDDING_OPENAI_API_VERSION=${{ secrets.EMBEDDING_OPENAI_API_VERSION }}
      NAMING_OPENAI_API_BASE=${{ secrets.NAMING_OPENAI_API_BASE }}
      NAMING_OPENAI_API_KEY=${{ secrets.NAMING_OPENAI_API_KEY }}
      NAMING_OPENAI_API_TYPE=${{ secrets.NAMING_OPENAI_API_TYPE }}
      API_DATABASE_SECRET_KEY=${{ secrets.API_DATABASE_SECRET_KEY }}
      AZURE_DATABASE_NAME=${{ secrets.AZURE_DATABASE_NAME }}
      AZURE_DATABASE_PASSWORD=${{ secrets.AZURE_DATABASE_PASSWORD }}
      AZURE_DATABASE_USERNAME=${{ secrets.AZURE_DATABASE_USERNAME }}
      AZURE_SERVER_NAME=${{ secrets.AZURE_SERVER_NAME }}
      DRIVER=${{ secrets.DRIVER }}
      MLFLOW_TRACKING_URI=${{ secrets.MLFLOW_TRACKING_URI}}
      AZURE_CLIENT_ID=${{ secrets.AZURE_CLIENT_ID}}
      AZURE_CLIENT_SECRET=${{ secrets.AZURE_CLIENT_SECRET}}
      AZURE_TENANT_ID=${{ secrets.AZURE_TENANT_ID}}
```
Deploys the API IA service to Azure Container Instances with the necessary environment variables for configuration.

### 6. Deploy API Database to Azure Container Instances

```yaml

- name: Deploy API Database to Azure Container Instances
  uses: azure/aci-deploy@v1
  with:
    resource-group: ${{ secrets.RESOURCE_GROUP }}
    dns-name-label: prbmg-api-database
    image: docker.io/manon29/api_database:latest
    registry-login-server: docker.io
    registry-username: ${{ secrets.DOCKERHUB_USERNAME }}
    registry-password: ${{ secrets.DOCKERHUB_PASSWORD }}
    name: prbmg-api-database
    location: francecentral
    ports: '8000'
    secure-environment-variables: |
      AZURE_DATABASE_NAME=${{ secrets.AZURE_DATABASE_NAME }}
      AZURE_DATABASE_PASSWORD=${{ secrets.AZURE_DATABASE_PASSWORD }}
      AZURE_DATABASE_USERNAME=${{ secrets.AZURE_DATABASE_USERNAME }}
      AZURE_SERVER_NAME=${{ secrets.AZURE_SERVER_NAME }}
      DRIVER=${{ secrets.DRIVER }}
      API_DATABASE_SECRET_KEY=${{ secrets.API_DATABASE_SECRET_KEY }}
```

Deploys the API Database service to Azure Container Instances with the required environment variables.

### 7. Deploy Web App to Azure Container Instances

```yaml
- name: Deploy Web App to Azure Container Instances
  uses: azure/aci-deploy@v1
  with:
    resource-group: ${{ secrets.RESOURCE_GROUP }}
    dns-name-label: prbmg-web-app
    image: docker.io/manon29/web_app:latest
    registry-login-server: docker.io
    registry-username: ${{ secrets.DOCKERHUB_USERNAME }}
    registry-password: ${{ secrets.DOCKERHUB_PASSWORD }}
    name: prbmg-web-app
    location: francecentral
    ports: '8002'
    secure-environment-variables: |
      API_IA_SECRET_KEY=${{ secrets.API_IA_SECRET_KEY }}
      API_DATABASE_SECRET_KEY=${{ secrets.API_DATABASE_SECRET_KEY }}
      AZURE_DATABASE_NAME=${{ secrets.AZURE_DATABASE_NAME }}
      AZURE_DATABASE_PASSWORD=${{ secrets.AZURE_DATABASE_PASSWORD }}
      AZURE_DATABASE_USERNAME=${{ secrets.AZURE_DATABASE_USERNAME }}
      AZURE_SERVER_NAME=${{ secrets.AZURE_SERVER_NAME }}
      DRIVER=${{ secrets.DRIVER }}
      APPLICATIONINSIGHTS_CONNECTION_STRING=${{ secrets.APPLICATIONINSIGHTS_CONNECTION_STRING}}
```
Deploys the Web App to Azure Container Instances with the necessary secure environment variables.


