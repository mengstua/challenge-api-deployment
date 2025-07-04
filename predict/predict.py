import pickle
import pandas as pd

def predict_price(df):
    with open("./model/model.pkl", "rb") as f:
        unpickled_model = pickle.load(f)
        print("Model loaded successfully.")
        df = pd.read_csv('data_cleaned.csv')
        X = df.drop(columns=['price'])
        first_row = X.iloc[0:1] 
        print("first row:",first_row)

        res = unpickled_model.predict(first_row)
        print(res)