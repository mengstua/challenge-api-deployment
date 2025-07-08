import pandas as pd
import json
import os
from typing import Dict, Any
import logging
from geopy.geocoders import Nominatim

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration files
current_dir = os.path.dirname(__file__)
zip_region_path = os.path.join(current_dir, '../data/zip_region_mapping.csv')
defaults_path = os.path.join(current_dir, '../data/default_values.json')

zip_region = pd.read_csv(zip_region_path)
with open(defaults_path) as f:
    defaults = json.load(f)

# Initialize geocoder
geolocator = Nominatim(user_agent="immoeliza_api")

def map_zip_to_region(zip_code: int) -> Dict[str, int]:
    """Map Belgian zip code to region flags"""
    try:
        region = zip_region[zip_region['zip_code'] == zip_code].iloc[0]
        return {
            'region_Brussels': int(region['Brussels']),
            'region_Flanders': int(region['Flanders']),
            'region_Wallonia': int(region['Wallonia'])
        }
    except IndexError:
        raise ValueError(f"Zip code {zip_code} not found in our database")

def geocode_address(address: str, zip_code: int):
    """Get coordinates from address or zip code"""
    try:
        if address:
            location = geolocator.geocode(f"{address}, Belgium")
        else:
            location = geolocator.geocode(f"{zip_code}, Belgium")
        
        if location:
            return location.latitude, location.longitude
        return defaults['latitude'], defaults['longitude']
    except Exception as e:
        logger.warning(f"Geocoding failed: {str(e)}")
        return defaults['latitude'], defaults['longitude']

def encode_property_type(prop_type: str) -> int:
    """Encode property type to numerical value"""
    prop_type = prop_type.upper()
    mapping = {
        'APARTMENT': 1,
        'HOUSE': 2,
        'OTHERS': 3
    }
    if prop_type not in mapping:
        raise ValueError(f"Invalid property type: {prop_type}")
    return mapping[prop_type]

def encode_building_state(state: str) -> int:
    """Encode building condition to numerical value"""
    if not state:
        return defaults['buildingcondition_encoded']
    
    state = state.upper()
    mapping = {
        'NEW': 1,
        'GOOD': 2,
        'JUST RENOVATED': 3,
        'TO RENOVATE': 4,
        'TO REBUILD': 5
    }
    if state not in mapping:
        raise ValueError(f"Invalid building state: {state}")
    return mapping[state]

def preprocess(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Main preprocessing function"""
    # Validate required fields
    required = ['area', 'property_type', 'rooms_number', 'zip_code']
    for field in required:
        if field not in input_data or input_data[field] is None:
            raise ValueError(f"Missing required field: {field}")
    
    # Process regions
    region_data = map_zip_to_region(input_data['zip_code'])
    
    # Geocode location
    latitude, longitude = geocode_address(
        input_data.get('full_address'),
        input_data['zip_code']
    )
    
    # Prepare feature dictionary
    features = {
        'bedroomcount': input_data['rooms_number'],
        'habitablesurface': input_data['area'],
        'haslift': defaults['haslift'],
        'hasgarden': input_data.get('garden', False),
        'hasswimmingpool': input_data.get('swimming_pool', False),
        'hasterrace': input_data.get('terrace', False),
        'hasparking': defaults['hasparking'],
        'epcscore_encoded': defaults['epcscore_encoded'],
        'buildingcondition_encoded': encode_building_state(input_data.get('building_state')),
        'type_encoded': encode_property_type(input_data['property_type']),
        'latitude': latitude,
        'longitude': longitude
    }
    
    # Add region flags
    features.update(region_data)
    
    return features

