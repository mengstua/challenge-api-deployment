from fastapi import FastAPI
from typing import Optional, Literal, List
from pydantic import BaseModel

from predict.predict import predict_price
import pandas as pd

app = FastAPI()


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

@app.get("/predict")
async def dataframe_to_json():
    # Convert DataFrame to JSON
    json_data = df.to_dict(orient="records")
    return JSONResponse(content=json_data)

@app.post("/predict")
async def predict(data:PropertyData):
    

    # transorm JSON to df
    # call predict_price()
    pass
