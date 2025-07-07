from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Optional, Literal
import pandas as pd
import os

from predict.predict_Nad import Predict_Nad
from prepocessing.preprocessing import Immo_Preprocessing #####!!!!! spelling error: preposessing

#app = FastAPI()

# Set port to the env variable PORT to make it easy to choose the port on the server
# If the Port env variable is not set, use port 8000
PORT = os.environ.get("PORT", 8000)
app = FastAPI(port=PORT)

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
    "property-type": "APARTMENT | HOUSE ",     # Removed | OTHERS - not in our model!   
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

#################  Process input JSON file

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
  
  print ("Ok now!!!!!!!!!!!")
  
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

  ############ Caterina- did you normalized your df before doing modeling? If yes, we need to normalise our input then! But what are norm. coeff-s???

  price_pred=Predict_Nad.predict_price(immo_Preprocessing.df)

  print("Predicted price: ", price_pred)
  return{"price_pred" : price_pred}


