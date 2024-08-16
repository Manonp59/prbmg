# Tests 

Les tests automatisés du modèle qui permettent de vérifier la qualité des jeux de données et de l’entraînement du modèle sont dans le fichier <code>test_quality.py</code>. 

Le framework de test utilisé est **pytest**. Les tests sont automatisés dans le pipeline de **Continuous Integration**.

## Dependencies 

All necessary dependencies are listed in the <code>requirements-api_ia.txt</code>. 

## Run the tests 

```bash
pytest -v --cov=api_ia/clustering_model/tests/test_quality.py
```

The <code> --cov</code> argument calculates the test coverage.

## Test functions

::: api_ia.clustering_model.tests.test_quality



