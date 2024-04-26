from fastapi.testclient import TestClient
from api_ia.api.main import app
import pytest 
from unittest.mock import MagicMock
from sqlalchemy.orm import sessionmaker, Session
from api_ia.api.database import Base, get_db
from typing import Generator
from sqlalchemy import create_engine, StaticPool
from api_ia.api.utils import PredictionInput

from fastapi.testclient import TestClient
from api_ia.api.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_jwt_decode(monkeypatch):
    # Mock the jwt.decode function to return the mock payload
    monkeypatch.setattr("jose.jwt.decode", MagicMock(return_value={"sub": "admin"}))
    yield "mock_token"


def test_predict_endpoint(mock_jwt_decode):
    # Préparer les données de test
    data = {"input_str":"somme document text"}

    # Envoyer une requête POST à l'endpoint /predict
    response = client.post("/predict", json=data,headers={"Authorization":f"Bearer {mock_jwt_decode}"})
    # Vérifier le code de statut de la réponse
    assert response.status_code == 200

    # Vérifier le contenu de la réponse
    assert "cluster_number" in response.json()
    assert "problem_title" in response.json()
