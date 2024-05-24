from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api_database.api.functions_database import Base, DBIncidents
from typing import Generator
from api_database.api.functions_database import IncidentCreate, create_db_incident, generate_id
import pytest



@pytest.fixture
def session() -> Generator[Session, None, None]:
    TEST_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread":False},poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

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

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_incidents(session:Session) -> None: 
    incident = create_db_incident( 
        IncidentCreate( 
            incident_number = generate_id(session),
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
            SLA = "ISC SLA INC P4"
            ), 
            session)
    assert len(incident.incident_number) == 14
    assert incident.category_full == "Incidents/Infrastructure/System/Exchange On'prem"
    assert incident.ci_name == "S101X01X"
    assert incident.location_full == "Lestrem"


