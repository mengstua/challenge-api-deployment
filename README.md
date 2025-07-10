# challenge-api-deployment

## Description

This project provides a production-ready API for real estate price prediction, built for ImmoEliza. The API wraps a machine learning regression model and exposes endpoints for web developers to integrate into their applications. The API is deployed using Docker and available both on [Render](https://challenge-api-deployment-m30c.onrender.com/) and as a [Streamlit app](https://challenge-api-deployment-hj2rduzqiwpbuehni9usz2.streamlit.app/).

---


## Installation

### Requirements

- Python 3.10+
- Docker (for containerized deployment)
- pip

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

4. **Run the Streamlit app locally:**
   ```sh
   streamlit run streamlit_app.py
   ```
   The Streamlit UI will be available at [http://localhost:8501](http://localhost:8501).

---

## Usage

### API Endpoints

| Route         | Method | Description                                  |
|---------------|--------|----------------------------------------------|
| `/`           | GET    | Health check. Returns `"Alive!"`             |
| `/predict`    | GET    | Returns expected JSON input format            |
| `/predict`    | POST   | Returns price prediction for input data       |

**Deployed API:**  
- Render: [https://challenge-api-deployment-m30c.onrender.com/](https://challenge-api-deployment-m30c.onrender.com/)
- Streamlit: [https://challenge-api-deployment-hj2rduzqiwpbuehni9usz2.streamlit.app/](https://challenge-api-deployment-hj2rduzqiwpbuehni9usz2.streamlit.app/)

### Input Format

POST `/predict` expects:

```json
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
```

**Required fields:**  
- `area`, `property-type`, `rooms-number`, `zip-code`

**Optional fields:**  
- `land-area`, `garden`, `garden-area`, `equipped-kitchen`, `full-address`, `swimming-pool`, `furnished`, `open-fire`, `terrace`, `terrace-area`, `facades-number`, `building-state`

### Output Format

On success:

```json
{
  "prediction": "int",
  "status_code": 200
}
```

### Error Handling

If input is invalid or required fields are missing, the API returns an error response with a 422 status code. 
If the input is a valid type but unexpected value (e.g., zip code not found), it returns a validation error with a custom error message.

---

## Deployment


### Render

The API is deployed at:  
[https://challenge-api-deployment-m30c.onrender.com/](https://challenge-api-deployment-m30c.onrender.com/)

### Streamlit

The Streamlit app is deployed at:  
[https://caterinamennito-challenge-api-deployment-streamlit-app-vqlqgu.streamlit.app/](https://caterinamennito-challenge-api-deployment-streamlit-app-vqlqgu.streamlit.app/)

---

## Contributors

- [Caterina Mennito](https://github.com/caterinamennito)
- [Mengstu Arefe](https://github.com/mengstua)
- [Nadiya Gorlova](https://github.com/nadiya0509)


## API Documentation

FastAPI auto-generates interactive documentation at `/docs` (Swagger UI) and `/redoc` (ReDoc) endpoints.

