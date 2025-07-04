import pickle
import pandas as pd

def predict_price(df):
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