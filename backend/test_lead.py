import requests
import json
import time

URL = "http://127.0.0.1:8000/api/v1/analyze"

payload = {
  "first_name": "Sarah",
  "last_name": "Connor",
  "email": "sarah@skynet-resistance.org",
  "company_name": "Resistance LLC",
  "notes": "We need a secure system immediately. Budget is unlimited, I am the leader."
}

def test_api():
    print("Sending request...")
    try:
        response = requests.post(URL, json=payload)
        response.raise_for_status()
        data = response.json()
        print("Response received:")
        score = data['lead_score']['score']
        print(f"Lead Score: {score}")
        return True
    except Exception as e:
        print(f"API Request failed: {e}")
        return False

if __name__ == "__main__":
    if test_api():
        print("API test pass.")
    else:
        print("API test fail.")
