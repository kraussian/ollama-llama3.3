# Ollama-Llama 3.3

This is a `dockerfile` to build a Docker image based on Ollama's official image, but with Llama 3.3 model pre-installed and ready to serve.

The scripts in the image (`start.sh`, `runpod_wrapper.py`) were designed to be easily used with RunPod's [Serverless Endpoint](https://docs.runpod.io/serverless/endpoints/overview).

Also included in the repo are Python scripts to confirm that the Runpod Endpoint is working as expected:

* `basic_test.py`: Asks the LLM a simple question (`Why the sky is blue?`) and outputs the answer received
* `chat_test.py`: A simple but fully working text-based chatbot using the Runpod Endpoint

Note that to run the Python scripts, `python-dotenv` needs to be installed and a `.env` file created with the following details inside:

```bash
RUNPOD_API_KEY=your_api_key
ENDPOINT_ID=your_endpoint_id
```
