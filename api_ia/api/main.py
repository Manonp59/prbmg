
from fastapi import FastAPI, Request, HTTPException
from api_ia.api.utils import PredictionOuput, PredictionInput, predict_cluster, get_model_path
from api_ia.api.database import get_db, create_db_prediction
from fastapi import Depends
from sqlalchemy.orm import Session
import os 
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()


API_IA_SECRET_KEY = os.getenv('API_IA_SECRET_KEY')

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
        if api_key != API_IA_SECRET_KEY:
            raise HTTPException(status_code=401, detail="Accès non autorisé")
    response = await call_next(request)
    return response


@app.post("/predict", response_model=PredictionOuput)
def predict(
    incident: PredictionInput, 
    db: Session = Depends(get_db)
    ) -> PredictionOuput:
    """
    Predicts the cluster for a given incident and saves the prediction to the database.

    This endpoint:
    1. Loads a KMeans model based on a fixed cluster number.
    2. Uses the model to predict the cluster of the given incident.
    3. Creates or updates the prediction record in the database.
    4. Returns the prediction results.

    Args:
        incident (PredictionInput): Input data for the prediction, including incident details.
        db (Session): SQLAlchemy session object for database interactions, provided by dependency injection.

    Returns:
        PredictionOuput: The prediction result including the cluster number, problem title, and resulting embeddings.
    """
    n_cluster = 40
    model_name = f"kmeans_{n_cluster}"
    model_path = get_model_path(model_name)
    
    prediction = predict_cluster(model_path,incident)

    # MLops: Save prediction to database
    prediction_dict = {
        "incident_number": incident.incident_number,
        "creation_date": incident.creation_date,
        "description": incident.description, 
        "category_full": incident.category_full,
        "ci_name": incident.ci_name, 
        "location_full": incident.location_full,
        "resulted_embeddings": json.dumps(prediction.resulted_embeddings),
        "cluster_number": int(prediction.cluster_number),
        "problem_title": prediction.problem_title,
        "model":model_name
    }
    
    create_db_prediction(prediction_dict, db)

    return PredictionOuput(cluster_number=prediction.cluster_number, problem_title=prediction.problem_title,resulted_embeddings=prediction.resulted_embeddings)