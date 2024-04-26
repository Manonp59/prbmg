# main.py script
from fastapi import FastAPI, Depends
import api_ia.api.predict as predict
from .utils import has_access
from fastapi.params import Depends


app = FastAPI()

# routes
PROTECTED = [Depends(has_access)]

app.include_router(
    predict.router,
    prefix="/predict",
    dependencies=PROTECTED
)