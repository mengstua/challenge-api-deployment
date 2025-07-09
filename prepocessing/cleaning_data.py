import pandas as pd
from typing import Dict, Any

def preprocess(input_data: Dict[str, Any]) -> pd.DataFrame:
    """
    Preprocess the input data dict and return a cleaned dataframe suitable for the model.
    Raise ValueError if required fields are missing.
    """
    required_fields = ["area", "property-type", "rooms-number", "zip-code"]
    
    for field in required_fields:
        if field not in input_data or input_data[field] is None:
            raise ValueError(f"Missing required field: {field}")


    
    data = input_data.copy()
    
    # Fill NaNs for optional numeric fields with 0 or other default values
    optional_numeric_fields = [
        "land-area", "garden-area", "terrace-area", "facades-number"
    ]
    for field in optional_numeric_fields:
        if field not in data or data[field] is None:
            data[field] = 0
    
    # Fill NaNs for optional bool fields with False
    optional_bool_fields = [
        "garden", "equipped-kitchen", "swimming-pool", "furnished",
        "open-fire", "terrace"
    ]
    for field in optional_bool_fields:
        if field not in data or data[field] is None:
            data[field] = False
    
    # You can add encoding steps, etc.
    
    # Convert to DataFrame (single row)
    df = pd.DataFrame([data])
    
    # Example: rename columns if your model expects specific names
    # df = df.rename(columns={"property-type": "property_type"})
    
    return df
