import pickle
import pandas as pd
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "./model/model.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)

def predict(df):
    with open("./model/model.pkl", "rb") as f:
        unpickled_model = pickle.load(f)
        print("Model loaded successfully.")
        first_row = df.iloc[0:1] 
        print("first row:",first_row)

        res = unpickled_model.predict(first_row)[0]
        # print first 2 decimals
        res = round(res, 2)
        print("---------PRED---------", res)
        return res