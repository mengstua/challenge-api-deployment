import pickle
import pandas as pd
import catboost

def predict_price(df):
    with open("./model/model.pkl", "rb") as f:
        unpickled_model = pickle.load(f)
        print("Model loaded successfully.")
        first_row = df.iloc[0:1] 
        print("first row:",first_row)

        res = unpickled_model.predict(first_row)[0]
        return f"{int(res):,d}".replace(",", ".")