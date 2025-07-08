from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from prepocessing.preprocessing import Immo_Preprocessing
from predict.predict_Meng import predictor
import logging


app = FastAPI()
logger = logging.getLogger(__name__)

# Input Models
class PropertyData(BaseModel):
    area: int
    property_type: Literal["APARTMENT", "HOUSE", "OTHERS"]
    rooms_number: int
    zip_code: int
    land_area: Optional[int] = None
    garden: Optional[bool] = False
    garden_area: Optional[int] = None
    equipped_kitchen: Optional[bool] = False
    full_address: Optional[str] = None
    swimming_pool: Optional[bool] = False
    furnished: Optional[bool] = False
    open_fire: Optional[bool] = False
    terrace: Optional[bool] = False
    terrace_area: Optional[int] = None
    facades_number: Optional[int] = None
    building_state: Optional[Literal["NEW", "GOOD", "TO_RENOVATE", "JUST_RENOVATED", "TO_REBUILD"]] = None

class InputData(BaseModel):
    data: PropertyData

# Output Model
class PredictionResult(BaseModel):
    prediction: Optional[float] = None
    status_code: int
    error: Optional[str] = None

# Endpoints
@app.get("/")
def root():
    return {"status": "alive"}

@app.get("/predict")
def get_predict_request():
    """Returns required input structure"""
    return {
        "required_fields": ["area", "property_type", "rooms_number", "zip_code"],
        "optional_fields": [f for f in PropertyData if f not in ["area", "property_type", "rooms_number", "zip_code"]]
    }

# Correct indentation example:
@app.post("/predict", response_model=PredictionResult)
async def predict(input_data: InputData):  # <- Base level (0 indent)
    try:  # <- 1 level indent (4 spaces)
        processor = Immo_Preprocessing()  # <- Same level as try
        features = processor.preprocess_api_input(input_data.data.dict())  # <- Aligned
        
        prediction = predictor.predict_price(features)  # <- Same level
        
        return {  # <- Same level
            "prediction": prediction,
            "status_code": 200
        }
    except ValueError as e:  # <- Same level as try
        logger.error(f"Input error: {str(e)}")
        return {
            "error": str(e),
            "status_code": 400
        }