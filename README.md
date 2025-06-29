# IOT DATA CLASSIFICATION AND ENCRYPTION 

Below is a structured outline of the steps we will follow to build, train, and deploy a real-time classification model for IoT data on a local middleware (e.g., Raspberry Pi), using `joblib` for model serialization and `FastAPI` for serving.

---

## ✅ PROJECT OUTLINE: IoT Sensitivity Classifier

### **🔧 Phase 1: Model Development**

#### 1. **Prepare Data**

* Load the synthetic dataset (CSV file)
* Select features: `sensor_name`, `sensor_type`, `device_type`, `location`
* Define target: `sensitivity_label`

#### 2. **Preprocess Features**

* Apply **One-Hot Encoding** to categorical fields
* Use `ColumnTransformer` to integrate preprocessing into a pipeline

#### 3. **Train Classifier**

* Split data into training and testing sets
* Train a **Decision Tree Classifier** (lightweight, interpretable)
* Evaluate performance using classification report

#### 4. **Serialize Model**

* Save trained model pipeline using `joblib` for deployment

---

### **🚀 Phase 2: REST API Deployment (on Middleware)**

#### 5. **Create REST API with FastAPI**

* Define a `/predict` endpoint that accepts JSON with fields:

  ```json
  {
    "sensor_name": "...",
    "sensor_type": "...",
    "device_type": "...",
    "location": "..."
  }
  ```
* Load the serialized model and return prediction: `sensitive` or `non-sensitive`

#### 6. **Test the API Locally**

* Use `curl` or Postman to simulate IoT input
* Validate correct response and latency

---

### **📦 Phase 3: Deployment on Raspberry Pi or Middleware**

#### 7. **Transfer Files**

* Copy model `.joblib` and FastAPI app to the Raspberry Pi

#### 8. **Set Up Environment**

* Install Python, `uvicorn`, `FastAPI`, `scikit-learn`, and other dependencies

#### 9. **Run the API Server**

* Start the service (e.g., with `uvicorn`) on boot or via `systemd`

