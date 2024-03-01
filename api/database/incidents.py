from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .core import DBIncidents, NotFoundError
from datetime import datetime

# Represents an incident
class Incident(BaseModel):
    incident_number: str
    description: str
    category_full: str
    ci_name: str
    location_full: str


# Model for creating an incident
class IncidentCreate(BaseModel):
    description: str
    category_full: str
    ci_name: str
    location_full: str


# Model for updating an incident"
class IncidentUpdate(BaseModel):
    description: str
    category_full: str
    ci_name: str
    location_full: str



def read_db_one_incident(incident_number: str, session: Session) -> DBIncidents:
    """Reads a single incident from the database by incident number.

    Args:
        incident_number (str): The incident number to search for.
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        DBIncidents: Database incident object.

    Raises:
        NotFoundError: If the incident with the given number is not found.
    """
    db_incident = session.query(DBIncidents).filter(DBIncidents.incident_number == incident_number).first()
    if db_incident is None:
        raise NotFoundError(f"Item with id {incident_number} not found.")
    return db_incident

def read_db_incident(session: Session) -> List[DBIncidents]:
    """Reads incidents from the database.

    Args:
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        List[DBIncidents]: List of database incident objects.

    Raises:
        NotFoundError: If the database is empty.
    """
    db_incident = session.query(DBIncidents).limit(5).all()
    if db_incident is None:
        raise NotFoundError(f"Database is empty")
    return db_incident

def generate_id(session: Session) -> str:
    """Generate a unique string ID."""
    today_date = datetime.now().strftime("%y%m%d")
    incident_prefix = f"I{today_date}_"
    last_incident = session.query(DBIncidents.incident_number).filter(DBIncidents.incident_number.like(f"{incident_prefix}%")).order_by(DBIncidents.incident_number.desc()).first()    
    session.close()
    if last_incident:
        # Extraire le numéro d'incident de l'ID
        _, incident_number = last_incident.incident_number.split("_")
        last_number = int(incident_number)
    else:
        last_number = 0
    next_incident_number = str(last_number + 1).zfill(6)
    return f"I{today_date}_{next_incident_number}"


def create_db_incident(incident: IncidentCreate, session: Session) -> DBIncidents:
    """Creates an incident in the database.

    Args:
        incident (IncidentCreate): Data for creating the incident.
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        DBIncidents: Database incident object.
    """
    db_incident = DBIncidents(**incident.model_dump(exclude_none=True), incident_number=generate_id(session))
    session.add(db_incident)
    session.commit()
    session.refresh(db_incident)

    return db_incident


def update_db_incident(incident_number: str, incident: IncidentUpdate, session: Session) -> DBIncidents:
    """Updates an incident in the database.

    Args:
        incident_number (str): The incident number to update.
        incident (IncidentUpdate): Data for updating the incident.
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        DBIncidents: Updated database incident object.
    """
    db_incident = read_db_one_incident(incident_number, session)
    for key, value in incident.model_dump(exclude_none=True).items():
        setattr(db_incident, key, value)
    session.commit()
    session.refresh(db_incident)

    return db_incident


def delete_db_incident(incident_number: str, session: Session) -> DBIncidents:
    """Deletes an incident from the database.

    Args:
        incident_number (str): The incident number to delete.
        session (Session): SQLAlchemy session to interact with the database.

    Returns:
        DBIncidents: Deleted database incident object.
    """
    db_incident = read_db_one_incident(incident_number, session)
    session.delete(db_incident)
    session.commit()
    return db_incident