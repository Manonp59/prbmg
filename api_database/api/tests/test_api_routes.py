import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api_database.api.functions_database import Base, get_db_azure
from api_database.api.main import app

# Configure a test database URL (this should be a separate test database)
TEST_DATABASE_URL = "sqlite:///./test.db"

# Set up the database
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

app.dependency_overrides[get_db_azure] = override_get_db

# Use a test client
client = TestClient(app)

# Set the test API key
api_key = os.getenv('API_DATABASE_SECRET_KEY')


@pytest.fixture(scope="module")
def test_app():
    yield client


def test_read_root(test_app):
    response = test_app.get("/", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    assert response.json() == "Server is running."

def test_get_all_incidents_empty(test_app):
    response = test_app.get("/incidents", headers = {"X-API-Key": api_key})
    assert response.status_code == 200


def test_create_incident(test_app):
    incident_data = {
        "description" : "Test Incident",
        "category_full" : "Incidents/Infrastructure/System/Exchange On'prem",
        "ci_name" : "S101X01X",
        "location_full" :"Lestrem",
        "owner_group" :"CORP_ISC_L1",
        "urgency":"3 - Low",
        "priority" : 4,
        "SLA":"ISC SLA INC P4"
    }
    response = test_app.post("/incident", json=incident_data, headers = {"X-API-Key": api_key})
    assert response.status_code == 200
    incident = response.json()
    assert incident["description"] == "Test Incident"
    return incident["incident_number"]


def test_get_one_incident(test_app):
    incident_number = test_create_incident(test_app)
    response = test_app.get(f"/incident/{incident_number}",headers = {"X-API-Key": api_key})
    assert response.status_code == 200
    assert response.json()["incident_number"] == incident_number
    assert response.json()["description"] == "Test Incident"

def test_update_incident(test_app):
    incident_number = test_create_incident(test_app)
    update_data = {
        "description": "Updated Incident",
        "category_full": "Incidents/Infrastructure/System/Updated",
        "ci_name": "S101X01X",
        "location_full": "Updated Location",
        "owner_group": "CORP_ISC_L1",
        "urgency": "2 - Medium",
        "priority": 2,
        "SLA": "ISC SLA INC P2"
    }
    response = test_app.put(f"/{incident_number}", json=update_data, headers={"X-API-Key": api_key})
    assert response.status_code == 200
    updated_incident = response.json()
    assert updated_incident["description"] == "Updated Incident"
    assert updated_incident["category_full"] == "Incidents/Infrastructure/System/Updated"
    assert updated_incident["urgency"] == "2 - Medium"

def test_delete_incident(test_app):
    incident_number = test_create_incident(test_app)
    response = test_app.delete(f"/{incident_number}", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    deleted_incident = response.json()
    assert deleted_incident["incident_number"] == incident_number

def test_get_all_incidents_non_empty(test_app):
    incident_data = {
        "description": "Another Test Incident",
        "category_full": "Incidents/Infrastructure/System/Another",
        "ci_name": "S101X01Y",
        "location_full": "Another Location",
        "owner_group": "CORP_ISC_L1",
        "urgency": "3 - Low",
        "priority": 3,
        "SLA": "ISC SLA INC P3"
    }
    test_app.post("/incident", json=incident_data, headers={"X-API-Key": api_key})
    response = test_app.get("/incidents", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_non_existing_incident(test_app):
    response = test_app.get("/incident/NON_EXISTENT_INCIDENT", headers={"X-API-Key": api_key})
    assert response.status_code == 404
    os.remove("./test.db")







