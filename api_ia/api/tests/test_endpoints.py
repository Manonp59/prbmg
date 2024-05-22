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


@pytest.fixture
def mock_jwt_decode(monkeypatch):
    # Mock the jwt.decode function to return the mock payload
    monkeypatch.setattr("jose.jwt.decode", MagicMock(return_value={"sub": "admin"}))
    return "mock_token"


@pytest.fixture(autouse=False)
def mock_predict(monkeypatch):
    # Mock the jwt.decode function to return the mock payload
    monkeypatch.setattr("api_ia.api.utils.predict_cluster", MagicMock(return_value=1))


def test_predict_endpoint(mock_jwt_decode, mock_predict):
    # Prepare test data
    data = {"input_str": "some document text"}

    # Send a POST request to the /predict endpoint
    response = client.post("/predict", json=data, headers={"Authorization": f"Bearer {mock_jwt_decode}"})

    # Verify the response status code
    assert response.status_code == 200

    # Verify the response content
    assert "cluster_number" in response.json()
    assert "problem_title" in response.json()
