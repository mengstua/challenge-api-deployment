from fastapi import FastAPI, Path, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

############ Get method for multipling by two 

@app.get("/multiply-by-two/{n}") # url: http://127.0.0.1:8000/multiply-by-two/5
def multiply_by_two(n: float | int = Path(..., description = "Enter number to be multiplied by 2")): 
    return n*2

# OR

@app.get("/multiply-by-2/{number}") # url: http://127.0.0.1:8000/multiply-by-2/5
#def multiply_by_two(request: Request, number: int): 
#    return number * 2  
# OR
def multiply_by_2(request: Request):
    number = int(request.path_params["number"])
    return number * 2

############ POST method to calculate net salary 

class SalaryData(BaseModel):
    salary: float
    bonus: float
    taxes: float

@app.post("/compute")
async def compute_salary(data: SalaryData):
    result = data.salary + data.bonus - data.taxes
    return {"result": result}
    
# Custom handler for 422 errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    formatted_errors = []
    
    def generate_custom_message(error, field):
        # Customize messages based on error type
        if error["type"] == "float_parsing":
            return "expected numbers, got string in {field}"
        elif error["type"] == "missing":
            return f"Required field missing: {field}."
        # Add more cases as needed
        return f"Check field -- {field} -- for errors."
    

    for error in errors:
        field = error["loc"][1]
        #message = error["msg"]
        custom_message = generate_custom_message(error, field)
        formatted_errors.append({
            #"field": field,
            #"message": message,
            #"error_type": error["type"],
            custom_message
        })
    
    return JSONResponse(
        status_code=422,
        content={"errors": f"{formatted_errors}" }
        )

 