import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api_ia.api.main import app
from api_ia.api.database import Base, get_db
from api_ia.api.utils import PredictionInput
from dotenv import load_dotenv

load_dotenv()

API_IA_SECRET_KEY = os.getenv('API_IA_SECRET_KEY')

# Configure a test database URL 
TEST_DATABASE_URL = "sqlite:///./test2.db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Use a test client
client = TestClient(app)

@pytest.fixture(scope="module")
def test_app():
    yield client

def test_predict_route(test_app):

    test_incident = {
        "incident_number":"1234",
        "description":"""Trigger: Host has been restarted (uptime < 15m) Responsible team: CORP_ISC_Wintel Trigger description:  
        Trigger severity: Warning Trigger nseverity: 2 Trigger tags: Application:Status, RT:CORP_ISC_Wintel Host: S273A12 
        Host group: Mumbai/Windows, PSRI, Windows/Mumbai Host description:  Zabbix event ID: 1037670088""",
        "category_full":"Incidents/Infrastructure/System/RDS",
        "ci_name":"S273A12",
        "location_full":"INDIA/INDIA/MUMBAI",
        "creation_date":"2023-04-23 08:34"
    }
    
    # Make a request to the predict route with the test incident and API key
    response = test_app.post("/predict", json=test_incident, headers={"X-API-Key": API_IA_SECRET_KEY})

    if response.status_code != 200:
        print(response.json())  # Print the error response

    # Check if the response status code is 200 (OK)
    assert response.status_code == 200

    # Check if the response contains the expected keys
    assert "cluster_number" in response.json()
    assert "problem_title" in response.json()




