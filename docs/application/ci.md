# CI Pipeline Documentation

## Overview

This document provides an overview of the **Continuous Integration (CI)** pipeline configured for the project. The CI pipeline is defined using **GitHub Actions**, and it automates the process of testing the application upon code changes.

## Pipeline Configuration

The CI pipeline is triggered by a push event to the main branch. It consists of several steps, which are executed on an ubuntu-latest virtual environment.

### Workflow Configuration

```yaml

name: CI

on:
  push:
    branches:
    - main
```

The workflow is named "CI" and is triggered whenever changes are pushed to the main branch.

### Jobs

#### Test Job

The test job is responsible for running the tests and consists of the following steps:

- Checkout Code

```yaml

- name: Checkout code
  uses: actions/checkout@v2
```

This step checks out the code from the repository, allowing subsequent steps to access it.

- Set Up Python

```yaml

- name: Set up Python
  uses: actions/setup-python@v2
  with:
    python-version: '3.10'
```

This step sets up Python version 3.10 in the virtual environment.

- Install Requirements

```yaml

- name: Install requirements
  run: pip install -r requirements.txt
```
This step installs the required Python packages as specified in requirements.txt.

- Set Up Environment Variables

```yaml

- name: Set up environment variables
  run: |
    echo "API_IA_SECRET_KEY=${{ secrets.API_IA_SECRET_KEY }}" >> $GITHUB_ENV &&
    echo "AZURE_DATABASE_NAME=${{ secrets.AZURE_DATABASE_NAME }}" >> $GITHUB_ENV &&
    echo "AZURE_DATABASE_PASSWORD=${{ secrets.AZURE_DATABASE_PASSWORD }}" >> $GITHUB_ENV &&
    echo "AZURE_DATABASE_USERNAME=${{ secrets.AZURE_DATABASE_USERNAME }}" >> $GITHUB_ENV &&
    echo "AZURE_SERVER_NAME=${{ secrets.AZURE_SERVER_NAME }}" >> $GITHUB_ENV &&
    echo "DRIVER=${{ secrets.DRIVER }}" >> $GITHUB_ENV &&
    echo "EMBEDDING_API_KEY=${{ secrets.EMBEDDING_API_KEY }}" >> $GITHUB_ENV &&
    echo "EMBEDDING_AZURE_DEPLOYMENT=${{ secrets.EMBEDDING_AZURE_DEPLOYMENT }}" >> $GITHUB_ENV &&
    echo "EMBEDDING_AZURE_ENDPOINT=${{ secrets.EMBEDDING_AZURE_ENDPOINT }}" >> $GITHUB_ENV &&
    echo "EMBEDDING_OPENAI_API_VERSION=${{ secrets.EMBEDDING_OPENAI_API_VERSION }}" >> $GITHUB_ENV &&
    echo "NAMING_OPENAI_API_BASE=${{ secrets.NAMING_OPENAI_API_BASE }}" >> $GITHUB_ENV &&
    echo "NAMING_OPENAI_API_KEY=${{ secrets.NAMING_OPENAI_API_KEY }}" >> $GITHUB_ENV &&
    echo "NAMING_OPENAI_API_TYPE=${{ secrets.NAMING_OPENAI_API_TYPE }}" >> $GITHUB_ENV &&
    echo "API_DATABASE_SECRET_KEY=${{ secrets.API_DATABASE_SECRET_KEY }}" >> $GITHUB_ENV &&
    echo "MLFLOW_TRACKING_URI=${{ secrets.MLFLOW_TRACKING_URI}}" >> $GITHUB_ENV &&
    echo "AZURE_CLIENT_ID=${{ secrets.AZURE_CLIENT_ID}}" >> $GITHUB_ENV &&
    echo "AZURE_CLIENT_SECRET=${{ secrets.AZURE_CLIENT_SECRET}}" >> $GITHUB_ENV &&
    echo "AZURE_TENANT_ID=${{ secrets.AZURE_TENANT_ID}}" >> $GITHUB_ENV &&
    echo "APPLICATIONINSIGHTS_CONNECTION_STRING=${{ secrets.APPLICATIONINSIGHTS_CONNECTION_STRING}}" >> $GITHUB_ENV
```
This step sets up the environment variables required for the application. The values for these variables are retrieved from GitHub Secrets to ensure sensitive information is kept secure.

- Run Pytest Tests

```yaml

- name: Run Test
  run: pytest -v
```

This step runs the test suite using pytest, providing verbose output. It includes tests about AI API, database API, model training... All the tests of the project except those about the web app. 

- Run Django Tests

```yaml

- name: Run Django Tests
  working-directory: web_app
  run: python manage.py test
```
This step runs Django-specific tests by executing manage.py test within the web_app directory.

## Summary

This CI pipeline ensures that every push to the main branch triggers the testing process. It checks out the code, sets up the Python environment, installs dependencies, configures environment variables, and runs both general and Django-specific tests. This automated process helps maintain code quality and ensures that the application functions as expected with each update.