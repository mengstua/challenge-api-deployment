from typing import Optional, Literal
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from predict.predict import predict_price
from preprocessing.preprocessing import pre_process_data

app = FastAPI()


class PropertyData(BaseModel):
    area: int
    property_type: Literal["APARTMENT", "HOUSE", "OTHERS"] = Field(
        ..., alias="property-type"
    )
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
        allow_population_by_field_name = True


@app.get("/")
async def root():
    """Route that return 'Alive!' if the server runs."""
    return {"Status": "Alive!"}


@app.get("/predict")
async def predict_info():
    return data_format_json


data_format_json = {
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
        "building-state (optional)": "NEW | GOOD | TO RENOVATE | JUST RENOVATED | TO REBUILD",
    }
}


@app.post("/predict")
async def predict(data: PropertyData):
    data_dict = data.model_dump(by_alias=True)
    try:
        pre_processed_data = pre_process_data(data_dict)
    except Exception as e:
        return JSONResponse(
            status_code=422,
            content={"error": f"Value error: {str(e)}"}
        )
    prediction = predict_price(pre_processed_data)
    return JSONResponse(
        status_code=200,
        content={
            "prediction": f"{int(prediction):,d}".replace(",", "."),
            "status_code": 200,
        })


# Custom handler for 422 errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []

    def generate_custom_message(error):
        # Customize messages based on error type
        if error["type"] == "float_parsing":
            return "expected numbers, got string in {field}"
        elif error["type"] == "missing":
            return f"Required field missing: {error['loc'] }."
        # Add more cases as needed
        return f"Check field -- {error['loc'] } -- for errors."

    for error in errors:
        custom_message = generate_custom_message(error)
        formatted_errors.append(
            {
                custom_message
            }
        )

    return JSONResponse(status_code=422, content={"errors": f"{formatted_errors}"})
