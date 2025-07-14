import string
import sys
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

# Store results
results = []

def generate_large_value(size_kb: int) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=size_kb * 1024))


# Fixed payloads
def get_sensitive_payload(value_kb:int):
    return {
        "sensor_name": "door_camera",  # Known to classify as sensitive
        "sensor_type": "video",
        "device_type": "camera",
        "location": "front_door",
        "value": generate_large_value(value_kb)
    }

def get_nonsensitive_payload(value_kb):
    return {
        "sensor_name": "door_sensor",  # Known to classify as non-sensitive
        "sensor_type": "access_control",
        "device_type": "access_control_device",
        "location": "Operating Room",
        "value": generate_large_value(value_kb)
    }


# Run test
def run_test(request_count: int, url: str, size:int):
    start = time.perf_counter()
    total_sensitive = 0
    total_non_sensitive = 0

    for i in range(request_count):
        # Alternate sensitive and non-sensitive data
        if i % 2 == 0:
            payload = get_sensitive_payload(size)
        else:
            payload = get_nonsensitive_payload(size)

        r = requests.post(url, json=payload)

        if r.status_code != 200:
            print(f"Request {i + 1} failed:", r.text)
            continue

        try:
            response_data = r.json()
        except Exception as e:
            print(f"Failed to parse response for request {i + 1}: {e}")
            continue

        if isinstance(response_data, dict):
            if 'iv' in response_data:
                total_sensitive += 1
            else:
                total_non_sensitive += 1

    duration = time.perf_counter() - start
    return duration, total_sensitive


def print_results_table(results):
    print("\n{:<10} {:<25} {:<25} {:<25}".format(
        "N", "Classified", "Unclassified", "Classified as sensitive"
    ))
    for row in results:
        print("{:<10} {:<25} {:<25} {:<25}".format(*row))


if __name__ == "__main__":
    size = 7000

    print(f"\n🔁 Testing with payloads (approx. {size/1000}MB each)")
    print("\n{:<10} {:<25} {:<25} {:<25}".format(
        "N", "Classified", "Unclassified", "Classified as sensitive"
    ))


    for N in range(10, 101, 10):

        # Selective classification + conditional encryption
        classified_time, num_sensitive = run_test(N, URL, size)

        # Unselective encryption
        unclassified_time, _ = run_test(N, URL_ALL, size)

        # Print result row
        print("{:<10} {:<25} {:<25} {:<25}".format(
            N,
            f"{classified_time:.4f}s",
            f"{unclassified_time:.4f}s",
            num_sensitive
        ))

