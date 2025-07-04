from fastapi import FastAPI
from typing import Optional, Literal
from pydantic import BaseModel

from predict import predict_price

app = FastAPI()

class PropertyData(BaseModel):
# TODO
    pass

@app.get("/")
async def root():
    """Route that return 'Alive!' if the server runs."""
    return {"Status": "Alive!"}


@app.get("/predict")
async def predict_info():
    return data_format_json


data_format_json =  {
  "Format of your JSON input for POST requests:": {
    "area": "int",
    "property-type": "APARTMENT | HOUSE | OTHERS",
    "rooms-number": "int",
    "zip-code": "int",
    "land-area (optional)": "int",
    "garden (optional)": "bool",
    "garden-area (optional)": "int",
    "equipped-kitchen (optional)": "bool",
    "full-address (optional)": "str",
    "swimming-pool (optional)": "bool",
    "furnished (optional)": "bool",
    "open-fire (optional)": "bool",
    "terrace (optional)": "bool",
    "terrace-area (optional)": "int",
    "facades-number (optional)": "int",
    "building-state (optional)": 
      "NEW | GOOD | TO RENOVATE | JUST RENOVATED | TO REBUILD"
  }
}

@app.post("/predict")
async def predict(data:PropertyData ):

    # transorm JSON to df
    # call predict_price()
    pass