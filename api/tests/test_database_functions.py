from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from database.core import Base, DBIncidents
from typing import Generator
from database.incidents import IncidentCreate, create_db_incident, generate_id
from database.authenticate import UserCreate, create_db_user
import pytest
from passlib.context import CryptContext


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
            location = "Lestrem",)
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
            location = "Lestrem",
            ), 
            session)
    assert len(incident.incident_number) == 14
    assert incident.category_full == "Incidents/Infrastructure/System/Exchange On'prem"
    assert incident.ci_name == "S101X01X"
    assert incident.location == "Lestrem"


def test_create_user(session:Session) -> None: 
    user = create_db_user( 
        UserCreate( 
            username="test_user",
            email = "test_user@test.com",
            full_name="test_user_fullname",
            password = "test_password"
            ), 
            session)
    
    
    assert user.username == "test_user"
    assert user.email == "test_user@test.com"
    assert user.full_name=="test_user_fullname"
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    assert pwd_context.verify("test_password", user.hashed_password)