# Tests 

The automated tests for the model, which verify the quality of the datasets and the model training, are located in the file  <code>test_quality.py</code>. 
The automated tests that check the API endpoints are in the file <code>test_endpoints.py</code>.

The testing framework used is **pytest**. nd the tests are automated in the **Continuous Integration** pipeline.

## Dependencies 

All necessary dependencies are listed in the <code>requirements-api_ia.txt</code>. 

## Test quality

```bash
pytest -v --cov=api_ia/clustering_model/tests/test_quality.py
```

The <code> --cov</code> argument calculates the test coverage.

::: api_ia.clustering_model.tests.test_quality


## Test endpoints 

```bash
pytest -v --cov=api_ia/api/tests/test_endpoints.py
```

::: api_ia.api.tests.test_endpoints


