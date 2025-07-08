
import joblib
import numpy as np
from pathlib import Path
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class PricePredictor:
    def __init__(self):
        try:
            # Load your trained model
            model_path = Path(__file__).parent.parent / "model" / "model.pkl"
            self.model = joblib.load(model_path)
            logger.info("Model loaded successfully")
            
            # Define the exact feature order expected by the model
            self.feature_order = [
                'bedroomcount', 
                'habitablesurface', 
                'haslift', 
                'hasgarden',
                'hasswimmingpool', 
                'hasterrace', 
                'hasparking', 
                'epcscore_encoded',
                'buildingcondition_encoded',
                'latitude', 
                'longitude'
            ]
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def predict(self, features: Dict) -> float:
        """
        Make a price prediction based on processed features
        
        Args:
            features: Dictionary containing all required features
            
        Returns:
            Predicted price as float rounded to 2 decimals
            
        Raises:
            ValueError: If required features are missing
        """
        try:
            # Validate all required features are present
            missing_features = [f for f in self.feature_order if f not in features]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")
            
            # Prepare feature array in exact order expected by the model
            feature_array = np.array([[features[f] for f in self.feature_order]])
            
            # Make prediction
            prediction = self.model.predict(feature_array)[0]
            
            # Return rounded value
            return round(float(prediction), 2)
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise ValueError(f"Prediction error: {str(e)}")

# Singleton instance for the app to use
predictor = PricePredictor()