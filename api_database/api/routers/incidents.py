from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from typing import List, Annotated
from api_database.api.database.core import NotFoundError, get_db_azure
from api_database.api.database.authenticate import oauth2_scheme, has_access, User
from api_database.api.database.incidents import Incident, IncidentCreate, IncidentUpdate, read_db_incident, read_db_one_incident, \
    create_db_incident, update_db_incident, delete_db_incident

PROTECTED = Annotated[User, Depends(has_access)]

router = APIRouter(
    prefix="/incidents",
)

@router.get("/{incident_number}", response_model=Incident)
def get_one_incident(request: Request, incident_number: str, db: Session = Depends(get_db_azure)) -> Incident:
    """Retrieve a single incident by incident number.

    Args:
        request (Request): The incoming request.
        incident_number (str): The incident number.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_azure).

    Returns:
        Incident: The retrieved incident.

    Raises:
        HTTPException: If the incident with the given number is not found.
    """
    try:
        db_incident = read_db_one_incident(incident_number, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Incident(**db_incident.__dict__)

@router.get("/", response_model=List[Incident])
def get_incident(request: Request,  db: Session = Depends(get_db_azure)) -> List[Incident]:
    """Retrieve all incidents.

    Args:
        request (Request): The incoming request.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_azure).

    Returns:
        List[Incident]: List of retrieved incidents.

    Raises:
        HTTPException: If no incidents are found.
    """
    try:
        db_incident = read_db_incident(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return [Incident(**incident.__dict__) for incident in db_incident]

@router.post("/")
def create_incident(has_access: PROTECTED,request: Request, incident: IncidentCreate, db: Session = Depends(get_db_azure)) -> Incident:
    """Create a new incident.

    Args:
        has_access (PROTECTED): The authenticated user.
        request (Request): The incoming request.
        incident (IncidentCreate): Information about the incident to be created.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_azure).

    Returns:
        Incident: The newly created incident.
    """
    db_incident = create_db_incident(incident, db)
    return Incident(**db_incident.__dict__)

@router.put("/{incident_number}")
def update_incident(has_access: PROTECTED,request: Request, incident_number: str, incident: IncidentUpdate, db: Session = Depends(get_db_azure)) -> Incident:
    """Update an existing incident.

    Args:
        has_access (PROTECTED): The authenticated user.
        request (Request): The incoming request.
        incident_number (str): The incident number.
        incident (IncidentUpdate): Information about the incident to be updated.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_azure).

    Returns:
        Incident: The updated incident.

    Raises:
        HTTPException: If the incident with the given number is not found.
    """
    try:
        db_incident = update_db_incident(incident_number, incident, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Incident(**db_incident.__dict__)

@router.delete("/{incident_number}")
def delete_incident(has_access: PROTECTED,request: Request, incident_number: str, db: Session = Depends(get_db_azure)) -> Incident:
    """Delete an existing incident.

    Args:
        has_access (PROTECTED): The authenticated user.
        request (Request): The incoming request.
        incident_number (str): The incident number.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_azure).

    Returns:
        Incident: The deleted incident.

    Raises:
        HTTPException: If the incident with the given number is not found.
    """
    try:
        db_incident = delete_db_incident(incident_number, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return Incident(**db_incident.__dict__)