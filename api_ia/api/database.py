from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import string
import random
import os
from sqlalchemy.exc import IntegrityError
from datetime import datetime

# Connection string for SQL Server
def create_sql_server_engine():
    """
    Create and return a SQLAlchemy engine for connecting to a SQL Server database using credentials from environment variables.

    The function constructs a connection string using the following environment variables:
    - DRIVER
    - AZURE_SERVER_NAME
    - AZURE_DATABASE_NAME
    - AZURE_DATABASE_USERNAME
    - AZURE_DATABASE_PASSWORD

    Returns:
        sqlalchemy.engine.base.Engine: SQLAlchemy engine connected to the SQL Server database.
    """
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
    incident_number = Column(String,unique=True,index=True)
    creation_date = Column(String)
    description = Column(String)
    category_full = Column(String)
    ci_name = Column(String)
    location_full = Column(String)
    resulted_embeddings = Column(Text)
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


def create_db_prediction(prediction: dict, db: SessionLocal) -> DBpredictions:
    """
    Create or update a prediction in the database based on the provided dictionary.

    This function checks if a prediction with the given `incident_number` already exists:
    - If it exists, updates the existing record with the new values.
    - If it does not exist, creates a new record with a generated ID.

    Args:
        prediction (dict): A dictionary containing prediction data, including 'incident_number'.
        db (SessionLocal): SQLAlchemy session object used for database operations.

    Returns:
        DBpredictions: The updated or newly created prediction record.

    Raises:
        ValueError: If there is an issue inserting a new prediction due to a database integrity error.
    """
    incident_number = prediction.get("incident_number")
    existing_prediction = db.query(DBpredictions).filter(DBpredictions.incident_number == incident_number).first()

    if existing_prediction:
        for key, value in prediction.items():
            setattr(existing_prediction, key, value)
        db.commit()
        db.refresh(existing_prediction)
        return existing_prediction
    else:
        prediction_id = generate_id()
        db_prediction = DBpredictions(prediction_id=prediction_id, **prediction)
        db.add(db_prediction)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            raise ValueError(f"Failed to insert prediction with incident_number: {incident_number}")
        db.refresh(db_prediction)
        return db_prediction