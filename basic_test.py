import requests
import json
import os
from   dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY")
ENDPOINT_ID    = os.getenv("ENDPOINT_ID")
if not RUNPOD_API_KEY:
    raise ValueError("API key not found! Ensure RUNPOD_API_KEY is set in the .env file.")
if not ENDPOINT_ID:
    raise ValueError("Endpoint ID not found! Ensure ENDPOINT_ID is set in the .env file.")

# Set options
DEBUG = True

# Define Runpod API Endpoint
url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"

# Define Runpod API Key
api_key = RUNPOD_API_KEY

# Form payload structure
payload = {
    "input": {
        "method_name": "generate",
        "input": {
            "prompt": "Why the sky is blue?"
        }
    }
}

# Headers for the request (including Authorization header)
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Send the POST request
response = requests.post(url, json=payload, headers=headers)
if DEBUG:
    print(f"Raw Response: {response.text}")

# Parse and display the response
if response.status_code == 200:
    try:
        data = response.json()
        # Extract the "response" from the nested "output" object
        assistant_response = data.get("output", {}).get("response", "No response found in output.")
        print("Assistant's Response:")
        print(assistant_response)
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
else:
    print(f"Request failed with status code {response.status_code}: {response.text}")
