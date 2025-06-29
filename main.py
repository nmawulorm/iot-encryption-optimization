from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# Values
public_key_location = "keys/public_key.pem"  # If this key does not exist, generate it before you use it.
model_location = "models/iot_sensitivity_model.joblib"

# Load the classification model
model = joblib.load(model_location)

# Load the RSA public key
with open(public_key_location, "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read())


# Define input model
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
    # Prepare features for prediction
    input_df = pd.DataFrame([{
        "sensor_name": data.sensor_name,
        "sensor_type": data.sensor_type,
        "device_type": data.device_type,
        "location": data.location
    }])

    # Predict sensitivity
    prediction = model.predict(input_df)[0]

    # Encrypt 'value' only if sensitive
    if prediction.lower() == "sensitive":
        encrypted_value = public_key.encrypt(
            data.value.encode("utf-8"),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # Encode encrypted value to Base64 for safe JSON transport
        encoded_value = base64.b64encode(encrypted_value).decode("utf-8")
    else:
        encoded_value = data.value

    return {
        "prediction": prediction,
        "value": encoded_value
    }
