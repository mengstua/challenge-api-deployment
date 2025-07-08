import pandas as pd
import numpy as np
import logging
from pathlib import Path
import json
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class Immo_Preprocessing:
    """Complete preprocessing class with all original methods + API support"""
    
    def __init__(self, file_path=None):
        self.df = pd.DataFrame() if file_path is None else pd.read_csv(file_path)
        self.defaults = self._load_defaults()
    
    def _load_defaults(self):
        """Load default values from JSON or use built-in"""
        try:
            with open(Path('data/default_values.json')) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Using built-in defaults")
            return {
                "haslift": 0,
                "hasparking": 0,
                "epcscore_encoded": 3,
                "buildingcondition_encoded": 2,
                "latitude": 50.8503,
                "longitude": 4.3517
            }

    # --- Your Original Methods (Keep Exactly As Is) ---
    def cleaning_columns(self):
        """Your existing column cleaning code"""
        self.df.columns = self.df.columns.str.strip().str.lower().str.replace(" ", "_")
        # ... [rest of your original implementation]

    # ... [ALL other original methods remain unchanged]

    # --- New API-Specific Method ---
    def preprocess_api_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process single API request input to model-ready features"""
        try:
            # Field mapping
            field_map = {
                'area': 'habitablesurface',
                'property_type': 'type',
                'rooms_number': 'bedroomcount',
                'zip_code': 'postcode',
                'garden': 'hasgarden',
                'swimming_pool': 'hasswimmingpool',
                'terrace': 'hasterrace',
                'building_state': 'buildingcondition',
                'facades_number': 'facedecount'
            }
            
            # Create input DataFrame
            self.df = pd.DataFrame({
                model_field: [input_data[api_field]]
                for api_field, model_field in field_map.items()
                if api_field in input_data
            })
            
            # Apply preprocessing pipeline
            self._run_preprocessing()
            
            # Return processed features
            return {
                'bedroomcount': float(self.df['bedroomcount'].iloc[0]),
                'habitablesurface': float(self.df['habitablesurface'].iloc[0]),
                'haslift': int(self.df.get('haslift', self.defaults['haslift']).iloc[0]),
                'hasgarden': int(self.df.get('hasgarden', 0).iloc[0]),
                'hasswimmingpool': int(self.df.get('hasswimmingpool', 0).iloc[0]),
                'hasterrace': int(self.df.get('hasterrace', 0).iloc[0]),
                'hasparking': int(self.df.get('hasparking', 0).iloc[0]),
                'epcscore_encoded': int(self.df.get('epcscore_encoded', self.defaults['epcscore_encoded']).iloc[0]),
                'buildingcondition_encoded': int(self.df.get('buildingcondition_encoded', self.defaults['buildingcondition_encoded']).iloc[0]),
                'latitude': float(self.df['latitude'].iloc[0]),
                'longitude': float(self.df['longitude'].iloc[0])
            }
            
        except Exception as e:
            logger.error(f"API preprocessing failed: {str(e)}")
            raise ValueError(f"Input processing error: {str(e)}")

    def _run_preprocessing(self):
        """Internal method to execute preprocessing steps"""
        # self.fill_boolean_values()
        self.add_parking_col()
        self.add_region_column()
        self.oe_ohe_processing()
        
        # Handle geocoding
        geo_path = Path('data/georef-belgium-postal-codes@public.csv')
        if geo_path.exists():
            self.latitude_longitude_columns(geo_path)
        else:
            self.df['latitude'] = self.defaults['latitude']
            self.df['longitude'] = self.defaults['longitude']

Immo_Preprocessing = Immo_Preprocessing()
