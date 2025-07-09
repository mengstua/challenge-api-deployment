from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, Literal
from preporcess.cleaning_data import preprocess
from predict.prediction import predict  # this function wraps your model's prediction
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

# Your input model
class PropertyData(BaseModel):
    area: int
    property_type: Literal["APARTMENT", "HOUSE", "OTHERS"] = Field(..., alias="property-type")
    rooms_number: int = Field(..., alias="rooms-number")
    zip_code: int = Field(..., alias="zip-code")
    land_area: Optional[int] = Field(None, alias="land-area")
    garden: Optional[bool] = None
    garden_area: Optional[int] = Field(None, alias="garden-area")
    equipped_kitchen: Optional[bool] = Field(None, alias="equipped-kitchen")
    full_address: Optional[str] = Field(None, alias="full-address")
    swimming_pool: Optional[bool] = Field(None, alias="swimming-pool")
    furnished: Optional[bool] = None
    open_fire: Optional[bool] = Field(None, alias="open-fire")
    terrace: Optional[bool] = None
    terrace_area: Optional[int] = Field(None, alias="terrace-area")
    facades_number: Optional[int] = Field(None, alias="facades-number")
    building_state: Optional[
        Literal["NEW", "GOOD", "TO RENOVATE", "JUST RENOVATED", "TO REBUILD"]
    ] = Field(None, alias="building-state")

    class Config:
        validate_by_name = True

class InputData(BaseModel):
    data: PropertyData

    class Config:
        validate_by_name = True

class PredictionResult(BaseModel):
    prediction: Optional[float] = None
    status_code: int
    error: Optional[str] = None

@app.post("/predict", response_model=PredictionResult)
async def predict_route(input_data: InputData):
    try:
        data_dict = input_data.data.model_dump(by_alias=True)
        logger.info(f"Raw input: {data_dict}")

        preprocessed_data = preprocess(data_dict)
        prediction_result = predict(preprocessed_data)

        return {
            "prediction": prediction_result,
            "status_code": 200
        }

    except ValueError as ve:
        logger.error(f"Validation error: {ve}")
        return {"error": str(ve), "status_code": 400}

    except Exception as e:
        logger.exception("Unhandled error")
        return {"error": "Internal server error", "status_code": 500}
