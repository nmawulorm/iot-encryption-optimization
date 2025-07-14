from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
import os, base64, joblib, pandas as pd, json

# Paths
model_location = "models/iot_sensitivity_model.joblib"
aes_key_file = "keys/aes.key"

# Load model
model = joblib.load(model_location)

# Global storage
cloud_public_key = None
aes_key = None

app = FastAPI()

class IoTInput(BaseModel):
    sensor_name: str
    sensor_type: str
    device_type: str
    location: str
    value: str

@app.get("/")
def read_root():
    return {"message": "IoT Sensitivity Classifier is running"}

@app.post("/init")
async def init_key_exchange(request: Request):
    global cloud_public_key, aes_key

    if os.path.exists(aes_key_file):
        raise HTTPException(status_code=400, detail="AES key already initialized")

    # Receive cloud ECC public key (PEM format)
    body = await request.json()
    pem_key = body.get("public_key")
    if not pem_key:
        raise HTTPException(status_code=400, detail="Missing ECC public key")

    cloud_public_key = serialization.load_pem_public_key(pem_key.encode(), backend=default_backend())

    # Generate random AES key (256-bit)
    aes_key = os.urandom(32)
    with open(aes_key_file, "wb") as f:
        f.write(aes_key)

    # Encrypt AES key with ECC public key
    ephemeral_private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())
    shared_key = ephemeral_private_key.exchange(ec.ECDH(), cloud_public_key)

    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"key_exchange",
        backend=default_backend()
    ).derive(shared_key)

    # Encrypt AES key using derived_key with AES-CBC
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(derived_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding for AES block size (16 bytes)
    pad_len = 16 - (len(aes_key) % 16)
    padded_key = aes_key + bytes([pad_len] * pad_len)

    encrypted_aes_key = encryptor.update(padded_key) + encryptor.finalize()

    response = {
        "ephemeral_public_key": ephemeral_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode(),
        "iv": base64.b64encode(iv).decode(),
        "encrypted_aes_key": base64.b64encode(encrypted_aes_key).decode()
    }

    return response

@app.post("/predict")
def predict_sensitivity(data: IoTInput):
    global aes_key

    if aes_key is None:
        if os.path.exists(aes_key_file):
            with open(aes_key_file, "rb") as f:
                aes_key = f.read()
        else:
            raise HTTPException(status_code=400, detail="AES key not initialized")

    input_df = pd.DataFrame([{
        "sensor_name": data.sensor_name,
        "sensor_type": data.sensor_type,
        "device_type": data.device_type,
        "location": data.location
    }])

    prediction = model.predict(input_df)[0]

    if prediction.lower() == "sensitive":
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        pad_len = 16 - len(data.value.encode()) % 16
        padded_value = data.value.encode() + bytes([pad_len] * pad_len)
        ciphertext = encryptor.update(padded_value) + encryptor.finalize()

        print(prediction)

        return {
            "prediction": prediction,
            "iv": base64.b64encode(iv).decode(),
            "value": base64.b64encode(ciphertext).decode()
        }
    else:
        print(prediction)
        return {
            "prediction": prediction,
            "value": data.value
        }

@app.post("/predict_all")
def predict_all_encrypt(data: IoTInput):
    global aes_key

    if aes_key is None:
        if os.path.exists(aes_key_file):
            with open(aes_key_file, "rb") as f:
                aes_key = f.read()
        else:
            raise HTTPException(status_code=400, detail="AES key not initialized")

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    pad_len = 16 - len(data.value.encode()) % 16
    padded_value = data.value.encode() + bytes([pad_len] * pad_len)
    ciphertext = encryptor.update(padded_value) + encryptor.finalize()

    return {
        "prediction": "sensitive",  # Simulated
        "iv": base64.b64encode(iv).decode(),
        "value": base64.b64encode(ciphertext).decode()
    }
