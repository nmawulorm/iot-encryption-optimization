from fastapi import FastAPI
import joblib
import pandas as pd

app = FastAPI()

model = joblib.load("fraud_model.pkl")
scaler = joblib.load("scaler.pkl")

@app.post("/predict")
def predict(data: dict):
    df = pd.DataFrame([data])
    df_scaled = scaler.transform(df)
    prediction = model.predict(df_scaled)
    return {"fraud": bool(prediction[0])}


# TODO Run the API ```uvicorn main:app --reload```