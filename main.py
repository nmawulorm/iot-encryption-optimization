from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# Load trained model
model = joblib.load("models/iot_sensitivity_model.joblib")

# Define expected input structure
class IoTInput(BaseModel):
    sensor_name: str
    sensor_type: str
    device_type: str
    location: str
    value: str

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "IoT Sensitivity Classifier is running"}

@app.post("/predict")
def predict_sensitivity(data: IoTInput):
    # Convert input into a DataFrame
    input_df = pd.DataFrame([data.model_dump()])
    # Predict sensitivity
    prediction = model.predict(input_df)[0]
    return {"prediction": prediction}
