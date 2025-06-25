Excellent. Now that your model is trained and saved as `iot_sensitivity_model.joblib`, we can proceed to the next step:

---

## ✅ **Phase 2: Build a REST API using FastAPI**

The API will:

* Accept incoming JSON data (from IoT middleware or gateway)
* Extract the required fields (`sensor_name`, etc.)
* Pass them to the trained model
* Return a prediction: `"sensitive"` or `"non-sensitive"`

---

### 🛠️ Step-by-Step: FastAPI Server for Local Classification

#### **1. Install FastAPI and Uvicorn**

```bash
pip install fastapi uvicorn joblib scikit-learn
```

---

#### **2. Create the FastAPI App**

Create a file called `main.py` with the following content:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

# Load trained model
model = joblib.load("iot_sensitivity_model.joblib")

# Define expected input structure
class IoTInput(BaseModel):
    sensor_name: str
    sensor_type: str
    device_type: str
    location: str

# Initialize FastAPI app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "IoT Sensitivity Classifier is running"}

@app.post("/predict")
def predict_sensitivity(data: IoTInput):
    # Convert input into a DataFrame
    input_df = pd.DataFrame([data.dict()])
    # Predict sensitivity
    prediction = model.predict(input_df)[0]
    return {"prediction": prediction}
```

---

#### **3. Run the API Server**

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

You should see output indicating the server is running on:
📍 `http://localhost:8000`

---

#### **4. Test the Endpoint**

You can use Postman or `curl`:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sensor_name": "atm_camera", "sensor_type": "video", "device_type": "video_sensor", "location": "ATM"}'
```

✅ Response:

```json
{"prediction": "sensitive"}
```

---

### ✅ Ready for Raspberry Pi

Once confirmed working locally:

* Transfer `main.py`, `iot_sensitivity_model.joblib`, and requirements to the Pi.
* Set up Python, install dependencies, and run the service.

Would you like a deployment script or systemd service file for auto-starting it on boot?
