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

# Store results
results = []

def generate_large_value(size_kb: int) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=size_kb * 1024))


def generate_payload(value_kb=2000):  # 2 MB per payload
    return {
        "sensor_name": random.choice(sensor_names),
        "sensor_type": random.choice(sensor_types),
        "device_type": random.choice(device_types),
        "location": random.choice(locations),
        "value": generate_large_value(value_kb)
    }


def run_test(request_count: int, url: str):
    start = time.perf_counter()
    total_sensitive = 0
    total_non_sensitive = 0

    for i in range(request_count):
        payload = generate_payload()
        r = requests.post(url, json=payload)

        if r.status_code != 200:
            print(f"Request {i + 1} failed:", r.text)
            continue

        try:
            response_data = r.json()
        except Exception as e:
            print(f"Failed to parse response for request {i + 1}: {e}")
            continue

        # Count sensitive based on presence of IV
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
    return duration, total_sensitive


def print_results_table(results):
    print("\n{:<10} {:<25} {:<25} {:<25}".format(
        "N", "Classified", "Unclassified", "Classified as sensitive"
    ))
    for row in results:
        print("{:<10} {:<25} {:<25} {:<25}".format(*row))


if __name__ == "__main__":
    print(f"\n🔁 Testing with payloads (approx. 2MB each)")
    print("\n{:<10} {:<25} {:<25} {:<25}".format(
        "N", "Classified", "Unclassified", "Classified as sensitive"
    ))


    for N in range(10, 101, 10):

        # Selective classification + conditional encryption
        classified_time, num_sensitive = run_test(N, URL)

        # Unselective encryption
        unclassified_time, _ = run_test(N, URL_ALL)

        # Print result row
        print("{:<10} {:<25} {:<25} {:<25}".format(
            N,
            f"{classified_time:.4f}s",
            f"{unclassified_time:.4f}s",
            num_sensitive
        ))

