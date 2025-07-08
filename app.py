import logging
from fastapi import FastAPI, Request, requests
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional, Literal
from pydantic import BaseModel, Field
import pandas as pd
import os

from pydantic import BaseModel

from prepocessing.preprocessing import Immo_Preprocessing #####!!!!! spelling error: preposessing
from predict.predict_Nad import Predict_Nad


#app = FastAPI()


# Set port to the env variable PORT to make it easy to choose the port on the server
# If the Port env variable is not set, use port 8000
PORT = os.environ.get("PORT", 8000)
app = FastAPI(port=PORT)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("myapp.log")
logger.addHandler(file_handler)

################## To handle errors with incorrectly input variables in the POST method

# Middleware to catch and log all unhandled exceptions (like 500 errors)
@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        logger.error(  # Prints in the log file
            "Unhandled exception encountered",
            exc_info=True,  # This writes the full traceback to the log file
            # extra={
            #     "path": request.url.path,
            #     "method": request.method,
            #     "client_host": request.client.host
            # }
        )
        # Print on screen
        return JSONResponse(
            status_code=500,
            content={"500 error detail ": "Internal Server Error"}
        )
     
##########################""    
    
@app.get("/check_LoggingStatus")
async def root():
    logger.info("Hello, logging works!")
    return {"message": "Look for the message above in the .log file!"}


@app.get("/")
async def root():
    """Route that return 'Alive!' if the server runs."""
    return {"Status": "Alive!"}

########### Give instructions about input JSON file

@app.get("/predict")
async def predict_info():
    return data_format_json

data_format_json =  { #  TO DO: adjust str, bool, etc according to my comments
  "Format of your JSON input for POST requests:": {
    "area": "int",
    "property-type": "APARTMENT | HOUSE",     # Removed | OTHERS - not in our model!   
    "rooms-number": "int",
    "zip-code": "int",
    " land-area (optional)": "int",  # If absent- will be replaced with 0.
    " garden (optional)": "bool",   # 1, 0, or NaN (> 1 are also allowed but don't affect price it seems), otherwise preprocessing.py complains! If absent- will be replaced with 0.
    " garden-area (optional)": "int", # will be dropped, any value or even absent 
    " equipped-kitchen (optional)": "bool", # will be dropped, any value or even absent
    " full-address (optional)": "str", # will be dropped, any value or even absent
    " swimming-pool (optional)": "bool", # 1, 0, or NaN (> 1 are also allowed but don't affect price it seems), otherwise preprocessing.py complains! If absent- will be replaced with 0.
    " furnished (optional)": "bool", # will be dropped, any value or even absent
    " open-fire (optional)": "bool", # will be dropped, any value or even absent
    " terrace (optional)": "bool", # 1, 0, or NaN (> 1 are also allowed but don't affect price it seems), otherwise preprocessing.py complains! If absent- will be replaced with 0.
    " terrace-area (optional)": "int", # will be dropped, any value or even absent
    " facades-number (optional)": "int", # will be dropped, any value or even absent
    " building-state (optional)": # if absent- will be replaced with 'GOOD'
     "AS_NEW | JUST_RENOVATED | GOOD | TO_BE_DONE_UP | TO_RENOVATE | TO_RESTORE",  # Was: "NEW | GOOD | TO RENOVATE | JUST RENOVATED | TO REBUILD"
    "lift" : "int", # added, 1, 0, NaN (> 1 are also allowed but don't affect price it seems), otherwise preprocessing.py complains!
    "parkingcountindoor" : "int", # added, 1, 0, or NaN (values > 0 are converted to 1, <0 - to 0), otherwise preprocessing.py complains!
    "parkingcountoutdoor" : "int", # added, 1, 0, or NaN (values > 0 are converted to 1, <0 - to 0), otherwise preprocessing.py complains!
    "province" : "str", # added, should be 'Antwerp', 'East Flanders','Flemish Brabant', 'Limburg','West Flanders',
                                # 'Walloon Brabant', 'Hainaut', 'Liège', 'Luxembourg', 'Namur', 'Brussels',
                                #  but can be be anything incl. NaN as well
    "epcscore" : "str", # added, has to be 'A++', 'A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G' 

  }
}

################## Will result from errors in http://127.0.0.1:8000/predict_WithBetterValidation

@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors=exc.args[0]
    formatted_errors = []

    def generate_custom_message(error, field):
        # Customize messages based on error type
        if error["type"] == "missing":
            return f" ---You forgot to input: {field}."
        # Add more cases as needed
        return f" ---Wrong type of input for: {field} - {error['msg']}"  
          
    for error in errors:
      field = error["loc"]
      custom_message = generate_custom_message(error, field)
      formatted_errors.append(custom_message)
    
    return JSONResponse(
        status_code=422,
        #content=jsonable_encoder({"errors": formatted_errors, "body": exc.body, "Detail": exc.args}),
        content=jsonable_encoder({"Errors": formatted_errors}),
    )
#################  Process input JSON file with validation of types ####################

# Needed for validation of input data and renaming is needed because can't have dashes in the variables' names
class PropertyData(BaseModel):
    area: int
    property_type: Literal["APARTMENT", "HOUSE"] = Field(..., alias="property-type")
    rooms_number: int = Field(..., alias="rooms-number")
    zip_code: int = Field(..., alias="zip-code")
    land_area: Optional[int]  = Field(None, alias="land-area")
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
    building_state: Optional[Literal["NEW", "GOOD", "TO RENOVATE", "JUST RENOVATED", "TO REBUILD"]]  = Field(None, alias="building-state")
    lift: int
    parkingcountindoor: int
    parkingcountoutdoor: int
    province: Literal['Antwerp', 'East Flanders','Flemish Brabant', 'Limburg','West Flanders',
                      'Walloon Brabant', 'Hainaut', 'Liège', 'Luxembourg', 'Namur', 'Brussels']
    epcscore: Literal['A++', 'A+', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

    class Config:
        allow_population_by_field_name = True

@app.post("/predict_WithBetterValidation")
async def predict_WithBetterValidation(propertyData: PropertyData):

  data_dict = propertyData.model_dump()

  df = pd.DataFrame([data_dict])

  df["price"] = 0
  df["subtype"] = "subtype"
  df["locality"] = "locality"

  # Drop columns according to preprocessing.py
  df.drop(columns=['garden_area', 'equipped_kitchen', 'full_address',
                    'furnished', 'open_fire', 'terrace_area','facades_number'], inplace=True, errors='ignore')
  
  # Fix column names
  df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
  # Rename columns according to preprocessing.py

  if 'building_state' not in df.columns: df['building_state'] = "GOOD"
  if 'terrace' not in df.columns: df['terrace'] = 0
  if 'swimming_pool' not in df.columns: df['swimming_pool'] = 0
  if 'garden' not in df.columns: df['garden'] = 0
  if 'land_area' not in df.columns: df['land_area'] = 0

  df.rename(columns={ 'rooms_number': 'bedroomcount',      
                              'area': 'habitablesurface',
                     'property_type': 'type',
                          'zip_code': 'postcode',
                         'land_area': 'landsurface',
                            'garden': 'hasgarden',
                     'swimming_pool': 'hasswimmingpool',
                           'terrace': 'hasterrace',
                    'building_state': 'buildingcondition',
                              'lift': 'haslift'
                        }, inplace=True)
  
  df_temp = df
  immo_Preprocessing = Immo_Preprocessing("data_cleaned_Nad.csv") # We don't need the csv, but because I don't want to modify preprocessing.py, I need to give it some file.
  immo_Preprocessing.df=df_temp # Here we replace df that was before populated from the csv to train the model, with our json input.

  immo_Preprocessing.fill_boolean_values()
  immo_Preprocessing.add_parking_col()
  immo_Preprocessing.add_region_column()
  #immo_Preprocessing.eliminate_outliers()
  #immo_Preprocessing.eliminate_postcode_small_number()
  immo_Preprocessing.drop_remaining_rows()
  immo_Preprocessing.oe_ohe_processing()
  immo_Preprocessing.drop_remaining_columns()
  immo_Preprocessing.drop_duplicates()
  immo_Preprocessing.latitude_longitude_columns('prepocessing//data//georef-belgium-postal-codes@public.csv')
  # Create missing region columns
  columns_to_check = ['region_Brussels', 'region_Flanders', 'region_Wallonia']
  for col in columns_to_check:
    if col not in immo_Preprocessing.df.columns:
       immo_Preprocessing.df[col] = 0

  #*** Caterina- did you normalized your df before doing modeling? If yes, we need to normalise our input then! But what are norm. coeff-s???

  price_pred=Predict_Nad.predict_price(immo_Preprocessing.df)

  print("Predicted price: ", price_pred)
  return(JSONResponse(status_code=200, content= {"price_pred" : price_pred}))


#################  Process input JSON file with less validation

@app.post("/predict")
async def predict(request: Request):

  json_data = await request.json()
  json_data["price"] = 0 # adds field price, it will be dropped in preprocessing.py, but I don't want to alter it (preprocessing.py)
  json_data["subtype"] = "subtype" # adds field subtype, it will be dropped in preprocessing.py, but I don't want to alter it (preprocessing.py)
  json_data["locality"] = "locality" # adds field locality, it will be dropped in preprocessing.py, but I don't want to alter it (preprocessing.py)
  
  #data = json.loads(json_data)
  df = pd.DataFrame([json_data])

  # Drop columns according to preprocessing.py
  df.drop(columns=['garden-area', 'equipped-kitchen', 'full-address',
                    'furnished', 'open-fire', 'terrace-area','facades-number'], inplace=True, errors='ignore')
  
  # Fix column names
  df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
  # Rename columns according to preprocessing.py

  if 'building-state' not in df.columns: df['building-state'] = "GOOD"
  if 'terrace' not in df.columns: df['terrace'] = 0
  if 'swimming-pool' not in df.columns: df['swimming-pool'] = 0
  if 'garden' not in df.columns: df['garden'] = 0
  if 'land-area' not in df.columns: df['land-area'] = 0

  df.rename(columns={ 'rooms-number': 'bedroomcount',      
                              'area': 'habitablesurface',
                     'property-type': 'type',
                          'zip-code': 'postcode',
                         'land-area': 'landsurface',
                            'garden': 'hasgarden',
                     'swimming-pool': 'hasswimmingpool',
                           'terrace': 'hasterrace',
                    'building-state': 'buildingcondition',
                              'lift': 'haslift'
                        }, inplace=True)
  
  df_temp = df
  immo_Preprocessing = Immo_Preprocessing("data_cleaned_Nad.csv") # We don't need the csv, but because I don't want to modify preprocessing.py, I need to give it some file.
  immo_Preprocessing.df=df_temp # Here we replace df that was before populated from the csv to train the model, with our json input.

  immo_Preprocessing.fill_boolean_values()
  immo_Preprocessing.add_parking_col()
  immo_Preprocessing.add_region_column()
  #immo_Preprocessing.eliminate_outliers()
  #immo_Preprocessing.eliminate_postcode_small_number()
  immo_Preprocessing.drop_remaining_rows()
  immo_Preprocessing.oe_ohe_processing()
  immo_Preprocessing.drop_remaining_columns()
  immo_Preprocessing.drop_duplicates()
  immo_Preprocessing.latitude_longitude_columns('prepocessing//data//georef-belgium-postal-codes@public.csv')
  # Create missing region columns
  columns_to_check = ['region_Brussels', 'region_Flanders', 'region_Wallonia']
  for col in columns_to_check:
    if col not in immo_Preprocessing.df.columns:
       immo_Preprocessing.df[col] = 0

  #*** Caterina- did you normalized your df before doing modeling? If yes, we need to normalise our input then! But what are norm. coeff-s???

  price_pred=Predict_Nad.predict_price(immo_Preprocessing.df)

  print("Predicted price: ", price_pred)
  return(JSONResponse(status_code=200, content= {"price_pred" : price_pred}))


