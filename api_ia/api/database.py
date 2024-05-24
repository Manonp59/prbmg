from sqlalchemy import create_engine, Column, Integer, String, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import string
import random
import os


# Connection string for SQL Server
def create_sql_server_engine():
    driver = os.getenv("DRIVER")
    server = os.getenv("AZURE_SERVER_NAME")
    database = os.getenv("AZURE_DATABASE_NAME")
    username = os.getenv("AZURE_DATABASE_USERNAME")
    password = os.getenv("AZURE_DATABASE_PASSWORD")
    CONNECTION_STRING = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"

    # Create engine and session
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={CONNECTION_STRING}")
    return engine

engine = create_sql_server_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Model class for predictions
class DBpredictions(Base):
    __tablename__ = "predictions"

    prediction_id = Column(String(255), primary_key=True, index=True)
    incident_number = Column(String)
    description = Column(String)
    category_full = Column(String)
    ci_name = Column(String)
    location_full = Column(String)
    cluster_number = Column(Integer)
    problem_title = Column(String)
    model = Column(String)


# Create tables in the database
Base.metadata.create_all(bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to generate a unique ID
def generate_id():
    length = 14
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))


# Function to create a prediction in the database
def create_db_prediction(prediction: dict, db: SessionLocal) -> DBpredictions:
    
    prediction_id = generate_id()
    db_prediction = DBpredictions(prediction_id=prediction_id, **prediction)
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction
