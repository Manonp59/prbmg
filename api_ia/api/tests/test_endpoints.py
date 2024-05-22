from fastapi.testclient import TestClient
from api_ia.api.main import app
import pytest 
from unittest.mock import MagicMock, mock_open
from sqlalchemy.orm import sessionmaker, Session
from api_ia.api.database import Base, get_db
from typing import Generator
from sqlalchemy import create_engine, StaticPool
from api_ia.api.utils import PredictionInput
import pickle 

client = TestClient(app)

class MockModel:
    def predict(self, embeddings):
        return [0]

@pytest.fixture
def mock_jwt_decode(monkeypatch):
    # Mock the jwt.decode function to return the mock payload
    monkeypatch.setattr("jose.jwt.decode", MagicMock(return_value={"sub": "admin"}))
    return "mock_token"

@pytest.fixture
def mock_get_model_path(monkeypatch):
    # Mock the get_model_path function to return a valid path
    mock_path = "/path/to/mock/model.pkl"
    monkeypatch.setattr("api_ia.api.utils.get_model_path", lambda x: mock_path)
    return mock_path

@pytest.fixture
def mock_open_file(monkeypatch):
    # Create a pickled mock model
    mock_model = MockModel()
    mock_model_data = pickle.dumps(mock_model)

    # Mock the open function to simulate reading a model file
    mock_file = mock_open(read_data=mock_model_data)
    monkeypatch.setattr("builtins.open", mock_file)
    return mock_file

def test_predict_endpoint(mock_jwt_decode, mock_get_model_path, mock_open_file):
    # Prepare test data
    data = {"input_str": "some document text"}

    # Send a POST request to the /predict endpoint
    response = client.post("/predict", json=data, headers={"Authorization": f"Bearer {mock_jwt_decode}"})

    # Verify the response status code
    assert response.status_code == 200

    # Verify the response content
    assert "cluster_number" in response.json()
    assert "problem_title" in response.json()
