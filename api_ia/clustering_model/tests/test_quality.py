import pytest
import pandas as pd
from api_ia.embeddings.embeddings import clean_dataset, features_selection
from api_ia.clustering_model.clustering import modelisation
from api_ia.api.utils import connect_to_sql_server
import pytest
from pandas.testing import assert_frame_equal
from api_ia.embeddings.embeddings import clean_dataset, features_selection, make_embeddings
from unittest.mock import Mock, MagicMock
import numpy as np


@pytest.fixture
def mock_connection():
    # Créer un objet mock pour la connexion
    mock_conn = MagicMock()

    # Configurer la méthode execute pour retourner un objet mock avec la méthode description
    mock_cursor = MagicMock()
    mock_cursor.description = [('incident_number',), ('description',), ('category_full',), ('ci_name',), ('location_full',), ('owner_group',), ('urgency',), ('priority',), ('SLA',)]
    mock_conn.return_value.cursor.return_value.__enter__.return_value.description = mock_cursor

    # Configurer la méthode execute pour retourner des données simulées
    mock_data = [
        (0, 'some description', 'cat1', 'ci1', 'Paris', 'og1', 'medium', 1, '4h office'),
        (1, 'description example', 'cat2', 'ci2', 'Lestrem', 'og2', 'high', 2, '8h office'),
        (1, 'descritption', 'cat3', 'ci3', 'La Madeleine', 'og3', 'low', 3, '4h office'),
        (3, 'some text', 'cat3', 'ci4', 'Lestrem', 'og4', 'medium', 4, '8h office'),
        (4, 'text example', 'cat4', 'ci5', 'Lestrem', 'og5', 'high', 5, '8h office')
    ]
    mock_conn.return_value.cursor.return_value.__enter__.return_value.fetchall.return_value = mock_data

    return mock_conn

def test_clean_dataset(mock_connection):
    mock_data = {
                    'incident number' :[0,1,1,3,4],
                    'description' : ['some description', 'description example','description example', 'some text','text example'],
                    'category (Full)' : ['cat1','cat2','cat2','cat3','cat4'],
                    'ci_name' : ['ci1','ci2','ci2','ci4','ci5'],
                    'location_full': ['Paris','Lestrem','Lestrem','Lestrem','Lestrem'],
                    'owner_group' : ['og1','og2','og2','og4','og5'],
                    'urgency' : ['medium','high','high','medium','high'],
                    'priority' : [1,2,3,4,5],
                    'SLA' : ['4h office', '8h office','8h office','8h office','8h office']
                }
    mock_df = pd.DataFrame(mock_data)
    result_df = clean_dataset(mock_df)

    # Données attendues
    expected_data = {
                    'incident_number' :[0,1,3,4],
                    'description' : ['some description', 'description example', 'some text','text example'],
                    'category_full' : ['cat1','cat2','cat3','cat4'],
                    'ci_name' : ['ci1','ci2','ci4','ci5'],
                    'location_full': ['Paris','Lestrem','Lestrem','Lestrem'],
                    'owner_group' : ['og1','og2','og4','og5'],
                    'urgency' : ['medium','high','medium','high'],
                    'priority' : [1,2,4,5],
                    'sla' : ['4h office', '8h office','8h office','8h office']
                }

    # Créer un DataFrame Pandas à partir des données attendues
    expected_df = pd.DataFrame(expected_data)

    # Vérifier que les données retournées sont identiques aux données attendues
    expected_df.reset_index(drop=True, inplace=True)
    result_df.reset_index(drop=True, inplace=True)
    assert_frame_equal(result_df, expected_df)

def test_features_selection():
    # Données d'entrée pour la fonction features_selection
    input_data = {
                    'incident_number' :[0,1,3,4],
                    'description' : ['some description', 'description example', 'some text','text example'],
                    'category_full' : ['cat1','cat2','cat3','cat4'],
                    'ci_name' : ['ci1','ci2','ci4','ci5'],
                    'location_full': ['Paris','Lestrem','Lestrem','Lestrem'],
                    'owner_group' : ['og1','og2','og4','og5'],
                    'urgency' : ['medium','high','medium','high'],
                    'priority' : [1,2,4,5],
                    'SLA' : ['4h office', '8h office','8h office','8h office']
                }

    # Créer un DataFrame Pandas à partir des données d'entrée
    input_df = pd.DataFrame(input_data)

    # Appel de la fonction features_selection avec les données d'entrée
    result_df = features_selection(input_df)

    # Colonnes attendues dans le DataFrame résultant
    expected_columns = ['incident_number', 'description', 'category_full', 'ci_name', 'location_full']

    # Vérifier que les colonnes du DataFrame résultant sont les mêmes que celles attendues
    assert result_df.columns.tolist() == expected_columns

def test_make_embeddings():
    # Données d'entrée pour la fonction make_embeddings
    input_data = {
        'incident_number': [1, 2, 3],
        'description': ['Desc1', 'Desc2', 'Desc3'],
        'category_full': ['Cat1', 'Cat2', 'Cat3'],
        'ci_name': ['CI1', 'CI2', 'CI3'],
        'location_full': ['Loc1', 'Loc2', 'Loc3']
    }

    # Créer un DataFrame Pandas à partir des données d'entrée
    input_df = pd.DataFrame(input_data)

    # Appel de la fonction make_embeddings avec les données d'entrée
    result_df = make_embeddings(input_df)

    # Colonnes attendues dans le DataFrame résultant
    expected_columns = ['incident_number', 'description', 'category_full', 'ci_name', 'location_full', 'docs', 'resulted_embeddings']

    # Vérifier que les colonnes du DataFrame résultant sont les mêmes que celles attendues
    assert result_df.columns.tolist() == expected_columns


@pytest.fixture
def sample_dataframe():
    data = {
        "resulted_embeddings": ['[0.1, 0.2, 0.3]', '[0.4, 0.5, 0.6]', '[0.7, 0.8, 0.9]']
    }
    return pd.DataFrame(data)


def test_modelisation(mocker, sample_dataframe):
    # Mock create_sql_server_engine
    mock_engine = mocker.MagicMock()
    mocker.patch('api_ia.api.utils.connect_to_sql_server', return_value=mock_engine)
    
    # Mock mlflow
    mock_mlflow = mocker.patch('api_ia.clustering_model.clustering.mlflow')
    mock_experiment = mocker.MagicMock()
    mock_experiment.experiment_id = 1
    mock_mlflow.get_experiment_by_name.return_value = mock_experiment
    mock_run = mocker.MagicMock()
    mock_mlflow.start_run.return_value.__enter__.return_value = mock_run
    
    # Mock cfg
    mock_cfg = mocker.MagicMock()
    mock_cfg.model.n_clusters = 2
    mocker.patch('api_ia.clustering_model.clustering.cfg', mock_cfg)
    
    # Call the function
    run_id, df_result = modelisation(sample_dataframe, 'test_run')
    
    # Assertions
    assert run_id == mock_run.info.run_id
    assert 'clusters' in df_result.columns
    assert len(df_result) == 3
    assert np.all(df_result['clusters'].isin([0, 1]))
    
    # Verify mlflow calls
    mock_mlflow.get_experiment_by_name.assert_called_once_with("incidents_clustering")
    mock_mlflow.create_experiment.assert_not_called()
    mock_mlflow.start_run.assert_called_once_with(experiment_id=1, run_name='kmeans_2')
    mock_mlflow.sklearn.log_model.assert_called_once()
    mock_mlflow.log_params.assert_called_once_with({"n_clusters": 2})
    mock_mlflow.set_tag.assert_called_once_with("model", "kmeans")
    mock_mlflow.log_metric.assert_called_once()