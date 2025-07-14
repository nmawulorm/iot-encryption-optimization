import time
import requests
import random

URL = "http://127.0.0.1:8000/predict"

# Test data pool
sensor_names = ["door_camera", "temperature_sensor", "light_bulb", "smart_plug"]
sensor_types = ["video", "temperature", "light", "power"]
device_types = ["camera", "sensor", "bulb", "plug"]
locations = ["kitchen", "living_room", "garage", "bedroom"]
value = "test_value_123"

# Prepare dataset
def generate_payload():
    return {
        "sensor_name": random.choice(sensor_names),
        "sensor_type": random.choice(sensor_types),
        "device_type": random.choice(device_types),
        "location": random.choice(locations),
        "value": value
    }

# Run test
def run_test(request_count: int):
    start = time.perf_counter()
    for _ in range(request_count):
        payload = generate_payload()
        r = requests.post(URL, json=payload)
        if r.status_code != 200:
            print("Request failed:", r.text)
    duration = time.perf_counter() - start
    return duration

if __name__ == "__main__":
    N = 100  # Number of test requests

    print(f"🔁 Sending {N} classification-based (selective encryption) requests...")
    duration = run_test(N)
    print(f"✅ Total time (selective encryption): {duration:.4f} seconds")
