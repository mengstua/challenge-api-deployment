 predict/prediction.py
python
import joblib
import os
import logging
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the model
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, '../model/model.pkl')

try:
    model = joblib.load(model_path)
except Exception as e:
    logger.error(f"Failed to load model: {str(e)}")
    raise

def predict(features: Dict) -> float:
    """Make prediction using the loaded model"""
    try:
        # Convert features to correct order (if needed)
        expected_features = [
            'bedroomcount', 'habitablesurface', 'haslift', 'hasgarden',
            'hasswimmingpool', 'hasterrace', 'hasparking', 'epcscore_encoded',
            'buildingcondition_encoded', 'region_Brussels', 'region_Flanders',
            'region_Wallonia', 'type_encoded', 'latitude', 'longitude'
        ]
        
        # Prepare feature vector in correct order
        feature_vector = [features[feat] for feat in expected_features]
        
        # Make prediction
        prediction = model.predict([feature_vector])[0]
        return round(float(prediction), 2)
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise ValueError("Error during prediction")
