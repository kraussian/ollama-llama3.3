import runpod
from typing import Any, Literal, TypedDict
import requests
import sys

# Define input structures
class HandlerInput(TypedDict):
    method_name: Literal["generate"]
    input: Any

class HandlerJob(TypedDict):
    input: HandlerInput

# Define handler
def handler(job: HandlerJob):
    base_url = "http://0.0.0.0:15251"
    input_data = job["input"]

    # Ensure model and disable streaming in serverless mode
    input_data["input"]["stream"] = False
    model = sys.argv[1]
    input_data["input"]["model"] = model

    try:
        # Send request with timeout
        response = requests.post(
            url=f"{base_url}/api/{input_data['method_name']}/",
            headers={"Content-Type": "application/json"},
            json=input_data["input"],
            timeout=30,  # 30 seconds timeout
        )
        response.raise_for_status()
        response.encoding = "utf-8"
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to communicate with Ollama: {str(e)}"}
    except Exception as e:
        return {"error": f"Unhandled exception: {str(e)}"}

# Start RunPod serverless mode
if __name__ == "__main__":
    print(f"Starting RunPod serverless handler for model: {sys.argv[1]}")
    runpod.serverless.start({"handler": handler})
