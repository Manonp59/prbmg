The API IA enables the use of the clustering model to obtain cluster number for new incidents. It is developed using the FastAPI framework.

## Authentication

The REST API designed to provide project data is protected by an API key required for all requests. The verification of this API key is handled by the **verify_api_key()** function.

::: api_ia.api.main.verify_api_key

## Endpoint

::: api_ia.api.main.predict