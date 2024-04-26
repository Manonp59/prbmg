from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api_ia.api.database import Base, create_db_prediction, DBpredictions
from typing import Generator
import pytest



@pytest.fixture
def session() -> Generator[Session, None, None]:
    TEST_DATABASE_URL = "sqlite:///:memory:"

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread":False},poolclass=StaticPool)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()

    yield db_session

    db_session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_prediction(session:Session) -> None: 
    mock_prediction = {
        "docs" : "docs str test",
        "cluster_number" : 4,
        "problem_title" : "example title",
        "model" :"test_model"
    }
    
    prediction = create_db_prediction(mock_prediction,session)
    
    prediction_in_db = session.query(DBpredictions).filter(DBpredictions.prediction_id == prediction.prediction_id).first()
    
    assert prediction_in_db
    assert len(prediction_in_db.prediction_id) == 14
    assert prediction_in_db.docs == "docs str test"
    assert prediction_in_db.cluster_number == 4
    assert prediction_in_db.problem_title == "example title"
    assert prediction_in_db.model == "test_model"