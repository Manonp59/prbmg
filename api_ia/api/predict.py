from fastapi import FastAPI
import pickle 
from api_ia.api.utils import get_embeddings, get_problem_title
from pydantic import BaseModel
import numpy as np 
import ast 
import uvicorn
import pandas as pd 

router = APIRouter()

@router.post("", response_model=SinglePredictionOutput)
def predict(
    order: SinglePredictionInput, 
    authenticated: bool = [Depends(has_access)],
    db: Session = Depends(get_db)
    ) -> SinglePredictionOutput:

    model_name = "first_run_2017"
    model_path = get_model_path(model_name)
    prediction = predict_single(model_path, order)

    # MLops: Save prediction to database
    prediction_dict = {
        "prediction": int(prediction),
        "produit_recu": order.produit_recu,
        "temps_livraison": order.temps_livraison,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model":model_name
    }
    create_db_prediction(prediction_dict, db)

    return SinglePredictionOutput(prediction=prediction)
 
with open('/home/utilisateur/DevIA/prbmg/api_ia/clustering_model/model_kmeans_30.pickle','rb') as f:
    model = pickle.load(f)



@app.post("/predict/")
def cluster_incidents(input:DocsInput):
    print(input)
    input_series = pd.Series({"docs":input.input_str})
    embeddings = get_embeddings(input_series)
    prediction = model.predict(embeddings)
    problem_title = get_problem_title(prediction[0])
    output = PredictionOuput(cluster_number=prediction[0],problem_title=problem_title)

    return output 

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=80)



