from fastapi import FastAPI, Query
from fastapi import HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List
from api_database.api.functions_database import NotFoundError, get_db_azure
from api_database.api.functions_database import Incident, IncidentCreate, IncidentUpdate, CILocation, Prediction, read_db_predictions, read_db_incident, read_db_one_incident, \
    create_db_incident, update_db_incident, delete_db_incident, read_db_ci_location
import os 
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from datetime import date

load_dotenv()

API_DATABASE_SECRET_KEY = os.getenv('API_DATABASE_SECRET_KEY')

app = FastAPI()

# Apply CORS middleware to allow documentation access without API key
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    """
    A middleware function that verifies the API key in the request headers.

    Parameters:
        request (Request): The incoming HTTP request.
        call_next (callable): The callback function to proceed with the request handling.

    Returns:
        The HTTP response after verifying the API key.
    """
    if request.url.path != "/docs" and request.url.path != "/openapi.json":
        api_key = request.headers.get("X-API-Key")
        if api_key != API_DATABASE_SECRET_KEY:
            raise HTTPException(status_code=401, detail="Accès non autorisé")
    response = await call_next(request)
    return response


@app.get("/")
def read_root():
    return "Server is running."


@app.get("/incident/{incident_number}", response_model=Incident)
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

@app.get("/incidents", response_model=List[Incident])
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


@app.get("/ci_location", response_model=List[CILocation])
def get_ci_location(request: Request,  db: Session = Depends(get_db_azure)) -> List[CILocation]:
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
        db_ci_location = read_db_ci_location(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return [CILocation(**ci.__dict__) for ci in db_ci_location]


@app.get("/predictions", response_model=List[Prediction])
def get_predictions(request: Request,  db: Session = Depends(get_db_azure)) -> List[Prediction]:
    """Retrieve all predictions.

    Args:
        request (Request): The incoming request.
        db (Session, optional): SQLAlchemy session to interact with the database. Defaults to Depends(get_db_azure).

    Returns:
        List[Prediction]: List of retrieved incidents.

    Raises:
        HTTPException: If no predictions are found.
    """
    try:
        db_predictions = read_db_predictions(db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return [Prediction(**prediction.__dict__) for prediction in db_predictions]

@app.post("/incident")
def create_incident(request: Request, incident: IncidentCreate, db: Session = Depends(get_db_azure)) -> Incident:
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

@app.put("/{incident_number}")
def update_incident(request: Request, incident_number: str, incident: IncidentUpdate, db: Session = Depends(get_db_azure)) -> Incident:
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

@app.delete("/{incident_number}")
def delete_incident(request: Request, incident_number: str, db: Session = Depends(get_db_azure)) -> Incident:
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


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)
