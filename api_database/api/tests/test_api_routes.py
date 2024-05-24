from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api_database.api.functions_database import Base, get_db_azure, DBIncidents
from api_database.api.functions_database import generate_id
from api_database.api.main import app
from typing import Generator
import pytest 
from unittest.mock import MagicMock

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread":False},poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session() -> Generator[Session, None, None]:

    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    #create test incidents
    db_incident = DBIncidents(
            incident_number = generate_id(db_session),
            description = """Trigger: *.extranet.roquette.com - Days left until 30 expires
            Responsible team: {EVENT.TAGS.RT}
            Trigger description: 
            Trigger severity: Average
            Trigger nseverity: 3
            Trigger tags: Application:Exchange
            Host: S101X01X
            Host group: EXCH, Exchange/Lestrem, Lestrem/Exchange
            Host description: 
            Zabbix event ID: 1060797202""",
            category_full = "Incidents/Infrastructure/System/Exchange On'prem",
            ci_name = "S101X01X",
            location_full = "Lestrem",
            owner_group = "CORP_ISC_L1",
            urgency = "3 - Low",
            priority = 4,
            SLA = "ISC SLA INC P4")
    
    db_session.add(db_incident)
    db_session.commit()

    db_session.close()
    Base.metadata.drop_all(bind=engine)



client  = TestClient(app)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db_azure] = override_get_db

def test_read_root(session:Session):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == 'Server is running.'




def test_create_improper_incident(session:Session):
    response = client.post("/incidents/",json={
            "description": """Trigger: *.extranet.roquette.com - Days left until 30 expires
            Responsible team: {EVENT.TAGS.RT}
            Trigger description: 
            Trigger severity: Average
            Trigger nseverity: 3
            Trigger tags: Application:Exchange
            Host: S101X01X
            Host group: EXCH, Exchange/Lestrem, Lestrem/Exchange
            Host description: 
            Zabbix event ID: 1060797202""",
            "category_full": "Incidents/Infrastructure/System/Exchange On'prem",
            "ci_name": "S101X01X",},
            headers={"Authorization": f"Bearer {'mocked_token'}"})
    assert response.status_code == 422, response.text


def test_create_incident(session:Session):
    response = client.post("/incidents/",json={
            "description": """Trigger: *.extranet.roquette.com - Days left until 30 expires
            Responsible team: {EVENT.TAGS.RT}
            Trigger description: 
            Trigger severity: Average
            Trigger nseverity: 3
            Trigger tags: Application:Exchange
            Host: S101X01X
            Host group: EXCH, Exchange/Lestrem, Lestrem/Exchange
            Host description: 
            Zabbix event ID: 1060797202""",
            "category_full": "Incidents/Infrastructure/System/Exchange On'prem",
            "ci_name": "S101X01X",
            "location":"Lestrem"},
            headers={"Authorization": f"Bearer {'mocked_token'}"})
    assert response.status_code == 200, response.text




