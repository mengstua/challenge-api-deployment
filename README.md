# challenge-api-deployment

## Description

This project builds on the previous project -
Immo_Eliza_Regression, which trained several models (linear, logarythmic, Gradient Boost, and Random Forest, etc.)
to predict prices based on the immo data-set that we obtained after the immo-web scraping project.
For this project we use only the best model - catboost.
Our application is available both on Render (using API-s defined in app.py) or streamlit
(I did not deploy on streamlit, but see Caterina's implementation on the main branch).

## Installation

### Requirements

- Python 3.10+
- Docker (just Docker file, for containerized deployment on Render, Render will interpret it itself)
- pip

saved the best model - catboost, as /model/model.pkl - and we
use it to predict a property price when the user enters property parameters 

### Local Setup

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-org/challenge-api-deployment.git
   cd challenge-api-deployment
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the API locally:**
   ```sh
   uvicorn app:app --reload
   ```
   The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

4. **Test locally:**
    ```sh
    Use postman extension in the VSCode. Give it the endpoint, choose GET or POST for the request,
    for POST choose json and "raw" form.
    ```

## Algorithm of price prediction

When you go to the main endpoints/fastAPI methods

http://127.0.0.1:8000/predict_WithBetterValidation

https://challenge-api-deployment-nadiya.onrender.com/predict_WithBetterValidation

or

http://127.0.0.1:8000/predict

https://challenge-api-deployment-nadiya.onrender.com/predict

the code converts your json input into a dataframe (the first API above also performs validation of parameters),
manipulates columns to make them of the same type as required by prepocessing/preprocess.py (which is a non-modified
copy of Caterina's group's regression project), and launches predict/predict_Nad.py.
The latter code just unpickles the model (model/model.pkl), feeds our dataframe of one row (= one json request
corresponding to one property), rearranges columns to match the model, and uses the model to calculate the price.
The code then returns you the price in the json form, together with the request status: 200 if all is ok or another number if error.

## Error handling

Special attention was given to catch errors, because if there were an error in the json input (wrong paramete name, value, or required parameter absent), the user would only see Error 500: Internal server error, with no more information.
Using /predict API will log all the errors in myapp.log (which will not be available when you run the app on an
external server like Render!), while using /predict_WithBetterValidation will show directly which parameter was entered
incorrectly thanks to the implementation of the pydantic/BaseModel python package and the customised exception handlers
in the app.py
(as well as in preprocessing.py where check_required_columns_data(df) method is used to control values of some parameters).

## Usage

### API Endpoints

| Route         | Method | Description                                  |
|---------------|--------|----------------------------------------------|
| `/`           | GET    | Health check. Returns `"Alive!"` if the application is deployed correctly             |
| `/check_LoggingStatus`           | GET    | Health check. Writes "Hello, logging works!" in myapp.log if the application is deployed locally and log file is started correctly |
| `/predict`    | GET    | Returns expected JSON input format            |
| `/predict`    | POST   | Returns price prediction for input json request if no errors, otherwise returns "Internal Server Error" and prints stacktrace in the log file.      |
| `/predict_WithBetterValidation`    | POST   | Returns price prediction for input json request if no errors, otherwise it returns a customised message about the erroneous parameter. In case other errors occur, it returns  "Internal Server Error" and prints stacktrace in the log file.      |


