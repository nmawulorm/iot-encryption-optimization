Here is a JSON example of a data point coming from a smart home IoT device, structured with the fields we discussed:

---

### **📦 Sample IoT Data (JSON Format)**

```json
{
  "device_id": "dev-8843921",
  "sensor_name": "front_door_camera",
  "sensor_type": "camera",
  "device_type": "video_sensor",
  "location": "entrance",
  "timestamp": "2025-06-24T16:10:00Z",
  "value": "motion_detected",
  "unit": "boolean",
  "status": "active",
  "sensitivity_label": "sensitive"
}
```

---

### ✅ Another Example (Non-sensitive)

```json
{
  "device_id": "dev-3928122",
  "sensor_name": "kitchen_temperature_sensor",
  "sensor_type": "temperature",
  "device_type": "environment_sensor",
  "location": "kitchen",
  "timestamp": "2025-06-24T16:11:00Z",
  "value": 24.7,
  "unit": "°C",
  "status": "active",
  "sensitivity_label": "non-sensitive"
}
```

---

These examples assume labeled data (`sensitivity_label`) is available for training. For real-time prediction, this label would not be present—instead, it would be **predicted** by the model.
