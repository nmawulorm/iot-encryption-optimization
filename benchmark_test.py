import string
import time
import requests
import random

URL = "http://127.0.0.1:8000/predict"
URL_ALL = "http://127.0.0.1:8000/predict_all"

# Test data pool
sensor_names = ["humidity_sensor", "room_temp_sensor", "light_bulb", "smart_plug"]
sensor_types = ["environmental", "temperature", "light", "power"]
device_types = ["environmental_device", "temperature_device", "bulb", "plug"]
locations = ["Data Center", "Server Room", "garage", "bedroom"]
value = "test_value_123"


#
# # Test data pool
# sensor_names = ["door_camera", "temperature_sensor", "light_bulb", "smart_plug"]
# sensor_types = ["video", "temperature", "light", "power"]
# device_types = ["camera", "sensor", "bulb", "plug"]
# locations = ["kitchen", "living_room", "garage", "bedroom"]
# value = "test_value_123"

def generate_large_value(size_kb: int) -> str:
    """
    Generate a random ASCII string of specified size in kilobytes (KB).
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=size_kb * 1024))


# Prepare dataset
def generate_payload(value_kb=200000):  # e.g., 1000 KB = 1 MB
    return {
        "sensor_name": random.choice(sensor_names),
        "sensor_type": random.choice(sensor_types),
        "device_type": random.choice(device_types),
        "location": random.choice(locations),
        "value": generate_large_value(value_kb)
    }


# Run test
def run_test(request_count: int, url: str):
    start = time.perf_counter()
    total_sensitive = 0
    total_non_sensitive = 0

    for i in range(request_count):
        payload = generate_payload()
        r = requests.post(url, json=payload)

        if r.status_code != 200:
            print(f"Request {i+1} failed:", r.text)
            continue

        try:
            response_data = r.json()
        except Exception as e:
            print(f"Failed to parse response for request {i+1}: {e}")
            continue

        # Count based on presence of 'iv' field
        if isinstance(response_data, dict):
            if 'iv' in response_data:
                total_sensitive += 1
            else:
                total_non_sensitive += 1
        elif isinstance(response_data, list):
            for item in response_data:
                if isinstance(item, dict) and 'iv' in item:
                    total_sensitive += 1
                else:
                    total_non_sensitive += 1

    duration = time.perf_counter() - start
    print(f"🔐 Sensitive fields: {total_sensitive}")
    print(f"🔓 Non-sensitive fields: {total_non_sensitive}")
    return duration

if __name__ == "__main__":
    N = 4  # Number of test requests

    print(f"🔁 Sending {N} classification-based (selective encryption) requests...")
    duration = run_test(N, URL)
    print(f"✅ Total time (selective encryption): {duration:.4f} seconds\n-------------------\n\n")

    print(f"🔁 Sending {N} non-classification-based (unselective encryption) requests...")
    duration = run_test(N, URL_ALL)
    print(f"✅ Total time (unselective encryption): {duration:.4f} seconds")
