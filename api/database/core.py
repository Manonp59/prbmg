from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
import os 
from dotenv import load_dotenv
from sqlalchemy import Integer, String
import pyodbc

load_dotenv()

# Setting the users database
DATABASE_URL_SQLITE = "sqlite:///users.db"

# Setting the incidents database
server = os.getenv("AZURE_SERVER_NAME")
database_azure = os.getenv("AZURE_DATABASE_NAME")
username_azure = os.getenv("AZURE_DATABASE_USERNAME")
password_azure = os.getenv("AZURE_DATABASE_PASSWORD")
port = "1433"
DATABASE_URL_AZURE = f'mssql+pyodbc://{username_azure}:{password_azure}@{server}:{port}/{database_azure}?driver=ODBC+Driver+18+for+SQL+Server'

# Define custom exception for not found errors
class NotFoundError(Exception):
    pass


# Define base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Define the DBIncidents class for the incidents_location table 
class DBIncidents(Base):

    __tablename__ = "incidents_location"

    incident_number: Mapped[str] = mapped_column(primary_key=True, index=True)
    description: Mapped[str]
    category_full: Mapped[str]
    ci_name: Mapped[str]
    location_full: Mapped[str]


# Define the DBUsers class for the users table 
class DBUsers(Base):

    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(250),primary_key=True, index=True)
    email: Mapped[str]
    full_name: Mapped[str]
    hashed_password: Mapped[str]


# Define the DBToken class for the tokens table 
class DBToken(Base):

    __tablename__ = "tokens"

    username: Mapped[str] = mapped_column(String(250),primary_key=True, index=True)


# Create SQLAlchemy engines for SQLite and Azure Database
engine_sqlite = create_engine(DATABASE_URL_SQLITE)
engine_azure = create_engine(DATABASE_URL_AZURE)

# Create session makers for SQLite and Azure Database
SessionLocalSQLite = sessionmaker(autocommit=False, autoflush=False, bind=engine_sqlite)
SessionLocalAzure = sessionmaker(autocommit=False, autoflush=False, bind=engine_azure)

# Create table in SQLite database (Azure Database tables already exist)
Base.metadata.create_all(bind=engine_sqlite,tables=[DBUsers.__table__, DBToken.__table__])



def get_db_sqlite():
    """Get a SQLite database session"""
    db = SessionLocalSQLite()
    try:
        yield db
    finally:
        db.close()


def get_db_azure():
    """Get an Azure database session"""
    db = SessionLocalAzure()
    try:
        yield db
    finally:
        db.close()