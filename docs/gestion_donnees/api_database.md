The API Database enables the use of incident data from our database throughout the entire project. It is developed using the FastAPI framework.

## Authentication

The REST API designed to provide project data is protected by an API key required for all requests. The verification of this API key is handled by the **verify_api_key()** function.

## Endpoints

::: api_database.api.main