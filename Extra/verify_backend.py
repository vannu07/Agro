import requests
import json

BASE_URL = "http://localhost:5000"

def test_crop_agent():
    print("Testing Crop Agent...")
    payload = {
        "nitrogen": 90,
        "phosphorous": 42,
        "potassium": 43,
        "temperature": 25,
        "humidity": 80,
        "ph": 6.5,
        "rainfall": 200
    }
    try:
        response = requests.post(f"{BASE_URL}/api/agent/crop", json=payload)
        print("Response:", json.dumps(response.json(), indent=2))
        return response.status_code == 200 and response.json().get("status") == "ok"
    except Exception as e:
        print("Error:", e)
        return False

def test_memory():
    print("Testing Memory API...")
    try:
        response = requests.get(f"{BASE_URL}/api/memory")
        print("Response:", json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print("Error:", e)
        return False

if __name__ == "__main__":
    if test_crop_agent():
        print("Crop Agent Test PASSED")
    else:
        print("Crop Agent Test FAILED")
    
    if test_memory():
        print("Memory API Test PASSED")
    else:
        print("Memory API Test FAILED")
