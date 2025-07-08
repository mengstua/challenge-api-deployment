from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from typing import List
from predict import predict_price

app = FastAPI()

from fastapi import FastAPI
from typing import Optional, Literal, List
from pydantic import BaseModel

from predict.predict import predict_price
import pandas as pd

app = FastAPI()

# Define a Pydantic model for input data

class PropertyData(BaseModel):
  bedroomcount: int # Number of bedrooms
  habitablesurface: int # Habitable surface area in square meters
  zip_code: int # Postal code of the property
  haslift: Optional[bool] = False # Whether the property has a lift
  hasgarden: Optional[bool] = False # Whether the property has a garden
  hasswimmingpool: Optional[bool] = False # Whether the property has a swimming pool
  hasterrace: Optional[bool] = False # Whether the property has a terrace
  price: Optional[float] = None # Price of the property
  hasparking: Optional[bool] = False # Whether the property has parking
  epcscore_encoded: Optional[int] = None # Encoded EPC score
  buildingcondition_encoded: Optional[int] = None # Encoded building condition
  region_Brussels: Optional[bool] = False # Whether the property is in Brussels
  region_Flanders: Optional[bool] = False # Whether the property is in Flanders
  region_Wallonia: Optional[bool] = False # Whether the property is in Wallonia
  type_encoded: Optional[Literal['APARTMENT', 'HOUSE', 'OTHERS']] = None # Encoded property type
  latitude: Optional[float] = None # Latitude of the property
  longitude: Optional[float] = None # Longitude of the property

  # Define the fields that will be used for prediction

  # These fields should match the columns in your DataFrame used for prediction


    # Temporary DataFrame to hold the data
df = pd.DataFrame(columns=[
    'bedroomcount', 'habitablesurface', 'zip_code', 'haslift', 'hasgarden',
    'hasswimmingpool', 'hasterrace', 'price', 'hasparking', 'epcscore_encoded',
    'buildingcondition_encoded', 'region_Brussels', 'region_Flanders',
    'region_Wallonia', 'type_encoded', 'latitude', 'longitude'
    ])


@app.get("/")
# Temporary storage for the DataFrame
dataframe_storage = None


class DataInput(BaseModel):
    data: List[dict]


@app.post("/predict")
async def upload_dataframe(data_input: PropertyData):
    global dataframe_storage
    # Convert input data to a pandas DataFrame
    dataframe_storage = pd.DataFrame(data_input.data)
    return {"message": "DataFrame uploaded successfully", "columns": PropertyData.columns.tolist()}

@app.get("/predict")
async def get_dataframe_json():
    global dataframe_storage
    if dataframe_storage is None:
        return {"error": "No DataFrame found. Please upload data first."}
    # Convert the DataFrame to JSON
    dataframe_json = dataframe_storage.to_json(orient="records")
    return {"data": dataframe_json}







from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import Preprocessing_meng as preprocess
from predict.prediction import predict
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PropertyData(BaseModel):
    area: int
    property_type: str
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
    building_state: Optional[str] = None

class InputData(BaseModel):
    data: PropertyData

@app.get("/")
async def root():
    return {"status": "alive"}

@app.get("/predict")
async def predict_docs():
    return {
        "description": "Predict property price based on input features",
        "required_fields": ["area", "property_type", "rooms_number", "zip_code"],
        "property_types": ["APARTMENT", "HOUSE", "OTHERS"],
        "building_states": ["NEW", "GOOD", "TO RENOVATE", "JUST RENOVATED", "TO REBUILD"]
    }

@app.post("/predict")
async def predict_price(input_data: InputData):
    try:
        # Preprocess the input data
        processed_data = preprocess(input_data.data)
        
        # Make prediction
        prediction = predict(processed_data)
        
        return {
            "prediction": prediction,
            "status_code": 200
        }
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

