
from fastapi import APIRouter
import pickle 
from api_ia.api.utils import get_embeddings, get_problem_title, PredictionOuput, PredictionInput, has_access, get_model_path, predict_cluster
from api_ia.api.database import get_db, create_db_prediction
from pydantic import BaseModel
import numpy as np 
import ast 
import uvicorn
import pandas as pd 
from fastapi import Depends
from sqlalchemy.orm import Session

router = APIRouter()

@router.post("", response_model=PredictionOuput)
def predict(
    incident: PredictionInput, 
    authenticated: bool = [Depends(has_access)],
    db: Session = Depends(get_db)
    ) -> PredictionOuput:

    model_name = "kmeans_30"
    model_path = get_model_path(model_name)
    print(model_path)
    prediction = predict_cluster(model_path, incident)

    # MLops: Save prediction to database
    prediction_dict = {
        "cluster_number": int(prediction.cluster_number),
        "docs": incident.input_str,
        "problem_title": prediction.problem_title,
        "model":model_name
    }
    create_db_prediction(prediction_dict, db)

    return PredictionOuput(cluster_number=prediction.cluster_number, problem_title=prediction.problem_title)
 




