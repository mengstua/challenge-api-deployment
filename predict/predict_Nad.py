import pickle
import pandas as pd

def predict_price(df):
    """Loads trained model, saves given dataframe (which was made from json POST request) in a csv,
      and predicts price for the given dataframe
    """
    with open("model/model.pkl", "rb") as f:
        unpickled_model = pickle.load(f)
        print("Model loaded successfully.")
        df=df[unpickled_model.feature_names_] # re-arrage input dataframe columns like in the model
        df.to_csv('prepocessing/data/json_cleaned.csv')
        result = unpickled_model.predict(df)
        return(result[0])

#predict_price()